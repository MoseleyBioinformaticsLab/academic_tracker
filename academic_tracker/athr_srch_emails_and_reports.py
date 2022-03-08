# -*- coding: utf-8 -*-
"""
Author Search Emails and Reports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions to create emails and reports for author_search.
"""

import datetime
import re
import os
import copy

import pandas

from . import helper_functions
from . import fileio

DEFAULT_SUMMARY_TEMPLATE = "<project_loop><project_name>\n<author_loop>\t<author_first> <author_last>:<pub_loop>\n\t\tTitle: <title> \n\t\tAuthors: <authors> \n\t\tJournal: <journal> \n\t\tDOI: <DOI> \n\t\tPMID: <PMID> \n\t\tPMCID: <PMCID> \n\t\tGrants: <grants>\n</pub_loop>\n</author_loop></project_loop>"
DEFAULT_PROJECT_TEMPLATE = "<author_loop><author_first> <author_last>:<pub_loop>\n\tTitle: <title> \n\tAuthors: <authors> \n\tJournal: <journal> \n\tDOI: <DOI> \n\tPMID: <PMID> \n\tPMCID: <PMCID> \n\tGrants: <grants>\n</pub_loop>\n</author_loop>"
DEFAULT_AUTHOR_TEMPLATE = "<author_loop><author_first> <author_last>:<pub_loop>\n\tTitle: <title> \n\tAuthors: <authors> \n\tJournal: <journal> \n\tDOI: <DOI> \n\tPMID: <PMID> \n\tPMCID: <PMCID> \n\tGrants: <grants>\n</pub_loop>\n</author_loop>"


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
        
        ## If to_email is in project then send one email with all authors for the project.
        if "to_email" in report_attributes or not "from_email" in report_attributes:
            
            if "columns" in report_attributes:
                if "file_format" in report_attributes:
                    file_format = report_attributes["file_format"]
                else:
                    file_format = "csv"
                    
                if "filename" in report_attributes:
                    filename = report_attributes["filename"]
                else:
                    if file_format == "csv":
                        filename = project + "_project_report.csv"
                    else:
                        filename = project + "_project_report.xlsx"
                
                report, filename = create_tabular_project_report(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict, project, report_attributes, save_dir_name, filename)
            
            else:
                
                if "template" in report_attributes:
                    template = report_attributes["template"]
                else:
                    template = DEFAULT_PROJECT_TEMPLATE
                    
                if "filename" in report_attributes:
                    filename = report_attributes["filename"]
                else:
                    filename = project + "_project_report.txt"
                
                report = create_project_report(publication_dict, config_dict, authors_by_project_dict, project, template)
                fileio.save_string_to_file(save_dir_name, filename, report)
            
            if "from_email" in report_attributes:
                email_messages["emails"].append({"body":report_attributes["email_body"],
                                                 "subject":report_attributes["email_subject"],
                                                 "from":report_attributes["from_email"],
                                                 "to":",".join([email for email in report_attributes["to_email"]]),
                                                 "cc":",".join([email for email in report_attributes["cc_email"]]) if "cc_email" in report_attributes else "",
                                                 "attachment":report,
                                                 "attachment_filename": filename})
            
        else:
             ## If authors is in project send an email to each author in the project.
            if "authors" in project_attributes:
                authors = project_attributes["authors"]
            
            ## If neither authors nor to_email is in the project then send emails to all authors that have publications.    
            else:
                authors = pubs_by_author_dict
                
            for author in authors:
                report_attributes = authors_by_project_dict[project][author]["project_report"]
                
                if not author in pubs_by_author_dict:
                    continue
                
                if "columns" in report_attributes:
                    if "file_format" in report_attributes:
                        file_format = report_attributes["file_format"]
                    else:
                        file_format = "csv"
                        
                    if "filename" in report_attributes:
                        filename = report_attributes["filename"]
                    else:
                        if file_format == "csv":
                            filename = project + "_" + author + "_project_report.csv"
                        else:
                            filename = project + "_" + author + "_project_report.xlsx"
                    
                    report, filename = create_tabular_project_report(publication_dict, config_dict, {project:{author:authors_by_project_dict[project][author]}}, pubs_by_author_dict, project, report_attributes, save_dir_name, filename)
                
                else:
                    if "template" in report_attributes:
                        template = report_attributes["template"]
                    else:
                        template = DEFAULT_AUTHOR_TEMPLATE
                        
                    if "filename" in report_attributes:
                        filename = report_attributes["filename"]
                    else:
                        filename = project + "_" + author + "_project_report.txt"
                    
                    report = create_project_report(publication_dict, config_dict, {project:{author:authors_by_project_dict[project][author]}}, project, template, config_dict["Authors"][author]["first_name"], config_dict["Authors"][author]["last_name"])
                    fileio.save_string_to_file(save_dir_name, filename, report)
                
                if "from_email" in report_attributes and "email" in authors_by_project_dict[project][author]:
                    email_messages["emails"].append({"body":authors_by_project_dict[project][author]["project_report"]["email_body"],
                                                     "subject":authors_by_project_dict[project][author]["project_report"]["email_subject"],
                                                     "from":authors_by_project_dict[project][author]["project_report"]["from_email"],
                                                     "to":authors_by_project_dict[project][author]["email"],
                                                     "cc":",".join([email for email in authors_by_project_dict[project][author]["project_report"]["cc_email"]]) if "cc_email" in authors_by_project_dict[project][author]["project_report"] else "",
                                                     "attachment": report,
                                                     "attachment_filename": filename,
                                                     "author":author})            
    
    return email_messages



def create_project_report(publication_dict, config_dict, authors_by_project_dict, project_name, template_string=DEFAULT_PROJECT_TEMPLATE, author_first = "", author_last = ""):
    """Create the project report for the project.
    
    The details of creating project reports are outlined in the documentation.
    Use the information in the config_dict, publication_dict, and authors_by_project_dict 
    to fill in the information in the template_string. If author_first is given then 
    it is assumed the report is actually for a single author and not a whole project.
    
    Args:
        publication_dict (dict): keys and values match the publications JSON file.
        config_dict (dict): keys and values match the project tracking configuration JSON file.
        authors_by_project_dict (dict): keys are project names from the config file and values are pulled from config_dict["Authors"].
        project_name (str): The name of the project.
        template_string (str): Template used to create the project report.
        author_first (str): First name of the author. If not "" the report is assumed to be for 1 author.
        author_last (str): Last name of the author.
    
    Returns:
        template_string (str): The template_string with the appropriate tags replaced with relevant information.        
    """
    
    project_authors = build_author_loop(publication_dict, config_dict, authors_by_project_dict, project_name, template_string)
    
    template_string = re.sub(r"(?s)<author_loop>.*</author_loop>", project_authors, template_string)
    if author_first:
        template_string = template_string.replace("<author_first>", author_first)
        template_string = template_string.replace("<author_last>", author_last)
    
    return template_string




def create_summary_report(publication_dict, config_dict, authors_by_project_dict, template_string=DEFAULT_SUMMARY_TEMPLATE):
    """Create the summary report for the run.
    
    The details of creating summary reports are outlined in the documentation.
    Use the information in the config_dict, publication_dict, and authors_by_project_dict 
    to fill in the information in the template_string.
    
    Args:
        publication_dict (dict): keys and values match the publications JSON file.
        config_dict (dict): keys and values match the project tracking configuration JSON file.
        authors_by_project_dict (dict): keys are project names from the config file and values are pulled from config_dict["Authors"].
        template_string (str): Template used to create the project report.
    
    Returns:
        report_string (str): The report built by replacing the appropriate tags in template_string with relevant information.
    """
    
    project_template = helper_functions.regex_group_return(helper_functions.regex_match_return(r"(?s).*<project_loop>(.*)</project_loop>.*", template_string), 0)
    
    report_string = ""
    for project_name in config_dict["project_descriptions"]:
        project_template_copy = project_template
        
        project_authors = build_author_loop(publication_dict, config_dict, authors_by_project_dict, project_name, template_string)
        
        project_template_copy = re.sub(r"(?s)<author_loop>.*</author_loop>", project_authors, project_template_copy)
        project_template_copy = project_template_copy.replace("<project_name>", project_name)
        
        report_string += project_template_copy
    
    report_string = re.sub(r"(?s)<project_loop>.*</project_loop>", report_string, template_string)
        
    return report_string




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
                           "<pub_author_affiliations>":"affiliation"}

publication_date_keywords_map = {"<publication_year>":"year",
                                 "<publication_month>":"month",
                                 "<publication_day>":"day"}

authors_keywords_map = {"<author_first>":"first_name",
                        "<author_last>":"last_name",
                        "<author_name_search>":"pubmed_name_search",
                        "<author_email>":"email"}

pub_keywords = list(simple_publication_keywords_map.keys()) + list(publication_date_keywords_map.keys()) + ["<first_author>", "<last_author>", "<authors>", "<grants>"]


def build_author_loop(publication_dict, config_dict, authors_by_project_dict, project_name, template_string):
    """Replace tags in template_string with the appropriate information.
    
    Args:
        publication_dict (dict): keys and values match the publications JSON file.
        config_dict (dict): keys and values match the project tracking configuration JSON file.
        authors_by_project_dict (dict): keys are project names from the config file and values are pulled from config_dict["Authors"].
        project_name (str): The name of the project.
        template_string (str): Template used to create the project report.
        
    Returns:
        project_authors (str): The string built by looping over the authors in authors_by_project_dict and using the template_string to build a report.
    """
    
    pubs_by_author_dict = create_pubs_by_author_dict(publication_dict)
    
    author_template = helper_functions.regex_group_return(helper_functions.regex_match_return(r"(?s).*<author_loop>(.*)</author_loop>.*", template_string), 0)
    pub_template = helper_functions.regex_group_return(helper_functions.regex_match_return(r"(?s).*<pub_loop>(.*)</pub_loop>.*", template_string), 0)
    pub_author_template = helper_functions.regex_group_return(helper_functions.regex_match_return(r"(?s).*<pub_author_loop>(.*)</pub_author_loop>.*", template_string), 0)
    
    project_authors = ""
    for author in authors_by_project_dict[project_name]:
        if not author in pubs_by_author_dict:
            continue
        author_template_copy = author_template
        
        authors_pubs = ""
        for pub in pubs_by_author_dict[author]:
            pub_template_copy = pub_template
            
            pub_authors = ""
            for pub_author in publication_dict[pub]["authors"]:
                pub_author_template_copy = pub_author_template
                
                for keyword, pub_author_key in pub_authors_keyword_map.items():
                    pub_author_template_copy = pub_author_template_copy.replace(keyword, str(pub_author[pub_author_key]))
                    
                pub_authors += pub_author_template_copy
                
            pub_template_copy = re.sub(r"(?s)<pub_author_loop>.*</pub_author_loop>", pub_authors, pub_template_copy)
            
            for keyword, pub_key in simple_publication_keywords_map.items():
                pub_template_copy = pub_template_copy.replace(keyword, str(publication_dict[pub][pub_key]))
                
            ## build first and last author
            first_author = str(publication_dict[pub]["authors"][0]["lastname"]) + ", " + str(publication_dict[pub]["authors"][0]["firstname"])
            pub_template_copy = pub_template_copy.replace("<first_author>", first_author)
            
            last_author = str(publication_dict[pub]["authors"][-1]["lastname"]) + ", " + str(publication_dict[pub]["authors"][-1]["firstname"])
            pub_template_copy = pub_template_copy.replace("<last_author>", last_author)
            
            authors = ", ".join([str(author["firstname"]) + " " + str(author["lastname"]) for author in publication_dict[pub]["authors"]])
            pub_template_copy = pub_template_copy.replace("<authors>", authors)
            
            if publication_dict[pub]["grants"]:
                grants = ", ".join(publication_dict[pub]["grants"])
            else:
                grants = "None Found"
            pub_template_copy = pub_template_copy.replace("<grants>", grants)
            
            for keyword, date_key in publication_date_keywords_map.items():
                pub_template_copy = pub_template_copy.replace(keyword, str(publication_dict[pub]["publication_date"][date_key]))
                    
            authors_pubs += pub_template_copy
        
        author_template_copy = re.sub(r"(?s)<pub_loop>.*</pub_loop>", authors_pubs, author_template_copy)
        for keyword, auth_key in authors_keywords_map.items():
            author_template_copy = author_template_copy.replace(keyword, str(config_dict["Authors"][author][auth_key]))
            
        project_authors += author_template_copy
        
    return project_authors




def create_tabular_collaborator_report(publication_dict, config_dict, author, pubs, filename, file_format, save_dir_name):
    """Create a table for a collaborator report and save as either csv or xlsx.
    
    Args:
        publication_dict (dict): keys and values match the publications JSON file.
        config_dict (dict): keys and values match the project tracking configuration JSON file.
        author (str): The key to the author in config_dict["Authors"].
        pubs (dict): Keys are publications for the author and values are the grants associated with that pub.
        filename (str): filename to save the publication under.
        file_format (str): csv or xlsx, determines what format to save in.
        save_dir_name (str): directory to save the report in.
        
    Returns:
        report (str): The text of the report, empty string, or path to the saved xlsx file.
        filename (str): Filename of the report. Made have had an .xlsx added to the end.
    """
    
    default_columns = {"Name":"<pub_author_last>, <pub_author_first>", "Affiliations":"<pub_author_affiliations>"}
    default_sort = ["Name"]
    default_order = ["Name", "Affiliations"]
    
    if "separator" in config_dict["Authors"][author]["collaborator_report"]:
        separator = config_dict["Authors"][author]["collaborator_report"]["separator"]
    else:
        separator = ","
    
    ## Determine whether to build the report to user specifications or use the deaults.
    if "columns" in config_dict["Authors"][author]["collaborator_report"]:
        columns = config_dict["Authors"][author]["collaborator_report"]["columns"]
        
        if "sort" in config_dict["Authors"][author]["collaborator_report"]:
            sort = config_dict["Authors"][author]["collaborator_report"]["sort"]
        else:
            sort = []
            
        if "column_order" in config_dict["Authors"][author]["collaborator_report"]:
            column_order = config_dict["Authors"][author]["collaborator_report"]["column_order"]
        else:
            column_order = list(columns.keys())
    else:
        columns = default_columns
        sort = default_sort
        column_order = default_order
        
    
    
    
    authors_already_added = []
    
    collaborators = []
    for pub in pubs:
        for pub_author in publication_dict[pub]["authors"]:
            
            if ("author_id" in pub_author and pub_author["author_id"] == author) or pub_author in authors_already_added:
                continue
            
            temp_dict = {}
            for column_name, value in columns.items():
                for keyword, pub_author_key in pub_authors_keyword_map.items():
                    value = value.replace(keyword, str(pub_author[pub_author_key]))
                temp_dict[column_name] = value
                
            collaborators.append(temp_dict)
            authors_already_added.append(pub_author)
    
                
    if collaborators:
        df = pandas.DataFrame(collaborators)
        if sort:
            df = df.sort_values(by=sort)
        df = df.drop_duplicates()
        df = df[column_order]
        
        if file_format == "csv":
            report = df.to_csv(index=False, sep=separator, line_terminator="\n")
            fileio.save_string_to_file(save_dir_name, filename, report)
        else:
            ## If the file extension isn't .xlsx then there will be an error, so force it.
            extension = os.path.splitext(filename)[1][1:].lower()
            if not extension == "xlsx":
                filename += ".xlsx"
            
            report = os.path.join(save_dir_name, filename)
            df.to_excel(report, index=False)
    else:
        report = ""
        
    return report, filename
    



def create_collaborator_report(publication_dict, template, author, pubs, filename, save_dir_name):
    """Create a collaborator report from a formatted string.
    
    Loop over all of the author's publications and create a 
    
    Args:
        publication_dict (dict): keys and values match the publications JSON file.
        author (str): The key to the author in config_dict["Authors"].
        pubs (dict): Keys are publications for the author and values are the grants associated with that pub.
        filename (str): filename to save the publication under.
        save_dir_name (str): directory to save the report in.
        
    Returns:
        report (str): The text of the report or an empty string.
    """
    
    authors_already_added = []
    
    pub_author_template = helper_functions.regex_group_return(helper_functions.regex_match_return(r"(?s).*<pub_author_loop>(.*)</pub_author_loop>.*", template), 0)
    
    report = ""
    for pub in pubs:
        for pub_author in publication_dict[pub]["authors"]:
            
            if ("author_id" in pub_author and pub_author["author_id"] == author) or pub_author in authors_already_added:
                continue
            
            pub_author_template_copy = pub_author_template
            
            for keyword, pub_author_key in pub_authors_keyword_map.items():
                pub_author_template_copy = pub_author_template_copy.replace(keyword, str(pub_author[pub_author_key]))
                
            report += pub_author_template_copy
            
            authors_already_added.append(pub_author)
            
    if report:
        report = re.sub(r"(?s)<pub_author_loop>.*</pub_author_loop>", report, template)
        fileio.save_string_to_file(save_dir_name, filename, report)
    
    return report





def create_collaborators_reports_and_emails(publication_dict, config_dict, save_dir_name):
    """Create a report of collaborators for authors in publication_dict.
    
    For each author in publication_dict with an author_id create a csv file with 
    the other authors on their publicaitons.
    
    Args:
        publication_dict (dict): keys and values match the publications JSON file.
        config_dict (dict): keys and values match the project tracking configuration JSON file.
        save_dir_name (str): directory to save the reports in.
        
    Returns:
        email_messages (dict): keys and values match the email JSON file.
    """

    pubs_by_author_dict = create_pubs_by_author_dict(publication_dict)
    
    # dict for email messages.
    email_messages = {"creation_date" : str(datetime.datetime.now())[0:16]}
    email_messages["emails"] = []
    
    for author, pubs in pubs_by_author_dict.items():
        
        ## Skip if the author isn't in the config dict or if the author doesn't have a collaborator report.
        if not author in config_dict["Authors"]:
            continue
        elif not "collaborator_report" in config_dict["Authors"][author]:
            continue
        
        
        if "template" in config_dict["Authors"][author]["collaborator_report"]:
            template = config_dict["Authors"][author]["collaborator_report"]["template"]
            
            if "filename" in config_dict["Authors"][author]["collaborator_report"]:
                filename = config_dict["Authors"][author]["collaborator_report"]["filename"]
            else:
                filename = author + "_collaborators.txt"
                
            report = create_collaborator_report(publication_dict, template, author, pubs, filename, save_dir_name)
        
        else:
        
            if "file_format" in config_dict["Authors"][author]["collaborator_report"]:
                file_format = config_dict["Authors"][author]["collaborator_report"]["file_format"]
            else:
                file_format = "csv"
                
            if "filename" in config_dict["Authors"][author]["collaborator_report"]:
                filename = config_dict["Authors"][author]["collaborator_report"]["filename"]
            else:
                if file_format == "csv":
                    filename = author + "_collaborators.csv"
                else:
                    filename = author + "_collaborators.xlsx"
                    
            report, filename = create_tabular_collaborator_report(publication_dict, config_dict, author, pubs, filename, file_format, save_dir_name)
            
        
        if report:
            if "from_email" in config_dict["Authors"][author]["collaborator_report"]:
                if "to_email" in config_dict["Authors"][author]["collaborator_report"]:
                    to_email = config_dict["Authors"][author]["collaborator_report"]["to_email"]
                else:
                    to_email = config_dict["Authors"][author]["email"] if "email" in config_dict["Authors"][author] else ""
                
                if to_email:
                    email_messages["emails"].append({"body":config_dict["Authors"][author]["collaborator_report"]["email_body"],
                                                     "subject":config_dict["Authors"][author]["collaborator_report"]["email_subject"],
                                                     "from":config_dict["Authors"][author]["collaborator_report"]["from_email"],
                                                     "to":to_email,
                                                     "cc":",".join([email for email in config_dict["Authors"][author]["collaborator_report"]["cc_email"]]) if "cc_email" in config_dict["Authors"][author]["collaborator_report"] else "",
                                                     "attachment": report,
                                                     "attachment_filename": filename,
                                                     "author":author})
        
    return email_messages
        



def create_tabular_summary_report(publication_dict, config_dict, authors_by_project_dict, save_dir_name):
    """Create a pandas DataFrame and save it as Excel or CSV.
    
    Args:
        publication_dict (dict): keys and values match the publications JSON file.
        config_dict (dict): keys and values match the project tracking configuration JSON file.
        authors_by_project_dict (dict): keys are project names from the config file and values are pulled from config_dict["Authors"].
        save_dir_name (str): directory to save the report in.
        
    Returns:
        report (str): Either the text of the report if csv or a relative filepath to where the Excel file is saved.
        filename (str): Filename of the report. Made have had an .xlsx added to the end.
    """
    
    pubs_by_author_dict = create_pubs_by_author_dict(publication_dict)
        
    rows = []
    row_template = copy.deepcopy(config_dict["summary_report"]["columns"])
    
    if "separator" in config_dict["summary_report"]:
        separator = config_dict["summary_report"]["separator"]
    else:
        separator = ","
        
    if "sort" in config_dict["summary_report"]:
        sort = config_dict["summary_report"]["sort"]
    else:
        sort = []
        
    if "column_order" in config_dict["summary_report"]:
        column_order = config_dict["summary_report"]["column_order"]
    else:
        column_order = list(row_template.keys())
        
    if "file_format" in config_dict["summary_report"]:
        file_format = config_dict["summary_report"]["file_format"]
    else:
        file_format = "csv"
        
    if "filename" in config_dict["summary_report"]:
        filename = config_dict["summary_report"]["filename"]
    else:
        if file_format == "csv":
            filename = "summary_report.csv"
        else:
            filename = "summary_report.xlsx"
    
    row_string = "".join(row_template.values())    
    if any([pub_keyword in row_string for pub_keyword in pub_keywords]):
        has_pub_keywords = True
    else:
        has_pub_keywords = False
        
    if any([pub_author_keyword in row_string for pub_author_keyword in pub_authors_keyword_map.keys()]):
        has_pub_author_keywords = True
    else:
        has_pub_author_keywords = False
    
    
    for project_name, project_attributes in config_dict["project_descriptions"].items():
        
        for author, author_attributes in authors_by_project_dict[project_name].items():
            if not author in pubs_by_author_dict:
                continue
            
            if has_pub_author_keywords or has_pub_keywords:
                for pub in pubs_by_author_dict[author]:
                    
                    if has_pub_author_keywords:
                        for pub_author in publication_dict[pub]["authors"]:
                            
                            rows.append(replace_keywords(row_template, publication_dict, config_dict, project_name, author, pub, pub_author))
                            
                    else:
                        rows.append(replace_keywords(row_template, publication_dict, config_dict, project_name, author, pub))
                        
            else:
                rows.append(replace_keywords(row_template, publication_dict, config_dict, project_name, author))
                
    
    report = ""            
    if rows:
        df = pandas.DataFrame(rows)
        if sort:
            df = df.sort_values(by=sort)
        df = df.drop_duplicates()
        df = df[column_order]
        
        if file_format == "csv":
            report = df.to_csv(index=False, sep=separator, line_terminator="\n")
            fileio.save_string_to_file(save_dir_name, filename, report)
        else:
            ## If the file extension isn't .xlsx then there will be an error, so force it.
            extension = os.path.splitext(filename)[1][1:].lower()
            if not extension == "xlsx":
                filename += ".xlsx"
            
            report = os.path.join(save_dir_name, filename)
            df.to_excel(report, index=False)
            
    return report, filename



def create_tabular_project_report(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict, project_name, report_attributes, save_dir_name, filename):
    """Create a pandas DataFrame and save it as Excel or CSV.
    
    Args:
        publication_dict (dict): keys and values match the publications JSON file.
        config_dict (dict): keys and values match the project tracking configuration JSON file.
        authors_by_project_dict (dict): keys are project names from the config file and values are pulled from config_dict["Authors"].
        pubs_by_author_dict (dict): dictionary where the keys are authors and the values are a dictionary of pub_ids with thier associated grants.
        project_name (str): Name of the project.
        report_attributes (dict): Dictionary of the report attributes. Could come from project_descriptions or an author.
        save_dir_name (str): directory to save the report in.
        filename (str): Filename of the report.
        
    Returns:
        report (str): Either the text of the report if csv or a relative filepath to where the Excel file is saved.
        filename (str): Filename of the report. Made have had an .xlsx added to the end.
    """
    
    rows = []
    row_template = copy.deepcopy(report_attributes["columns"])
    
    if "separator" in report_attributes:
        separator = report_attributes["separator"]
    else:
        separator = ","
        
    if "sort" in report_attributes:
        sort = report_attributes["sort"]
    else:
        sort = []
        
    if "column_order" in report_attributes:
        column_order = report_attributes["column_order"]
    else:
        column_order = list(row_template.keys())
        
    if "file_format" in report_attributes:
        file_format = report_attributes["file_format"]
    else:
        file_format = "csv"
    
        
    row_string = "".join(row_template.values())    
    if any([pub_keyword in row_string for pub_keyword in pub_keywords]):
        has_pub_keywords = True
    else:
        has_pub_keywords = False
        
    if any([pub_author_keyword in row_string for pub_author_keyword in pub_authors_keyword_map.keys()]):
        has_pub_author_keywords = True
    else:
        has_pub_author_keywords = False
    
    
    for author, author_attributes in authors_by_project_dict[project_name].items():
        if not author in pubs_by_author_dict:
            continue
        
        if has_pub_author_keywords or has_pub_keywords:
            for pub in pubs_by_author_dict[author]:
                
                if has_pub_author_keywords:
                    for pub_author in publication_dict[pub]["authors"]:
                        
                        rows.append(replace_keywords(row_template, publication_dict, config_dict, project_name, author, pub, pub_author))
                        
                else:
                    rows.append(replace_keywords(row_template, publication_dict, config_dict, project_name, author, pub))
                    
        else:
            rows.append(replace_keywords(row_template, publication_dict, config_dict, project_name, author))
                
    
    report = ""            
    if rows:
        df = pandas.DataFrame(rows)
        if sort:
            df = df.sort_values(by=sort)
        df = df.drop_duplicates()
        df = df[column_order]
        
        if file_format == "csv":
            report = df.to_csv(index=False, sep=separator, line_terminator="\n")
            fileio.save_string_to_file(save_dir_name, filename, report)
        else:
            ## If the file extension isn't .xlsx then there will be an error, so force it.
            extension = os.path.splitext(filename)[1][1:].lower()
            if not extension == "xlsx":
                filename += ".xlsx"
            
            report = os.path.join(save_dir_name, filename)
            df.to_excel(report, index=False)
            
    return report, filename
                    
                    
                    

def replace_keywords(template, publication_dict, config_dict, project_name="", author="", pub="", pub_author={}):
    """Replace keywords in the values of the template dictionary.
    
    Args:
        template (dict): keys are column names and values are what the elements of the column should be.
        publication_dict (dict): keys and values match the publications JSON file.
        config_dict (dict): keys and values match the project tracking configuration JSON file.
        project_name (str): the name of the project to replace.
        author (str): the key to the author in config_dict["Authors"].
        pub (str): the key to the pub in publication_dict.
        pub_author (dict): The author in pub.
        
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
                template_copy[key] = template_copy[key].replace(keyword, str(config_dict["Authors"][author][auth_key]))
        
        ## Publication keywords
        if pub:
            for keyword, pub_key in simple_publication_keywords_map.items():
                template_copy[key] = template_copy[key].replace(keyword, str(publication_dict[pub][pub_key]))
                
            ## build first and last author
            first_author = str(publication_dict[pub]["authors"][0]["lastname"]) + ", " + str(publication_dict[pub]["authors"][0]["firstname"])
            template_copy[key] = template_copy[key].replace("<first_author>", first_author)
            
            last_author = str(publication_dict[pub]["authors"][-1]["lastname"]) + ", " + str(publication_dict[pub]["authors"][-1]["firstname"])
            template_copy[key] = template_copy[key].replace("<last_author>", last_author)
            
            authors = ", ".join([str(author["firstname"]) + " " + str(author["lastname"]) for author in publication_dict[pub]["authors"]])
            template_copy[key] = template_copy[key].replace("<authors>", authors)
            
            if publication_dict[pub]["grants"]:
                grants = ", ".join(publication_dict[pub]["grants"])
            else:
                grants = "None Found"
            template_copy[key] = template_copy[key].replace("<grants>", grants)
            
            for keyword, date_key in publication_date_keywords_map.items():
                template_copy[key] = template_copy[key].replace(keyword, str(publication_dict[pub]["publication_date"][date_key]))
        
        ## Pub authors keywords
        if pub_author:
            for keyword, pub_author_key in pub_authors_keyword_map.items():
                template_copy[key] = template_copy[key].replace(keyword, str(pub_author[pub_author_key]))
            
    return template_copy
        






