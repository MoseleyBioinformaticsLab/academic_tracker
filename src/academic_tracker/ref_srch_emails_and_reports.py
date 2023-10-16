# -*- coding: utf-8 -*-
"""
Reference Search Emails and Reports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions to create emails and reports for reference_search.
"""

import re
import copy
import os

import pandas

from . import helper_functions
from . import fileio
from . import emails_and_reports_helpers


DEFAULT_SUMMARY_TEMPLATE = "<pub_loop>Reference Line:\n\t<ref_line>\nTokenized Reference:\n\tAuthors: <tok_authors>\n\tTitle: <tok_title>\n\tPMID: <tok_PMID>\n\tDOI: <tok_DOI>\nQueried Information:\n\tDOI: <DOI>\n\tPMID: <PMID>\n\tPMCID: <PMCID>\n\tGrants: <grants>\n\n</pub_loop>"

simple_publication_keywords_map = emails_and_reports_helpers.simple_publication_keywords_map

pub_authors_keyword_map = emails_and_reports_helpers.pub_authors_keyword_map

references_keyword_map = emails_and_reports_helpers.references_keyword_map

publication_date_keywords_map = emails_and_reports_helpers.publication_date_keywords_map

tokenized_keywords_map = emails_and_reports_helpers.tokenized_keywords_map


def convert_tokenized_authors_to_str(authors):
    """Combine authors into a comma separated string.
    
    Try to do first_name last_name for each author, but if first name isn't there
    then last_name initials. ex. first_name1 last_name1, last_name2 initials2
    
    Args:
        authors (list): a list of dictionaries [{"last":last_name, "initials":initials}, {"last":last_name, "first":first_name}]
        
    Returns:
        authors_string (str): comma separated list of authors.
    """
    
    authors_string = ""
    for author in authors:
        if "first" in author:
            if author["first"]:
                authors_string += author["first"]
                authors_string += " " + author["last"] + ", " if author["last"] else ", "
            elif author["last"]:
                authors_string += author["last"] + ", "
        else:
            if author["last"]:
                authors_string += author["last"]
                authors_string += " " + author["initials"] + ", " if author["initials"] else ", "
            else:
                authors_string += author["initials"] + ", "
        
    authors_string = authors_string[:-2]
    
    if not authors_string:
        authors_string = str(None)
            
    return authors_string



    
def create_report_from_template(publication_dict, is_citation_in_prev_pubs_list, tokenized_citations, template_string = DEFAULT_SUMMARY_TEMPLATE):
    """Create project report based on template_string.
    
    Loop over each publication in publication_dict and build a report based on 
    the tags in the template_string. Details about reports are in the documentation.
    
    Args:
        publication_dict (dict): keys and values match the publications JSON file.
        is_citation_in_prev_pubs_list (list): list of bools that indicate whether or not the citation at the same index in tokenized_citations is in the prev_pubs
        tokenized_citations (list): list of dicts. Matches the JSON schema for tokenized citations.
        template_string (str): string with tags indicated what information to put in the report.
        
    Returns:
        report (str): text of the created report.
    """
    
    matching_key_for_citation = [citation["pub_dict_key"] for citation in tokenized_citations]
    
    pub_template = helper_functions.regex_group_return(helper_functions.regex_match_return(r"(?s).*<pub_loop>(.*)</pub_loop>.*", template_string), 0)
    pub_author_template = helper_functions.regex_group_return(helper_functions.regex_match_return(r"(?s).*<pub_author_loop>(.*)</pub_author_loop>.*", template_string), 0)
    reference_template = helper_functions.regex_group_return(helper_functions.regex_match_return(r"(?s).*<reference_loop>(.*)</reference_loop>.*", template_string), 0)

    
    report_string = ""
    for pub_id, pub_values in publication_dict.items():
        pub_template_copy = pub_template
        tok_index = matching_key_for_citation.index(pub_id)
        tokenized_citation = tokenized_citations[tok_index]
        is_citation_in_prev_pubs = is_citation_in_prev_pubs_list[tok_index] if is_citation_in_prev_pubs_list else None
        
        pub_template_copy = emails_and_reports_helpers._replace_pub_author_and_reference_loops(publication_dict, 
                                                                                               pub_id, 
                                                                                               pub_template_copy, 
                                                                                               pub_author_template, 
                                                                                               reference_template)
                
        pub_template_copy = emails_and_reports_helpers._replace_keywords({"1":pub_template_copy}, 
                                                                         publication_dict, {}, 
                                                                         pub=pub_id, 
                                                                         tokenized_citation=tokenized_citation, 
                                                                         is_citation_in_prev_pubs=is_citation_in_prev_pubs)["1"]
                
        report_string += pub_template_copy
        
    report = re.sub(r"(?s)<pub_loop>.*</pub_loop>", report_string, template_string)

    return report



def create_tabular_report(publication_dict, config_dict, is_citation_in_prev_pubs_list, tokenized_citations, save_dir_name):
    """Create a pandas DataFrame and save it as Excel or CSV.
    
    Args:
        publication_dict (dict): keys and values match the publications JSON file.
        config_dict (dict): keys and values match the project tracking configuration JSON file.
        is_citation_in_prev_pubs_list (list): list of bools that indicate whether or not the citation at the same index in tokenized_citations is in the prev_pubs
        tokenized_citations (list): list of dicts. Matches the JSON schema for tokenized citations.
        save_dir_name (str): directory to save the report in.
        
    Returns:
        report (str): Either the text of the report if csv or a relative filepath to where the Excel file is saved.
        filename (str): Filename of the report. Made have had an .xlsx added to the end.
    """
    
    row_template = copy.deepcopy(config_dict["summary_report"]["columns"])
    
    matching_key_for_citation = [citation["pub_dict_key"] for citation in tokenized_citations]
    
    separator = config_dict["summary_report"]["separator"] if "separator" in config_dict["summary_report"] else ","
    
    sort = config_dict["summary_report"]["sort"] if "sort" in config_dict["summary_report"] else []
    
    if "column_order" in config_dict["summary_report"]:
        column_order = config_dict["summary_report"]["column_order"]
    else:
        column_order = list(row_template.keys())
    
    file_format = config_dict["summary_report"]["file_format"] if "file_format" in config_dict["summary_report"] else "csv"
        
    if "filename" in config_dict["summary_report"]:
        filename = config_dict["summary_report"]["filename"]
    else:
        filename = "summary_report.csv" if file_format == "csv" else "summary_report.xlsx"
    
    
    row_string = "".join(row_template.values()) 
    
    has_pub_author_keywords = False
    if any([pub_author_keyword in row_string for pub_author_keyword in pub_authors_keyword_map.keys()]):
        has_pub_author_keywords = True
        
    
    has_reference_keywords = False
    if any([reference_keyword in row_string for reference_keyword in references_keyword_map.keys()]):
        has_reference_keywords = True
    
    
    rows = []
    for pub, pub_values in publication_dict.items():
        tok_index = matching_key_for_citation.index(pub)
        is_citation_in_prev_pubs = is_citation_in_prev_pubs_list[tok_index] if is_citation_in_prev_pubs_list else None
        
        if has_reference_keywords or has_pub_author_keywords:
            
            rows += emails_and_reports_helpers._build_pub_author_and_reference_rows(publication_dict, 
                                                                                    config_dict, 
                                                                                    has_pub_author_keywords, 
                                                                                    has_reference_keywords,
                                                                                    row_template, 
                                                                                    None, 
                                                                                    None, 
                                                                                    pub, 
                                                                                    tokenized_citations[tok_index], 
                                                                                    is_citation_in_prev_pubs)
            
        else:
            rows.append(emails_and_reports_helpers._replace_keywords(row_template, 
                                                                     publication_dict, 
                                                                     None,
                                                                     pub=pub, 
                                                                     tokenized_citation=tokenized_citations[tok_index], 
                                                                     is_citation_in_prev_pubs=is_citation_in_prev_pubs))
            
    report, filename = emails_and_reports_helpers._save_rows_to_file(rows, 
                                                                     filename, 
                                                                     sort, 
                                                                     column_order, 
                                                                     file_format, 
                                                                     separator, 
                                                                     save_dir_name)
            
    return report, filename




# def replace_keywords(template, publication_dict, pub, tokenized_citation, is_citation_in_prev_pubs, pub_author={}):
#     """Replace keywords in the values of the template dictionary.
    
#     Args:
#         template (dict): keys are column names and values are what the elements of the column should be.
#         publication_dict (dict): keys and values match the publications JSON file.
#         pub (str): the key to the pub in publication_dict.
#         tokenized_citation (dict): The tokenized citation from the reference for the publication.
#         is_citation_in_prev_pubs (bool or None): Whether this publication is in the previous publications or not. If None then it isn't applicable.
#         pub_author (dict): The author in pub.
        
#     Returns:
#         template_copy (dict): template with the keywords replaced in its values.
#     """
    
#     template_copy = copy.deepcopy(template)
    
#     for key in template_copy:
                
#         for keyword, pub_key in simple_publication_keywords_map.items():
#             template_copy[key] = template_copy[key].replace(keyword, str(publication_dict[pub][pub_key]))
            
#         ## build first and last author
#         first_author = str(publication_dict[pub]["authors"][0]["lastname"]) + ", " + str(publication_dict[pub]["authors"][0]["firstname"])
#         template_copy[key] = template_copy[key].replace("<first_author>", first_author)
        
#         last_author = str(publication_dict[pub]["authors"][-1]["lastname"]) + ", " + str(publication_dict[pub]["authors"][-1]["firstname"])
#         template_copy[key] = template_copy[key].replace("<last_author>", last_author)
        
#         authors = ", ".join([str(author["firstname"]) + " " + str(author["lastname"]) for author in publication_dict[pub]["authors"]])
#         template_copy[key] = template_copy[key].replace("<authors>", authors)
        
#         grants = ", ".join(publication_dict[pub]["grants"]) if publication_dict[pub]["grants"] else "None Found"
#         template_copy[key] = template_copy[key].replace("<grants>", grants)
        
#         for keyword, date_key in publication_date_keywords_map.items():
#             template_copy[key] = template_copy[key].replace(keyword, str(publication_dict[pub]["publication_date"][date_key]))
        
#         ## Pub authors keywords
#         if pub_author:
#             for keyword, pub_author_key in pub_authors_keyword_map.items():
#                 template_copy[key] = template_copy[key].replace(keyword, str(pub_author[pub_author_key]))
                
#         ## tokenized keywords
#         for keyword, tok_key in tokenized_keywords_map.items():
#             replacement = str(tokenized_citation[tok_key])
#             if not replacement:
#                 replacement = "None"
#             template_copy[key] = template_copy[key].replace(keyword, replacement)
            
#         tok_authors = convert_tokenized_authors_to_str(tokenized_citation["authors"])
#         template_copy[key] = template_copy[key].replace("<tok_authors>", tok_authors)
        
#         if tokenized_citation["reference_line"]:
#             pretty_print = tokenized_citation["reference_line"].split("\n")
#             pretty_print = " ".join([line.strip() for line in pretty_print])
#             template_copy[key] = template_copy[key].replace("<ref_line>", pretty_print)
#         else:
#             template_copy[key] = template_copy[key].replace("<ref_line>", "N/A")
        
#         if type(is_citation_in_prev_pubs) == bool:
#             template_copy[key] = template_copy[key].replace("<is_in_comparison_file>", str(is_citation_in_prev_pubs))
#         else:
#             template_copy[key] = template_copy[key].replace("<is_in_comparison_file>", "N/A")
            
#     return template_copy




def create_tokenization_report(tokenized_citations):
    """Create a report that details all the information about how a reference was tokenized.
    
    Intended as a troubleshooting report.
    
    Args:
        tokenized_citations (list): list of dicts. Matches the JSON schema for tokenized citations.
        
    Returns:
        report_string (str): report text built from tokenized_citations.
    """
    
    report_string = ""
    for count, citation in enumerate(tokenized_citations):
        if tokenized_citations[count]["reference_line"]:
            pretty_print = tokenized_citations[count]["reference_line"].split("\n")
            pretty_print = " ".join([line.strip() for line in pretty_print])
            report_string += "Reference Line: \n\t" + pretty_print + "\n"
        else:
            report_string += "Reference Line: \n\tN/A\n"
        
        report_string += "Tokenized Reference: \n\tAuthors: " + convert_tokenized_authors_to_str(citation["authors"])
        report_string += "\n\tTitle: " + citation["title"] if citation["title"] else "\n\tTitle: None"
        report_string += "\n\tPMID: " + str(citation["PMID"]) if citation["PMID"] else "\n\tPMID: None"
        report_string += "\n\tDOI: " + citation["DOI"] if citation["DOI"] else "\n\tDOI: None"
        report_string += "\n\n"
        
    return report_string



###############
## Unused
###############
    

# def create_reference_search_diagnostic(publication_dict, is_citation_in_prev_pubs_list, tokenized_citations):
#     """"""
    
#     report_string = ""
#     for count, citation in enumerate(tokenized_citations):
#         if tokenized_citations[count]["reference_line"]:
#             pretty_print = tokenized_citations[count]["reference_line"].split("\n")
#             pretty_print = " ".join([line.strip() for line in pretty_print])
#             report_string += "Reference Line: " + pretty_print + "\n"
        
#         report_string += "Tokenized Reference: \n\tAuthors: " + convert_tokenized_authors_to_str(citation["authors"]) + " \n\tTitle: " + citation["title"]
#         if citation["PMID"]:
#             report_string += " \n\tPMID: " + str(citation["PMID"])
#         if citation["DOI"]:
#             report_string += " \n\tDOI: " + citation["DOI"]
#         report_string += "\n"
        
#         if tokenized_citations[count]["pub_dict_key"]:
#             doi = publication_dict[tokenized_citations[count]["pub_dict_key"]]["doi"]
#             pmid = publication_dict[tokenized_citations[count]["pub_dict_key"]]["pubmed_id"]
#             pmcid = publication_dict[tokenized_citations[count]["pub_dict_key"]]["PMCID"]
#             if publication_dict[tokenized_citations[count]["pub_dict_key"]]["grants"]:
#                 grants = ", ".join(publication_dict[tokenized_citations[count]["pub_dict_key"]]["grants"])
        
                
#         if not doi:
#             doi = "Not Found"
#         if not pmid:
#             pmid = "Not Found"
#         if not pmcid:
#             pmcid = "Not Found"
#         if not grants:
#             grants = "None Found"
        
#         report_string += "Queried Information: \n\tDOI: " + doi + \
#                          " \n\tPMID: " + pmid + \
#                          " \n\tPMCID: " + pmcid +\
#                          " \n\tGrants: " + grants
#         if is_citation_in_prev_pubs_list:
#             report_string += " \n\tIs In Comparison File: " + str(is_citation_in_prev_pubs_list[count])
        
#         report_string += "\n\n\n"
        
#     return report_string


