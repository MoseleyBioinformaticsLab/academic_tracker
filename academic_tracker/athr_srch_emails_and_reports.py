# -*- coding: utf-8 -*-
"""
Functions to create emails and reports for author_search.
"""

import datetime
import re

from . import helper_functions


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



def create_emails_dict(authors_by_project_dict, publication_dict, config_dict):
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
        ## If to_email is in project then send one email with all authors for the project.
        if "to_email" in project_attributes:
            email_messages["emails"].append({"body":build_email_body(publication_dict, config_dict, authors_by_project_dict, project, project_attributes["email_template"]),
                                             "subject":project_attributes["email_subject"],
                                             "from":project_attributes["from_email"],
                                             "to":",".join([email for email in project_attributes["to_email"]]),
                                             "cc":",".join([email for email in project_attributes["cc_email"]])})
        ## If authors is in project send an email to each author in the project.
        elif "authors" in project_attributes:
            email_messages["emails"] = email_messages["emails"] + \
                                       [{"body":build_email_body(publication_dict, config_dict, {project:{author:authors_by_project_dict[project][author]}}, project, project_attributes["email_template"], config_dict["Authors"][author]["first_name"], config_dict["Authors"][author]["last_name"]),
                                       "subject":replace_subject_keywords(authors_by_project_dict[project][author]),
                                       "from":authors_by_project_dict[project][author]["from_email"],
                                       "to":authors_by_project_dict[project][author]["email"],
                                       "cc":",".join([email for email in authors_by_project_dict[project][author]["cc_email"]]),
                                       "author":author}
                                       for author in project_attributes["authors"] if author in pubs_by_author_dict]
        ## If neither authors nor to_email is in the project then send emails to all authors that have publications.
        else:
            email_messages["emails"] = email_messages["emails"] + \
                                       [{"body":build_email_body(publication_dict, config_dict, {project:{author:authors_by_project_dict[project][author]}}, project, project_attributes["email_template"], config_dict["Authors"][author]["first_name"], config_dict["Authors"][author]["last_name"]),
                                       "subject":replace_subject_keywords(authors_by_project_dict[project][author]),
                                       "from":authors_by_project_dict[project][author]["from_email"],
                                       "to":authors_by_project_dict[project][author]["email"],
                                       "cc":",".join([email for email in authors_by_project_dict[project][author]["cc_email"]]),
                                       "author":author}
                                       for author in pubs_by_author_dict]
    
    return email_messages



def build_email_body(publication_dict, config_dict, authors_by_project_dict, project_name, template_string, author_first = "", author_last = ""):
    """"""
    
    project_authors = build_author_loop(publication_dict, config_dict, authors_by_project_dict, project_name, template_string)
    
    template_string = re.sub(r"(?s)<author_loop>.*</author_loop>", project_authors, template_string)
    if author_first:
        template_string = template_string.replace("<author_first>", author_first)
        template_string = template_string.replace("<author_last>", author_last)
    
    return template_string



def replace_subject_keywords(authors_attributes):
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



def create_report_from_template(template_string, publication_dict, config_dict, authors_by_project_dict):
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





