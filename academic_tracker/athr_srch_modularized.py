# -*- coding: utf-8 -*-
"""
Modularized pieces of author_search.
"""
import sys
import re
import datetime
import os

from . import user_input_checking
from . import fileio
from . import helper_functions
from . import athr_srch_webio
from . import athr_srch_emails_and_reports
from . import webio


def input_reading_and_checking(args):
    """Read in inputs from user and do error checking.
    
    Args:
        args (dict): The dictionary output from DocOpt.
        
    Returns:
        config_dict (dict): Matches the Configuration file JSON schema.
    """
    
    user_input_checking.cli_inputs_check(args)
        
    ## read in config file
    config_dict = fileio.load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.config_file_check(config_dict, args)
    
    return config_dict




def generate_internal_data_and_check_authors(args, config_dict):
    """Create authors_by_project_dict and look for authors without projects.
    
    Args:
        args (dict): The dictionary output from DocOpt.
        config_dict (dict): Matches the Configuration file JSON schema.
        
    Returns:
        authors_by_project_dict (dict): Keys are project names and values are a dictionary of authors and their attributes.
        config_dict (dict): same as input but with author information updated based on project information.
    """
    
    ## Create an authors_json for each project in the config_dict and update those authors attributes with the project attributes.
    authors_by_project_dict = helper_functions.create_authors_by_project_dict(config_dict)
                
    ## Find minimum cutoff_year, and take the union of affiliations and grants for each author.
    helper_functions.adjust_author_attributes(authors_by_project_dict, config_dict)
                    
    ## Look for authors not in any projects and warn user.
    authors_in_projects = {author for project_attributes in config_dict["project_descriptions"].values() if "authors" in project_attributes for author in project_attributes["authors"]}
    authors_not_in_projects = set(config_dict["Authors"].keys()) - authors_in_projects
    projects_without_authors = [project for project, project_attributes in config_dict["project_descriptions"].items() if not "authors" in project_attributes]
    
    if authors_not_in_projects and projects_without_authors and args["--verbose"]:
        print("Warning: The following authors in the Authors section of the configuration JSON file are not in any project.")
        for author in authors_not_in_projects:
            print(author)
            
    return authors_by_project_dict, config_dict



def build_publication_dict(args, config_dict, prev_pubs):
    """Query PubMed, ORCID, Google Scholar, and Crossref for publications for the authors.
    
    Args:
        args (dict): The dictionary output from DocOpt.
        config_dict (dict): Matches the Configuration file JSON schema.
        prev_pubs (dict): Matches the publication JSON schema. Used to ignore publications when querying.
        
    Returns:
        publication_dict (dict): The dictionary matching the publication JSON schema.
        prev_pubs (dict): Same as input, but updated with the new publications found.
    """
    
    ## Get publications from PubMed 
    print("Finding author's publications. This could take a while.")
    print("Searching PubMed.")
    PubMed_publication_dict = athr_srch_webio.search_PubMed_for_pubs(prev_pubs, config_dict["Authors"], config_dict["PubMed_search"]["PubMed_email"], args["--verbose"])
    prev_pubs.update(PubMed_publication_dict)
    if not args["--no_ORCID"]:
        print("Searching ORCID.")
        ORCID_publication_dict = athr_srch_webio.search_ORCID_for_pubs(prev_pubs, config_dict["ORCID_search"]["ORCID_key"], config_dict["ORCID_search"]["ORCID_secret"], config_dict["Authors"], args["--verbose"])
        prev_pubs.update(ORCID_publication_dict)
    if not args["--no_GoogleScholar"]:
        print("Searching Google Scholar.")
        Google_Scholar_publication_dict = athr_srch_webio.search_Google_Scholar_for_pubs(prev_pubs, config_dict["Authors"], config_dict["Crossref_search"]["mailto_email"], args["--verbose"])
        prev_pubs.update(Google_Scholar_publication_dict)
    if not args["--no_Crossref"]:
        print("Searching Crossref.")
        Crossref_publication_dict = athr_srch_webio.search_Crossref_for_pubs(prev_pubs, config_dict["Authors"], config_dict["Crossref_search"]["mailto_email"], args["--verbose"])
        prev_pubs.update(Crossref_publication_dict)
    
    publication_dict = PubMed_publication_dict
    if not args["--no_ORCID"]:
        for key, value in ORCID_publication_dict.items():
            if not key in publication_dict:
                publication_dict[key] = value
    if not args["--no_GoogleScholar"]:
        for key, value in Google_Scholar_publication_dict.items():
            if not key in publication_dict:
                publication_dict[key] = value
    if not args["--no_Crossref"]:
        for key, value in Crossref_publication_dict.items():
            if not key in publication_dict:
                publication_dict[key] = value
        
        
    if len(publication_dict) == 0:
        print("No new publications found.")
        sys.exit()
        
    return publication_dict, prev_pubs



def save_and_send_reports_and_emails(args, authors_by_project_dict, publication_dict, config_dict):
    """Build the summary report and project reports and email them.
    
    Args:
        args (dict): The dictionary output from DocOpt.
        authors_by_project_dict (dict): Keys are project names and values are a dictionary of authors and their attributes.
        publication_dict (dict): The dictionary matching the publication JSON schema.
        config_dict (dict): Matches the Configuration file JSON schema.
        
    Returns:
        save_dir_name (str): Name of the directory where the emails and reports were saved.
    """
    
    ## Build the save directory name.
    if args["--test"]:
        save_dir_name = "tracker-test-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
    else:
        save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
        
    
    email_messages = athr_srch_emails_and_reports.create_project_reports_and_emails(authors_by_project_dict, publication_dict, config_dict, save_dir_name)
            
    if "summary_report" in config_dict:
        
        if "template" in config_dict["summary_report"]:
            template = config_dict["summary_report"]["template"]
        else:
            template = athr_srch_emails_and_reports.DEFAULT_SUMMARY_TEMPLATE
        
        summary_report = athr_srch_emails_and_reports.create_summary_report(publication_dict, config_dict, authors_by_project_dict, template)
        summary_filename = "summary_report.txt"
        fileio.save_string_to_file(save_dir_name, summary_filename, summary_report)
        
        if "from_email" in config_dict["summary_report"]:
            email_messages["emails"].append({"to":",".join([email for email in config_dict["summary_report"]["to_email"]]),
                                             "from":config_dict["summary_report"]["from_email"],
                                             "cc":",".join([email for email in config_dict["summary_report"]["cc_email"]]),
                                             "subject":config_dict["summary_report"]["email_subject"],
                                             "body":config_dict["summary_report"]["email_body"],
                                             "attachment":summary_report,
                                             "attachment_filename": summary_filename})
            
    if email_messages["emails"]:
        ## save email messages to file
        fileio.save_emails_to_file(email_messages, save_dir_name)
    
        ## send emails
        if not args["--test"]:
            webio.send_emails(email_messages)
    
    return save_dir_name








