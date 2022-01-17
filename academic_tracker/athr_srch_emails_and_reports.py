# -*- coding: utf-8 -*-
"""
Functions to create emails and reports for author_search.
"""

import datetime
import re

from . import helper_functions
from . import fileio


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



def create_project_reports_and_emails(authors_by_project_dict, publication_dict, config_dict, save_dir_name):
    """Create project reports and emails for each project.
    
    For each project in config_dict create a report and optional email.
    Reports are saved in save_dir_name as they are created.
    
    Args:
        authors_by_project_dict (dict): keys are project names from the config file and values are pulled from config_dict["Authors"].
        publication_dict (dict): keys and values match the publications JSON file.
        config_dict (dict): keys and values match the project tracking configuration JSON file.
        save_dir_name (str): directory to save the reports in.
        
    Returns:
        email_messages (dict): keys and values match the email JSON file.
    """
    
    # dict for email messages.
    email_messages = {"creation_date" : str(datetime.datetime.now())[0:16]}
    email_messages["emails"] = []
    
    pubs_by_author_dict = create_pubs_by_author_dict(publication_dict)
    
    for project, project_attributes in config_dict["project_descriptions"].items():
        
        if "project_report" in project_attributes:
            report_attributes = project_attributes["project_report"]
        else:
            continue
        
        if "from_email" in report_attributes:
            ## If to_email is in project then send one email with all authors for the project.
            if "to_email" in report_attributes:
                
                report = create_project_report(publication_dict, config_dict, authors_by_project_dict, project, report_attributes["template"])
                filename = project + "_project_report.txt"
                fileio.save_string_to_file(report, save_dir_name, filename)
                
                email_messages["emails"].append({"body":report_attributes["email_body"],
                                                 "subject":report_attributes["email_subject"],
                                                 "from":report_attributes["from_email"],
                                                 "to":",".join([email for email in report_attributes["to_email"]]),
                                                 "cc":",".join([email for email in report_attributes["cc_email"]]),
                                                 "attachment":report,
                                                 "attachment_filename": filename})
                
            ## If authors is in project send an email to each author in the project.
            elif "authors" in report_attributes:
                for author in project_attributes["authors"]:
                    
                    if not author in pubs_by_author_dict:
                        continue
                    
                    report = create_project_report(publication_dict, config_dict, {project:{author:authors_by_project_dict[project][author]}}, project, report_attributes["template"], config_dict["Authors"][author]["first_name"], config_dict["Authors"][author]["last_name"])
                    filename = project + "_" + author + "_project_report.txt"
                    fileio.save_string_to_file(report, save_dir_name, filename)
                    
                    email_messages["emails"].append({"body":authors_by_project_dict[project][author]["project_report"]["email_body"],
                                                     "subject":authors_by_project_dict[project][author]["project_report"]["email_subject"],
                                                     "from":authors_by_project_dict[project][author]["project_report"]["from_email"],
                                                     "to":authors_by_project_dict[project][author]["email"],
                                                     "cc":",".join([email for email in authors_by_project_dict[project][author]["project_report"]["cc_email"]]),
                                                     "attachment": report,
                                                     "attachment_filename": filename,
                                                     "author":author})
            ## If neither authors nor to_email is in the project then send emails to all authors that have publications.
            else:
                for author in pubs_by_author_dict:
                    report = create_project_report(publication_dict, config_dict, {project:{author:authors_by_project_dict[project][author]}}, project, report_attributes["template"], config_dict["Authors"][author]["first_name"], config_dict["Authors"][author]["last_name"])
                    filename = project + "_" + author + "_project_report.txt"
                    fileio.save_string_to_file(report, save_dir_name, filename)
                    
                    email_messages["emails"].append({"body":authors_by_project_dict[project][author]["project_report"]["email_body"],
                                                     "subject":authors_by_project_dict[project][author]["project_report"]["email_subject"],
                                                     "from":authors_by_project_dict[project][author]["project_report"]["from_email"],
                                                     "to":authors_by_project_dict[project][author]["email"],
                                                     "cc":",".join([email for email in authors_by_project_dict[project][author]["project_report"]["cc_email"]]),
                                                     "attachment": report,
                                                     "attachment_filename": filename,
                                                     "author":author})
        else:
            
            report = create_project_report(publication_dict, config_dict, authors_by_project_dict, project, report_attributes["template"])
            filename = project + "_project_report.txt"
            fileio.save_string_to_file(report, save_dir_name, filename)
    
    return email_messages



def create_project_report(publication_dict, config_dict, authors_by_project_dict, project_name, template_string, author_first = "", author_last = ""):
    """"""
    
    project_authors = build_author_loop(publication_dict, config_dict, authors_by_project_dict, project_name, template_string)
    
    template_string = re.sub(r"(?s)<author_loop>.*</author_loop>", project_authors, template_string)
    if author_first:
        template_string = template_string.replace("<author_first>", author_first)
        template_string = template_string.replace("<author_last>", author_last)
    
    return template_string




def create_summary_report(template_string, publication_dict, config_dict, authors_by_project_dict):
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





