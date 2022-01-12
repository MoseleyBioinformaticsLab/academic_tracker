# -*- coding: utf-8 -*-
"""
This module has functions for string manipulation specific to building emails and reports.
"""

import datetime
from . import helper_functions
import re

def create_citation(publication):
    """Build a human readable string describing the publication.
    
    Args:
        publication (dict): dictionary of a publication from PubMed's API
        
    Returns:
        publication_str (str): human readable string with authors names, publication date, title, journal, DOI, and PubMed id
    """
    publication_str = ""

    publication_str += ", ".join([auth["firstname"] + " " + auth["lastname"] for auth in publication["authors"]]) + "."
    publication_str += " {}.".format(str(publication["publication_date"]["year"]))
    publication_str += " {}.".format(publication["title"])
    publication_str += " {}.".format(publication["journal"])
    publication_str += " DOI:{}".format(publication["doi"])
    publication_str += " PMID:{}".format(publication["pubmed_id"])
    publication_str += " PMCID:{}".format(publication["PMCID"])
    
    return publication_str



def create_citations_for_author(authors_pubs, publication_dict):
    """Create a publication citation with cited grants for each publication in authors_pubs.
    
    Args:
        authors_pubs (dict): A dict where the keys are publication IDs associated with the author and the values are a set of any grants cited for the publication.
        publication_dict (dict): A dict where the keys are publication IDs and the values are attributes of the publication such as the authors.
        
    Returns:
        (str): A string of the citations and cited grants for each publication.
    """
    
    return "\n\n\n".join([create_citation(publication_dict[pub_id]) + "\n\nCited Grants:\n" + 
                             "\n".join([grant_id for grant_id in authors_pubs[pub_id]] if authors_pubs[pub_id] else ["None"]) 
                             for pub_id in authors_pubs])


    
def add_indention_to_string(string_to_indent):
    """Adds a \t character to the begining of every line in string_to_indent
    Args:
        string_to_indent (str): string to add tabs to
    
    Returns:
        (str): string with tabs at the begining of each line
    """
    
    return "\n".join(["\t" + line for line in string_to_indent.split("\n")])



def create_pubs_by_author_dict(publication_dict):
    """Create a dictionary with authors as the keys and values as the pub_ids and grants
    
    Organizes the publication information in an author focused way so other operations are easier.
    
    Args:
        publication_dict (dict): keys and values match the publications JSON file.
        
    Returns:
        pubs_by_author_dict (dict): dictionary where the keys are authors and the values are a dictionary of pub_ids with thier associated grants.
    """
    
    pubs_by_author_dict = {}
    for pub_id, pub_attributes in publication_dict.items():
        for author_attributes in pub_attributes["authors"]:
            if "author_id" in author_attributes:
                author_id = author_attributes["author_id"]
                if author_id in pubs_by_author_dict:
                    pubs_by_author_dict[author_id][pub_id] = pub_attributes["grants"]
                else:
                    pubs_by_author_dict[author_id] = {pub_id : pub_attributes["grants"]}
                    
    return pubs_by_author_dict



def create_emails_dict_ref(template_string, publication_dict, matching_key_for_citation, is_citation_in_prev_pubs_list, reference_lines, tokenized_citations, project_attributes):
    """"""
    
    email_messages = {"creation_date" : str(datetime.datetime.now())[0:16]}

    pub_template = helper_functions.regex_group_return(helper_functions.regex_match_return(r"(?s).*<pub_loop>(.*)</pub_loop>.*", template_string), 0)
    pub_info = create_report_from_template_ref(pub_template, publication_dict, matching_key_for_citation, is_citation_in_prev_pubs_list, reference_lines, tokenized_citations)
    
    template_string = re.sub(r"(?s)<pub_loop>.*</pub_loop>", pub_info, template_string)
    
    email_messages["emails"] = [{"body":template_string,
                                 "subject":project_attributes["email_subject"],
                                 "from":project_attributes["from_email"],
                                 "to":",".join([email for email in project_attributes["to_email"]]),
                                 "cc":",".join([email for email in project_attributes["cc_email"]])}]
    
    return email_messages



def create_emails_dict_auth(authors_by_project_dict, publication_dict, config_dict):
    """Create emails for each author.
    
    For each author in pubs_by_author create an email with publication citations. 
    Information in authors_by_project_dict is used to get information about the author, and 
    publication_dict is used to get information about publications. 
    
    Args:
        authors_by_project_dict (dict): keys are project names from the config file and values are pulled from the authors JSON file.
        publication_dict (dict): keys and values match the publications JSON file.
        config_dict (dict):keys and values match the project tracking configuration JSON file.
        
    Returns:
        email_messages (dict): keys and values match the email JSON file.
    """
    
    # dict for email messages.
    email_messages = {"creation_date" : str(datetime.datetime.now())[0:16]}
    email_messages["emails"] = []
    
    pubs_by_author_dict = create_pubs_by_author_dict(publication_dict)
    
    for project, project_attributes in config_dict["project_descriptions"].items():
        ## If to_email is in project then send one email with all authors for the project, or all authors depending on if authors is in project.
        if "to_email" in project_attributes:
            email_messages["emails"].append({"body":build_email_body_auth(publication_dict, config_dict, authors_by_project_dict, project, project_attributes["email_template"]),
                                             "subject":project_attributes["email_subject"],
                                             "from":project_attributes["from_email"],
                                             "to":",".join([email for email in project_attributes["to_email"]]),
                                             "cc":",".join([email for email in project_attributes["cc_email"]])})
        ## If authors is in project send an email to each author in the project.
        elif "authors" in project_attributes:
            email_messages["emails"] = email_messages["emails"] + \
                                       [{"body":build_email_body_auth(publication_dict, config_dict, {project:{author:authors_by_project_dict[project][author]}}, project, project_attributes["email_template"], config_dict["Authors"][author]["first_name"], config_dict["Authors"][author]["last_name"]),
                                       "subject":replace_subject_magic_words(authors_by_project_dict[project][author]),
                                       "from":authors_by_project_dict[project][author]["from_email"],
                                       "to":authors_by_project_dict[project][author]["email"],
                                       "cc":",".join([email for email in authors_by_project_dict[project][author]["cc_email"]]),
                                       "author":author}
                                       for author in project_attributes["authors"] if author in pubs_by_author_dict]
        ## If neither authors nor to_email is in the project then send emails to all authors that have publications.
        else:
            email_messages["emails"] = email_messages["emails"] + \
                                       [{"body":build_email_body_auth(publication_dict, config_dict, {project:{author:authors_by_project_dict[project][author]}}, project, project_attributes["email_template"], config_dict["Authors"][author]["first_name"], config_dict["Authors"][author]["last_name"]),
                                       "subject":replace_subject_magic_words(authors_by_project_dict[project][author]),
                                       "from":authors_by_project_dict[project][author]["from_email"],
                                       "to":authors_by_project_dict[project][author]["email"],
                                       "cc":",".join([email for email in authors_by_project_dict[project][author]["cc_email"]]),
                                       "author":author}
                                       for author in pubs_by_author_dict]
    
    return email_messages



def build_email_body_auth(publication_dict, config_dict, authors_by_project_dict, project_name, template_string, author_first = "", author_last = ""):
    """"""
    
    project_authors = build_author_loop(publication_dict, config_dict, authors_by_project_dict, project_name, template_string)
    
    template_string = re.sub(r"(?s)<author_loop>.*</author_loop>", project_authors, template_string)
    if author_first:
        template_string = template_string.replace("<author_first>", author_first)
        template_string = template_string.replace("<author_last>", author_last)
    
    return template_string



def build_project_email_body(project_dict, publication_dict, pubs_by_author_dict):
    """Build the body of the email to send to the project lead.
    
    The email_template key for each project is expected to have <total_pubs> somewhere in 
    the string. This is replaced by the publications for each author and their cited grants.
    
    Args:
        project_dict (dict): dictionary where the keys are project names and the values are attributes for the projects such as the authors associated with the project.
        publication_dict (dict): dictionary with publication ids as the keys, schema matches the publications JSON file
        pubs_by_author_dict (dict): dictionary where the keys are authors and the values are a dictionary of pub_ids with thier associated grants.
    
    Returns:
        body (str): the body of the email to be sent
    """
    
    if "authors" in project_dict:
        pubs_string = "\n\n\n".join([author + ":\n" + create_citations_for_author(pubs_by_author_dict[author], publication_dict) for author in project_dict["authors"] if author in pubs_by_author_dict])
    else:
        pubs_string = "\n\n\n".join([author + ":\n" + create_citations_for_author(pubs_by_author_dict[author], publication_dict) for author in pubs_by_author_dict])
       
    body = project_dict["email_template"]
    body = body.replace("<total_pubs>", pubs_string)
    return body


def create_indented_project_report(project_dict, pubs_by_author_dict, publication_dict):
    """Create an indented project report for the project.
    
    If the project has authors then create a report of the publications found for only those authors.
    Otherwise create a report of the publications found for all authors.
    
    Args:
        project_dict (dict): dictionary where the keys are project names and the values are attributes for the projects such as the authors associated with the project.
        pubs_by_author_dict (dict): dictionary where the keys are authors and the values are a dictionary of pub_ids with thier associated grants.
        publication_dict (dict): dictionary with publication ids as the keys, schema matches the publications JSON file
    
    Returns:
        text_to_save (str): the indented project report
    """
    
    if "authors" in project_dict:
        text_to_save = add_indention_to_string("\n\n\n".join([author + ":\n" + 
                                                               add_indention_to_string(create_citations_for_author(pubs_by_author_dict[author], publication_dict)) 
                                                               for author in project_dict["authors"] if author in pubs_by_author_dict]))
    else:
        text_to_save = add_indention_to_string("\n\n\n".join([author + ":\n" + 
                                                               add_indention_to_string(create_citations_for_author(pubs_by_author_dict[author], publication_dict)) 
                                                               for author in pubs_by_author_dict]))
                                           
    return text_to_save




def create_email_dict_for_no_PMCID_pubs(publications_with_no_PMCID_list, config_file, to_email):
    """Create an email with the publications information in it.
    
    For each publication in publications_with_no_PMCID_list add it's information 
    to the body of an email. Pull the subject, from, and cc emails from the 
    config_dict, and to from to_email.
    
    Args:
        publications_with_no_PMCID_list (list): A list of dictionaries.
        [{"DOI":"publication DOI", "PMID": "publication PMID", "line":"short description of the publication", "Grants":"grants funding the publication"}]
        config_file (dict): dict with the same structure as the configuration JSON file
        
    Returns:
        email_messages (dict): keys and values match the email JSON file.
    """
    
    email_messages = {"creation_date" : str(datetime.datetime.now())[0:16]}
    
    pubs_string = "\n\n\n".join([dictionary["line"] + "\n\n" + 
                          "PMID: " + (dictionary["PMID"] if dictionary["PMID"] else "None") + "\n\n" + 
                          "Cited Grants:\n" + ("\n".join(dictionary["Grants"]) if dictionary["Grants"] else "None") for dictionary in publications_with_no_PMCID_list])
    
    body = config_file["email_template"]
    body = body.replace("<total_pubs>", pubs_string)
    
    email_messages["emails"] = [{"body":body,
                                 "subject":config_file["email_subject"],
                                 "from":config_file["from_email"],
                                 "to":to_email,
                                 "cc":",".join([email for email in config_file["cc_email"]])}]       
    
    return email_messages



def replace_body_magic_words(authors_pubs, authors_attributes, publication_dict):
    """Replace the magic words in email body with appropriate values.
    
    Args:
        authors_pubs (dict): A dict where the keys are publication IDs associated with the author and the values are a set of any grants cited for the publication.
        authors_attributes (dict): A dict where the keys are attributes associated with the author such as first and last name.
        publication_dict (dict): A dict where the keys are publication IDs and the values are attributes of the publication such as the authors.
        
    Returns:
        body (str): A string with the text for the body of the email to be sent to the author.
    """
    pubs_string = create_citations_for_author(authors_pubs, publication_dict)
    
    body = authors_attributes["email_template"]
    body = body.replace("<total_pubs>", pubs_string)
    body = body.replace("<author_first_name>", authors_attributes["first_name"])
    body = body.replace("<author_last_name>", authors_attributes["last_name"])
    
    return body




def replace_subject_magic_words(authors_attributes):
    """Replace the magic words in email subject with appropriate values.
    
    Args:
        authors_attributes (dict): A dict where the keys are attributes associated with the author such as first and last name.
        
    Returns:
        subject (str): A string with the text for the subject of the email to be sent to the author.
    """
    subject = authors_attributes["email_subject"]
    subject = subject.replace("<author_first>", authors_attributes["first_name"])
    subject = subject.replace("<author_last>", authors_attributes["last_name"])
    
    return subject



def convert_tokenized_authors_to_str(authors):
    """"""
    
    authors_string = ""
    for author in authors:
        if "first" in author:
            if author["first"]:
                authors_string += author["first"]
                if author["last"]:
                    authors_string += " " + author["last"] + ", "
                else:
                    authors_string += ", "
            elif author["last"]:
                authors_string += author["last"] + ", "
        else:
            if author["last"]:
                authors_string += author["last"]
                if author["initials"]:
                    authors_string += " " + author["initials"] + ", "
                else:
                    authors_string += ", "
            else:
                authors_string += author["initials"] + ", "
        
    authors_string = authors_string[:-2]
            
    return authors_string



def create_reference_search_diagnostic(publication_dict, matching_key_for_citation, is_citation_in_prev_pubs_list, reference_lines, tokenized_citations):
    """"""
    
    report_string = ""
    for count, citation in enumerate(tokenized_citations):
        if reference_lines:
            pretty_print = reference_lines[count].split("\n")
            pretty_print = " ".join([line.strip() for line in pretty_print])
            report_string += "Reference Line: " + pretty_print + "\n"
        
        report_string += "Tokenized Reference: \n\tAuthors: " + convert_tokenized_authors_to_str(citation["authors"]) + " \n\tTitle: " + citation["title"]
        if citation["PMID"]:
            report_string += " \n\tPMID: " + str(citation["PMID"])
        if citation["DOI"]:
            report_string += " \n\tDOI: " + citation["DOI"]
        report_string += "\n"
        
        if matching_key_for_citation[count]:
            doi = publication_dict[matching_key_for_citation[count]]["doi"]
            pmid = publication_dict[matching_key_for_citation[count]]["pubmed_id"]
            pmcid = publication_dict[matching_key_for_citation[count]]["PMCID"]
            if publication_dict[matching_key_for_citation[count]]["grants"]:
                grants = ", ".join(publication_dict[matching_key_for_citation[count]]["grants"])
        
                
        if not doi:
            doi = "Not Found"
        if not pmid:
            pmid = "Not Found"
        if not pmcid:
            pmcid = "Not Found"
        if not grants:
            grants = "None Found"
        
        report_string += "Queried Information: \n\tDOI: " + doi + \
                         " \n\tPMID: " + pmid + \
                         " \n\tPMCID: " + pmcid +\
                         " \n\tGrants: " + grants
        if is_citation_in_prev_pubs_list:
            report_string += " \n\tIs In Comparison File: " + str(is_citation_in_prev_pubs_list[count])
        
        report_string += "\n\n\n"
        
    return report_string
    


def create_report_from_template_ref(template_string, publication_dict, matching_key_for_citation, is_citation_in_prev_pubs_list, reference_lines, tokenized_citations):
    """"""
    
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
    
    publication_date_keywords_map = {"<publication_year>":["publication_date", "year"],
                                     "<publication_month>":["publication_date", "month"],
                                     "<publication_day>":["publication_date", "day"],}
    
    tokenized_keywords_map = {"<tok_title>":"title", 
                              "<tok_DOI>":"DOI", 
                              "<tok_PMID>":"PMID"}
    
    
    
    report_string = ""
    for pub_id, pub_values in publication_dict.items():
        template_string_copy = template_string
        
        for keyword, pub_key in simple_publication_keywords_map.items():
            template_string_copy = template_string_copy.replace(keyword, str(pub_values[pub_key]))
            
        authors = ",".join([str(author["firstname"]) + " " + str(author["lastname"]) for author in pub_values["authors"]])
        template_string_copy = template_string_copy.replace("<authors>", authors)
        
        if pub_values["grants"]:
            grants = ", ".join(pub_values["grants"])
        else:
            grants = "None"
        template_string_copy = template_string_copy.replace("<grants>", grants)
        
        for keyword, key_list in publication_date_keywords_map.items():
            template_string_copy = template_string_copy.replace(keyword, str(helper_functions.nested_get(pub_values, key_list)))
        
        tok_index = matching_key_for_citation.index(pub_id)
        for keyword, tok_key in tokenized_keywords_map.items():
            template_string_copy = template_string_copy.replace(keyword, str(tokenized_citations[tok_index][tok_key]))
            
        tok_authors = convert_tokenized_authors_to_str(tokenized_citations[tok_index]["authors"])
        template_string_copy = template_string_copy.replace("<tok_authors>", tok_authors)
        
        if reference_lines:
            pretty_print = reference_lines[tok_index].split("\n")
            pretty_print = " ".join([line.strip() for line in pretty_print])
            template_string_copy = template_string_copy.replace("<ref_line>", pretty_print)
        
        if is_citation_in_prev_pubs_list:
            template_string_copy = template_string_copy.replace("<is_in_comparison_file>", str(is_citation_in_prev_pubs_list[tok_index]))
        
        report_string += template_string_copy

    return report_string




def create_report_from_template_auth(template_string, publication_dict, config_dict, authors_by_project_dict):
    """"""
    
    report_string = ""
    for project_name in config_dict["project_descriptions"]:
        template_string_copy = template_string
        
        project_authors = build_author_loop(publication_dict, config_dict, authors_by_project_dict, project_name, template_string)
        
        template_string_copy = re.sub(r"(?s)<author_loop>.*</author_loop>", project_authors, template_string_copy)
        template_string_copy = template_string_copy.replace("<project_name>", project_name)
        
        report_string += template_string_copy
        
    return report_string




def build_author_loop(publication_dict, config_dict, authors_by_project_dict, project_name, template_string):
    """"""
    
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
    
    publication_date_keywords_map = {"<publication_year>":["publication_date", "year"],
                                     "<publication_month>":["publication_date", "month"],
                                     "<publication_day>":["publication_date", "day"],}
    
    authors_keywords_map = {"<author_first>":"first_name",
                            "<author_last>":"last_name",
                            "<author_name_search>":"pubmed_name_search",
                            "<author_email>":"email"}
    
    pubs_by_author_dict = create_pubs_by_author_dict(publication_dict)
    
    author_template = helper_functions.regex_group_return(helper_functions.regex_match_return(r"(?s).*<author_loop>(.*)</author_loop>.*", template_string), 0)
    pub_template = helper_functions.regex_group_return(helper_functions.regex_match_return(r"(?s).*<pub_loop>(.*)</pub_loop>.*", template_string), 0)
    
    project_authors = ""
    for author in authors_by_project_dict[project_name]:
        if not author in pubs_by_author_dict:
            continue
        author_template_copy = author_template
        
        authors_pubs = ""
        for pub in pubs_by_author_dict[author]:
            pub_template_copy = pub_template
            
            for keyword, pub_key in simple_publication_keywords_map.items():
                pub_template_copy = pub_template_copy.replace(keyword, str(publication_dict[pub][pub_key]))
                
            authors = ", ".join([str(author["firstname"]) + " " + str(author["lastname"]) for author in publication_dict[pub]["authors"]])
            pub_template_copy = pub_template_copy.replace("<authors>", authors)
            
            if publication_dict[pub]["grants"]:
                grants = ", ".join(publication_dict[pub]["grants"])
            else:
                grants = "None Found"
            pub_template_copy = pub_template_copy.replace("<grants>", grants)
            
            for keyword, key_list in publication_date_keywords_map.items():
                pub_template_copy = pub_template_copy.replace(keyword, str(helper_functions.nested_get(publication_dict[pub], key_list)))
                    
            authors_pubs += pub_template_copy
        
        author_template_copy = re.sub(r"(?s)<pub_loop>.*</pub_loop>", authors_pubs, author_template_copy)
        for keyword, auth_key in authors_keywords_map.items():
            author_template_copy = author_template_copy.replace(keyword, str(config_dict["Authors"][author][auth_key]))
            
        project_authors += author_template_copy
        
    return project_authors
    






