# -*- coding: utf-8 -*-
"""
Modularized pieces of reference_search.
"""

import re
import datetime
import os

from . import user_input_checking
from . import fileio
from . import helper_functions
from . import ref_srch_webio
from . import ref_srch_emails_and_reports
from . import webio



def input_reading_and_checking(args):
    """Read in inputs from user and do error checking.
    
    Args:
        args (dict): The dictionary output from DocOpt.
        
    Returns:
        config_dict (dict): Matches the Configuration file JSON schema.
        tokenized_citations (list): list of dicts. Matches the tokenized citations JSON schema.
        has_previous_pubs (bool): True if a prev_pub file was input, False otherwise.
        prev_pubs (dict): The contents of the prev_pub file input by the user if provided.
    """
    
    user_input_checking.cli_inputs_check(args)
    
    ## read in config file
    config_dict = fileio.load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.ref_config_file_check(config_dict, args)
    
    if not args["--prev_pub"] or args["--prev_pub"].lower() == "ignore":
        prev_pubs = {}
        has_previous_pubs = False
    else:
        prev_pubs = fileio.load_json(args["--prev_pub"])
        has_previous_pubs = True
    
    if has_previous_pubs:
        user_input_checking.prev_pubs_file_check(prev_pubs)
        
    tokenized_citations = ref_srch_webio.tokenize_reference_input(args["<references_file_or_URL>"], args["--MEDLINE_reference"], args["--verbose"]) 
    
    return config_dict, tokenized_citations, has_previous_pubs, prev_pubs



def build_publication_dict(args, config_dict, tokenized_citations):
    """Query PubMed and Crossref for publications matching the citations in tokenized_citations.
    
    Args:
        args (dict): The dictionary output from DocOpt.
        config_dict (dict): Matches the Configuration file JSON schema.
        tokenized_citations (list): list of dicts. Matches the tokenized citations JSON schema.
        
    Returns:
        publication_dict (dict): The dictionary matching the publication JSON schema.
        tokenized_citations (list): Same list as the input but with the pud_dict_key updated to match the publication found.        
    """
    
    print("Finding publications. This could take a while.")
    print("Searching PubMed.")
    PubMed_publication_dict, PubMed_matching_key_for_citation = ref_srch_webio.search_references_on_PubMed(tokenized_citations, config_dict["PubMed_search"]["PubMed_email"], args["--verbose"])
#    if not args["--no_GoogleScholar"]:
#        print("Searching Google Scholar.")
#        Google_Scholar_publication_dict, Google_Scholar_matching_key_for_citation = webio.search_references_on_Google_Scholar(tokenized_citations, config_dict["Crossref_search"]["Crossref_email"], args["--verbose"])
    if not args["--no_Crossref"]:
        print("Searching Crossref.")
        Crossref_publication_dict, Crossref_matching_key_for_citation = ref_srch_webio.search_references_on_Crossref(tokenized_citations, config_dict["Crossref_search"]["mailto_email"], args["--verbose"])
    
    publication_dict = PubMed_publication_dict
#    if not args["--no_GoogleScholar"]:
#        for key, value in Google_Scholar_publication_dict.items():
#            if not key in publication_dict:
#                publication_dict[key] = value
    if not args["--no_Crossref"]:
        for key, value in Crossref_publication_dict.items():
            if not key in publication_dict:
                publication_dict[key] = value
            
    matching_key_for_citation = PubMed_matching_key_for_citation
#    if not args["--no_GoogleScholar"]:
#        matching_key_for_citation = [key if key else Google_Scholar_matching_key_for_citation[count] for count, key in enumerate(matching_key_for_citation)]
    if not args["--no_Crossref"]:
        matching_key_for_citation = [key if key else Crossref_matching_key_for_citation[count] for count, key in enumerate(matching_key_for_citation)]
        
    for count, citation in enumerate(tokenized_citations):
        if matching_key_for_citation[count]:
            citation["pub_dict_key"] = matching_key_for_citation[count]
            
    return publication_dict, tokenized_citations



def save_and_send_reports_and_emails(args, config_dict, tokenized_citations, publication_dict, prev_pubs, has_previous_pubs):
    """Build the summary report and email it.
    
    Args:
        args (dict): The dictionary output from DocOpt.
        config_dict (dict): Matches the Configuration file JSON schema.
        tokenized_citations (list): list of dicts. Matches the tokenized citations JSON schema.
        publication_dict (dict): The dictionary matching the publication JSON schema.
        prev_pubs (dict): The contents of the prev_pub file input by the user if provided.
        has_previous_pubs (bool): True if a prev_pub file was input, False otherwise.
        
    Returns:
        save_dir_name (str): Name of the directory where the emails and report were saved.
    """
    
    ## Compare citations to prev_pubs 
    is_citation_in_prev_pubs_list = []
    if has_previous_pubs:
        is_citation_in_prev_pubs_list = helper_functions.are_citations_in_pub_dict(tokenized_citations, prev_pubs)
        
    
    ## Build the save directory name.
    if args["--test"]:
        save_dir_name = "tracker-test-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
    else:
        save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
    
    
    if "summary_report" in config_dict:
        
        if "template" in config_dict["summary_report"]:
            template = config_dict["summary_report"]["template"]
        else:
            template = ref_srch_emails_and_reports.DEFAULT_SUMMARY_TEMPLATE
        
        summary_report = ref_srch_emails_and_reports.create_report_from_template(publication_dict, is_citation_in_prev_pubs_list, tokenized_citations, template)
        summary_filename = "summary_report.txt"
        fileio.save_string_to_file(save_dir_name, summary_filename, summary_report)
        
        if "from_email" in config_dict["summary_report"]:
            email_messages = {"creation_date" : str(datetime.datetime.now())[0:16]}
            email_messages["emails"] = [{"to":",".join([email for email in config_dict["summary_report"]["to_email"]]),
                                         "from":config_dict["summary_report"]["from_email"],
                                         "cc":",".join([email for email in config_dict["summary_report"]["cc_email"]]),
                                         "subject":config_dict["summary_report"]["email_subject"],
                                         "body":config_dict["summary_report"]["email_body"],
                                         "attachment":summary_report,
                                         "attachment_filename": summary_filename}]
            
            fileio.save_emails_to_file(email_messages, save_dir_name)
        
            ## send emails
            if not args["--test"]:
                webio.send_emails(email_messages)
                
    return save_dir_name





