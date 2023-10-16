# -*- coding: utf-8 -*-
"""
Author Search Modularized
~~~~~~~~~~~~~~~~~~~~~~~~~

Modularized pieces of author_search.
"""
import sys
import re
import datetime
import os

import deepdiff

from . import user_input_checking
from . import fileio
from . import helper_functions
from . import athr_srch_webio
from . import athr_srch_emails_and_reports
from . import webio


def input_reading_and_checking(config_json_filepath, no_ORCID, no_GoogleScholar, no_Crossref, no_PubMed):
    """Read in inputs from user and do error checking.
    
    Args:
        config_json_filepath (str): filepath to the configuration JSON.
        no_ORCID (bool): If True search ORCID else don't. Reduces checking on config JSON if True.
        no_GoogleScholar (bool): if True search Google Scholar else don't. Reduces checking on config JSON if True.
        no_Crossref (bool): If True search Crossref else don't. Reduces checking on config JSON if True.
        no_PubMed (bool): If True search PubMed else don't. Reduces checking on config JSON if True.
        
    Returns:
        config_dict (dict): Matches the Configuration file JSON schema.
    """    
    ## read in config file
    config_dict = fileio.load_json(config_json_filepath)
    
    if not "ORCID_search" in config_dict:
        no_ORCID = True
        
    if not "Crossref_search" in config_dict:
        no_Crossref = True
        
    if not "PubMed_search" in config_dict:
        no_PubMed = True
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.config_file_check(config_dict, no_ORCID, no_GoogleScholar, no_Crossref, no_PubMed)
    user_input_checking.config_report_check(config_dict)
    
    return config_dict




def generate_internal_data_and_check_authors(config_dict):
    """Create authors_by_project_dict and look for authors without projects.
    
    Args:
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
    
    if authors_not_in_projects and projects_without_authors:
        helper_functions.vprint("Warning: The following authors in the Authors section of the configuration JSON file are not in any project.")
        for author in authors_not_in_projects:
            helper_functions.vprint(author)
            
    return authors_by_project_dict, config_dict



def build_publication_dict(config_dict, prev_pubs, no_ORCID, no_GoogleScholar, no_Crossref, no_PubMed):
    """Query PubMed, ORCID, Google Scholar, and Crossref for publications for the authors.
    
    Args:
        config_dict (dict): Matches the Configuration file JSON schema.
        prev_pubs (dict): Matches the publication JSON schema. Used to ignore publications when querying.
        no_ORCID (bool): If True search ORCID else don't.
        no_GoogleScholar (bool): if True search Google Scholar else don't.
        no_Crossref (bool): If True search Crossref else don't.
        no_PubMed (bool): If True search PubMed else don't.
        
    Returns:
        running_pubs (dict): The dictionary matching the publication JSON schema.
        all_queries (dict): The pubs searched for each source and each author. {"PubMed":{"author1":[pub1, ...], ...}, "ORCID":{"author1":[pub1, ...], ...}, "Google Scholar":{"author1":[pub1, ...], ...}, "Crossref":{"author1":[pub1, ...], ...}}
    """
    
    ## Get publications from PubMed 
    helper_functions.vprint("Finding author's publications. This could take a while.")
    running_pubs = {}
    all_queries = {}
    if not no_PubMed:
        helper_functions.vprint("Searching PubMed.")
        running_pubs, PubMed_publication_dict = athr_srch_webio.search_PubMed_for_pubs(running_pubs, config_dict["Authors"], config_dict["PubMed_search"]["PubMed_email"])
        all_queries["PubMed"] = PubMed_publication_dict
    if not no_ORCID:
        helper_functions.vprint("Searching ORCID.")
        running_pubs, ORCID_publication_dict = athr_srch_webio.search_ORCID_for_pubs(running_pubs, config_dict["ORCID_search"]["ORCID_key"], config_dict["ORCID_search"]["ORCID_secret"], config_dict["Authors"])
        all_queries["ORCID"] = ORCID_publication_dict
    if not no_GoogleScholar:
        helper_functions.vprint("Searching Google Scholar.")
        running_pubs, Google_Scholar_publication_dict = athr_srch_webio.search_Google_Scholar_for_pubs(running_pubs, config_dict["Authors"], config_dict["Crossref_search"]["mailto_email"])
        all_queries["Google Scholar"] = Google_Scholar_publication_dict
    if not no_Crossref:
        helper_functions.vprint("Searching Crossref.")
        running_pubs, Crossref_publication_dict = athr_srch_webio.search_Crossref_for_pubs(running_pubs, config_dict["Authors"], config_dict["Crossref_search"]["mailto_email"])
        all_queries["Crossref"] = Crossref_publication_dict
    
    ## Do a second pass using the saved queries.
    if not no_PubMed:
        running_pubs, PubMed_publication_dict = athr_srch_webio.search_PubMed_for_pubs(running_pubs, config_dict["Authors"], config_dict["PubMed_search"]["PubMed_email"], all_queries["PubMed"])
    if not no_ORCID:
        running_pubs, ORCID_publication_dict = athr_srch_webio.search_ORCID_for_pubs(running_pubs, config_dict["ORCID_search"]["ORCID_key"], config_dict["ORCID_search"]["ORCID_secret"], config_dict["Authors"], all_queries["ORCID"])
    if not no_GoogleScholar:
        running_pubs, Google_Scholar_publication_dict = athr_srch_webio.search_Google_Scholar_for_pubs(running_pubs, config_dict["Authors"], config_dict["Crossref_search"]["mailto_email"], all_queries["Google Scholar"])
    if not no_Crossref:
        running_pubs, Crossref_publication_dict = athr_srch_webio.search_Crossref_for_pubs(running_pubs, config_dict["Authors"], config_dict["Crossref_search"]["mailto_email"], all_queries["Crossref"])
        
    ## Compare current pubs with previous and only keep those that are new or updated.
    for pub_id, pub_values in prev_pubs.items():
        if pub_id in running_pubs and not deepdiff.DeepDiff(running_pubs[pub_id], pub_values, ignore_order=True, report_repetition=True):
            del running_pubs[pub_id]
        
    if len(running_pubs) == 0:
        helper_functions.vprint("No new publications found.")
        sys.exit()
        
    ## Convert PubMed articles class to dicts so they can be saved as JSON.
    if not no_PubMed:
        for author, pub_list in all_queries["PubMed"].items():
            new_list = []
            for pub in pub_list:
                _, pub_dict = helper_functions.create_pub_dict_for_saving_PubMed(pub, True)
                new_list.append(pub_dict)
            all_queries["PubMed"][author] = new_list
        
    return running_pubs, all_queries



def save_and_send_reports_and_emails(authors_by_project_dict, publication_dict, config_dict, test):
    """Build the summary report and project reports and email them.
    
    Args:
        authors_by_project_dict (dict): Keys are project names and values are a dictionary of authors and their attributes.
        publication_dict (dict): The dictionary matching the publication JSON schema.
        config_dict (dict): Matches the Configuration file JSON schema.
        test (bool): If True save_dir_name is tracker-test instead of tracker- and emails are not sent.
        
    Returns:
        save_dir_name (str): Name of the directory where the emails and reports were saved.
    """
    
    ## Build the save directory name.
    if test:
        save_dir_name = "tracker-test-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
    else:
        save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
    os.mkdir(save_dir_name)
        
    
    email_messages = athr_srch_emails_and_reports.create_project_reports_and_emails(authors_by_project_dict, publication_dict, config_dict, save_dir_name)
    email_messages["emails"] = email_messages["emails"] + athr_srch_emails_and_reports.create_collaborators_reports_and_emails(publication_dict, config_dict, save_dir_name)["emails"]
            
    if "summary_report" in config_dict:
        
        if "columns" in config_dict["summary_report"]:
            summary_report, summary_filename = athr_srch_emails_and_reports.create_tabular_summary_report(publication_dict, config_dict, authors_by_project_dict, save_dir_name)
        
        else:
            if "template" in config_dict["summary_report"]:
                template = config_dict["summary_report"]["template"]
            else:
                template = athr_srch_emails_and_reports.DEFAULT_SUMMARY_TEMPLATE
                
            if "filename" in config_dict["summary_report"]:
                summary_filename = config_dict["summary_report"]["filename"]
            else:
                summary_filename = "summary_report.txt"
            
            summary_report = athr_srch_emails_and_reports.create_summary_report(publication_dict, config_dict, authors_by_project_dict, template)
            fileio.save_string_to_file(save_dir_name, summary_filename, summary_report)
        
        if "from_email" in config_dict["summary_report"]:
            email_messages["emails"].append({"to":",".join([email for email in config_dict["summary_report"]["to_email"]]),
                                             "from":config_dict["summary_report"]["from_email"],
                                             "cc":",".join([email for email in config_dict["summary_report"]["cc_email"]]) if "cc_email" in config_dict["summary_report"] else "",
                                             "subject":config_dict["summary_report"]["email_subject"],
                                             "body":config_dict["summary_report"]["email_body"],
                                             "attachment":summary_report,
                                             "attachment_filename": summary_filename})
            
    if email_messages["emails"]:
        ## save email messages to file
        fileio.save_emails_to_file(email_messages, save_dir_name)
    
        ## send emails
        if not test:
            webio.send_emails(email_messages)
    
    return save_dir_name


