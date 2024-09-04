# -*- coding: utf-8 -*-
"""
Emails and Reports Helpers
~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions to create emails and reports that are in common for both author_search and ref_search.
"""

import copy
import os
import re

import pandas

from . import ref_srch_emails_and_reports
from . import fileio


simple_publication_keywords_map = {"<abstract>":"abstract",
                                    "<conclusions>":"conclusions",
                                    "<copyrights>":"copyrights",
                                    "<DOI>":"doi",
                                    "<journal>":"journal",
                                    "<keywords>":"keywords",
                                    "<methods>":"methods",
                                    "<PMID>":"pubmed_id",
                                    "<results>":"results",
                                    "<title>":"title",
                                    "<PMCID>":"PMCID",}

pub_authors_keyword_map = {"<pub_author_first>":"firstname",
                           "<pub_author_last>":"lastname",
                           "<pub_author_initials>":"initials",
                           "<pub_author_collective>": "collectivename",
                           "<pub_author_affiliations>":"affiliation",
                           "<pub_author_ORCID>":"ORCID",
                           "<pub_author_id>":"author_id"}

references_keyword_map = {"<reference_citation>":"citation",
                          "<reference_title>":"title",
                          "<reference_PMID>":"pubmed_id",
                          "<reference_PMCID>":"PMCID",
                          "<reference_DOI>":"doi"}

publication_date_keywords_map = {"<publication_year>":"year",
                                 "<publication_month>":"month",
                                 "<publication_day>":"day"}

authors_keywords_map = {"<author_first>":"first_name",
                        "<author_last>":"last_name",
                        "<author_collective>": "collective_name",
                        "<author_name_search>":"pubmed_name_search",
                        "<author_email>":"email"}

pub_keywords = list(simple_publication_keywords_map.keys()) + \
               list(publication_date_keywords_map.keys()) + \
               ["<first_author>", "<last_author>", "<authors>", "<grants>", "<queried_sources>"]

## Ref search only.
tokenized_keywords_map = {"<tok_title>":"title", 
                          "<tok_DOI>":"DOI", 
                          "<tok_PMID>":"PMID"}



def _replace_keywords(template, publication_dict, config_dict, 
                     project_name="", author="", pub="", 
                     pub_author=None, reference=None, 
                     tokenized_citation=None, is_citation_in_prev_pubs=None):
    """Replace keywords in the values of the template dictionary.
    
    This is a convenience function to replace keywords as needed in strings. It is 
    setup so template is a dictionary for creating tabular reports from DataFrames. 
    So dict to DataFrame to csv or xlsx. To replace in a single string simply wrap 
    that single string in a dictionary with a single key and then pull it back out 
    of that dictionary from that key.
    
    This was merged to handle both reference search and author search. Previously there 
    were 2 replace_keywords functions, one for each search type.
    
    Args:
        template (dict): keys are column names and values are what the elements of the column should be.
        publication_dict (dict): keys and values match the publications JSON file.
        config_dict (dict): keys and values match the project tracking configuration JSON file.
        project_name (str): the name of the project to replace.
        author (str): the key to the author in config_dict["Authors"].
        pub (str): the key to the pub in publication_dict.
        pub_author (dict|None): an author in pub. None means no author.
        reference (dict|None): a reference for pub. None means no reference.
        tokenized_citation (dict): a tokenized citation from the reference for the publication.
        is_citation_in_prev_pubs (bool or None): whether this publication is in the previous publications or not. If None then it isn't applicable.
        
    Returns:
        template_copy (dict): template with the keywords replaced in its values.
    """
    
    template_copy = copy.deepcopy(template)
    
    for key in template_copy:
        
        ## Project keywords
        if project_name:
            template_copy[key] = template_copy[key].replace("<project_name>", project_name)
        
        ## Authors keywords
        if author:
            for keyword, auth_key in authors_keywords_map.items():
                template_copy[key] = template_copy[key].replace(keyword, str(config_dict["Authors"][author][auth_key]) if auth_key in config_dict["Authors"][author] else "None")
        
        ## Publication keywords
        if pub:
            for keyword, pub_key in simple_publication_keywords_map.items():
                template_copy[key] = template_copy[key].replace(keyword, str(publication_dict[pub][pub_key]))
                
            ## build first and last author
            if publication_dict[pub]["authors"]:
                first_author_attributes = publication_dict[pub]["authors"][0]
                if "collectivename" in first_author_attributes:
                    first_author = first_author_attributes["collectivename"]
                else:
                    first_author = str(first_author_attributes["lastname"]) + ", " + str(first_author_attributes["firstname"])
                
                last_author_attributes = publication_dict[pub]["authors"][-1]
                if "collectivename" in last_author_attributes:
                    last_author = last_author_attributes["collectivename"]
                else:
                    last_author = str(last_author_attributes["lastname"]) + ", " + str(last_author_attributes["firstname"])
                
                # first_author = str(publication_dict[pub]["authors"][0]["lastname"]) + ", " + str(publication_dict[pub]["authors"][0]["firstname"])
                template_copy[key] = template_copy[key].replace("<first_author>", first_author)
                
                # last_author = str(publication_dict[pub]["authors"][-1]["lastname"]) + ", " + str(publication_dict[pub]["authors"][-1]["firstname"])
                template_copy[key] = template_copy[key].replace("<last_author>", last_author)
                
                authors = []
                for author_attributes in publication_dict[pub]["authors"]:
                    if "collectivename" in author_attributes:
                        authors.append(author_attributes["collectivename"])
                    else:
                        authors.append(str(author_attributes["firstname"]) + " " + str(author_attributes["lastname"]))
                authors = ", ".join(authors)
            
                # authors = ", ".join([str(author["firstname"]) + " " + str(author["lastname"]) for author in publication_dict[pub]["authors"]])
                template_copy[key] = template_copy[key].replace("<authors>", authors)
            else:
                first_author = "No Authors"
                last_author = "No Authors"
                authors = "No Authors"
            
            grants = ", ".join(publication_dict[pub]["grants"]) if publication_dict[pub]["grants"] else "None Found"
            template_copy[key] = template_copy[key].replace("<grants>", grants)
            
            queried_sources = ", ".join(publication_dict[pub]["queried_sources"])
            template_copy[key] = template_copy[key].replace("<queried_sources>", queried_sources)
            
            for keyword, date_key in publication_date_keywords_map.items():
                template_copy[key] = template_copy[key].replace(keyword, str(publication_dict[pub]["publication_date"][date_key]))
        
        ## Pub authors keywords
        if pub_author:
            for keyword, pub_author_key in pub_authors_keyword_map.items():
                template_copy[key] = template_copy[key].replace(keyword, str(pub_author[pub_author_key]) if pub_author_key in pub_author else "None")
        
        ## references keywords
        if reference:
            for keyword, reference_key in references_keyword_map.items():
                template_copy[key] = template_copy[key].replace(keyword, str(reference[reference_key]))
        
        ## tokenized keywords
        if tokenized_citation:
            for keyword, tok_key in tokenized_keywords_map.items():
                replacement = str(tokenized_citation[tok_key])
                if not replacement:
                    replacement = "None"
                template_copy[key] = template_copy[key].replace(keyword, replacement)
                
            tok_authors = ref_srch_emails_and_reports.convert_tokenized_authors_to_str(tokenized_citation["authors"])
            template_copy[key] = template_copy[key].replace("<tok_authors>", tok_authors)
            
            if tokenized_citation["reference_line"]:
                pretty_print = tokenized_citation["reference_line"].split("\n")
                pretty_print = " ".join([line.strip() for line in pretty_print])
                template_copy[key] = template_copy[key].replace("<ref_line>", pretty_print)
            else:
                template_copy[key] = template_copy[key].replace("<ref_line>", "N/A")
            
            if type(is_citation_in_prev_pubs) == bool:
                template_copy[key] = template_copy[key].replace("<is_in_comparison_file>", str(is_citation_in_prev_pubs))
            else:
                template_copy[key] = template_copy[key].replace("<is_in_comparison_file>", "N/A")
            
    return template_copy



def _replace_pub_author_and_reference_loops(publication_dict, pub, string_to_modify, pub_author_template, reference_template):
    """Replace the pub_author and reference loops in string_to_modify with appropriate pub data.
    
    Args:
        publication_dict (dict): keys and values match the publications JSON file.
        pub (str): the key to the pub in publication_dict.
        string_to_modify (str): the string to place the pub_author and reference information into.
        pub_author_template (str): string that serves as a template for how to build the information about each pub_author.
        reference_template (str): string that serves as a template for how to build the information about each reference.
    
    Returns:
        string_to_modify (str): the input string_to_modify with pub_author and reference loops replaced.
    """
    
    pub_authors = ""
    for pub_author in publication_dict[pub]["authors"]:
        pub_author_template_copy = _replace_keywords({"1":pub_author_template}, publication_dict, {}, pub_author=pub_author)["1"]
        pub_authors += pub_author_template_copy
        
    string_to_modify = re.sub(r"(?s)<pub_author_loop>.*</pub_author_loop>", pub_authors, string_to_modify)
    
    references = ""
    for reference in publication_dict[pub]["references"]:
        reference_template_copy = _replace_keywords({"1":reference_template}, publication_dict, {}, reference=reference)["1"]
        references += reference_template_copy
    
    if not references:
        references = "None"
    string_to_modify = re.sub(r"(?s)<reference_loop>.*</reference_loop>", references, string_to_modify)
    
    return string_to_modify



def _save_rows_to_file(rows, filename, sort, column_order, file_format, separator, save_dir_name):
    """Turn a list of dicts into a DataFrame and save it to file.
    
    Args:
        rows (list[dict]): list of dictionaries to save.
        filename (str): filename to save the DataFrame as, '.csv' or '.xlsx' will be added as needed.
        sort (list[str]): list of column names to sort the DataFrame by, passes into DataFrame.sort_values().
        column_order (list[str]): list of column names to reorder the DataFrame columns.
        file_format (str): either 'csv' or 'xlsx' to save in CSV or Excel format, respectively.
        separator (str): the separator to use if file_format is 'csv'.
        save_dir_name (str): the directory name to save the file in.
    
    Returns:
        report (str): if file_format is 'csv', then the DataFrame in CSV form, else the path to the Excel file.
        filename (str): the filename the DataFrame was ultimately saved under.
    """
    
    report = ""            
    if rows:
        df = pandas.DataFrame(rows)
        if sort:
            df = df.sort_values(by=sort)
        df = df.drop_duplicates()
        df = df[column_order]
        
        if file_format == "csv":
            report = df.to_csv(index=False, sep=separator, lineterminator="\n")
            fileio.save_string_to_file(save_dir_name, filename, report)
        else:
            ## If the file extension isn't .xlsx then there will be an error, so force it.
            extension = os.path.splitext(filename)[1][1:].lower()
            if not extension == "xlsx":
                filename += ".xlsx"
            
            report = os.path.join(save_dir_name, filename)
            df.to_excel(report, index=False)
    
    return report, filename



def _build_pub_author_and_reference_rows(publication_dict, config_dict, 
                                         has_pub_author_keywords, has_reference_keywords,
                                         row_template, 
                                         project_name="", author="", pub="", 
                                         tokenized_citation=None, is_citation_in_prev_pubs=None):
    """Build rows for each pub_author and reference.
    
    Args:
        publication_dict (dict): keys and values match the publications JSON file.
        config_dict (dict): keys and values match the project tracking configuration JSON file.
        has_pub_author_keywords (bool): if True, then row_template has keywords to replace that are attributes to publication authors.
        has_reference_keywords (bool): if True, then row_template has keywords to replace that are attributes to publication references.
        row_template (dict): keys are column names and values are what the elements of the column should be.
        project_name (str): the name of the project to replace.
        author (str): the key to the author in config_dict["Authors"].
        pub (str): the key to the pub in publication_dict.
        tokenized_citation (dict|None): a tokenized citation from the reference for the publication.
        is_citation_in_prev_pubs (bool|None): whether this publication is in the previous publications or not. If None then it isn't applicable.
    
    Returns:
        rows (list): list of dictionaries meant to eventually be turned into a pandas DataFrame.
    """
    
    rows = []
    ## If references or authors is an empty list then you get unexpected behavior where pubs just won't show up, 
    ## so look for it before hand and just give it a null dictionary if it is empty.
    if not (references := publication_dict[pub]["references"]):
        references = [{
                        "PMCID": None,
                        "citation": None,
                        "doi": None,
                        "pubmed_id": None,
                        "title": None
                      }]
    ## There should always be at least 1 author since this is specific to author search, but the code is here for completeness.
    if not (pub_authors := publication_dict[pub]["authors"]):
        pub_authors = [{
                        "ORCID": None,
                        "affiliation": None,
                        "author_id": None,
                        "firstname": None,
                        "initials": None,
                        "lastname": None
                      }]
    
    if has_pub_author_keywords and has_reference_keywords:
        for pub_author in pub_authors:
            for reference in references:
                rows.append(_replace_keywords(row_template, 
                                              publication_dict, 
                                              config_dict, 
                                              project_name, 
                                              author,
                                              pub, 
                                              pub_author, 
                                              reference,
                                              tokenized_citation,
                                              is_citation_in_prev_pubs))
    
    elif has_pub_author_keywords:
        for pub_author in pub_authors:
            rows.append(_replace_keywords(row_template, 
                                          publication_dict, 
                                          config_dict, 
                                          project_name, 
                                          author, 
                                          pub, 
                                          pub_author,
                                          None,
                                          tokenized_citation,
                                          is_citation_in_prev_pubs))
    
    elif has_reference_keywords:
        for reference in references:
            rows.append(_replace_keywords(row_template, 
                                          publication_dict, 
                                          config_dict, 
                                          project_name, 
                                          author, 
                                          pub, 
                                          None, 
                                          reference,
                                          tokenized_citation,
                                          is_citation_in_prev_pubs))
            
    else:
        rows.append(_replace_keywords(row_template, 
                                      publication_dict, 
                                      config_dict, 
                                      project_name, 
                                      author, 
                                      pub,
                                      None,
                                      None,
                                      tokenized_citation,
                                      is_citation_in_prev_pubs))
    
    return rows
