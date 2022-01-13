"""   
Usage:
    academic_tracker author_search <config_json_file> [--test,--prev_pub]
    academic_tracker reference_search <config_json_file> <references_file_or_URL> [--test,--prev_pub,--PMID_reference,--MEDLINE_reference]
    academic_tracker find_ORCID <config_json_file> 
    academic_tracker find_Google_Scholar <config_json_file> 
    academic_tracker add_authors <config_json_file> <authors_file> 
    
Options:
    -h --help                         Show this screen.
    --version                         Show version.
    --verbose                         Print hidden error messages.
    --test                            Generate pubs and email texts, but do not send emails.
    --PMID_reference                  Indicates that the reference_file is a PMID file and only PubMed info will be returned.
    --MEDLINE_reference               Indicates that the reference_file is a MEDLINE file.
    --prev_pub=<file-path>            Filepath to json or csv with publication ids to ignore. Enter "ignore" for the <file_path> to not look for previous publications.json files in tracker directories.
    --no_GoogleScholar                Don't search Google Scholar.
    --no_ORCID                        Don't search ORCID.
    --no_Crossref                     Don't search Crossref.
"""


## TODO add usage case for reading in a author csv or excel file and creating json.
## TODO add options to ignore google scholar and orcid
## TODO add functionality to more easily handle verbose option, and add more messages when it is in use.
## TODO add journal to queried info in summary report. Make the summary report now a raw debug report.
## Change config schema to reflect what is on wiki. Implement default project stuff.
## Make all publication.json keys keywords for reports, make tokenized data available and reference line.
## Add a way for a user to test the report and email formatting.
## Add option to tokenize a reference file and create JSON, add capability to read tokenized json to ref_search, probably going to have to change reading in previous pubs so it looks at more than the newest folder.

## Less important or far future things:
## TODO improve reference search to see if every author on the pub has the pub associated with them on ORCID



import re
import os
import datetime
import sys
import copy

import docopt

from . import __version__
from . import fileio
from . import user_input_checking
from . import athr_srch_webio
from . import ref_srch_webio
from . import webio
from . import helper_functions
from . import athr_srch_emails_and_reports
from . import ref_srch_emails_and_reports
from . import tracker_schema
from . import citation_parsing



def main():
    
    args = docopt.docopt(__doc__, version=str("Academic Tracker ") + __version__)
    
    if len(sys.argv) > 1 and sys.argv[1] == "author_search":
        author_search(args)
    elif len(sys.argv) > 1 and sys.argv[1] == "reference_search":
        if args["--PMID_reference"]:
            PMID_reference(args)
        else:
            reference_search(args)
    elif len(sys.argv) > 1 and sys.argv[1] == "find_ORCID":
        find_ORCID(args)
    elif len(sys.argv) > 1 and sys.argv[1] == "find_Google_Scholar":
        find_Google_Scholar(args)
    else:
        print("Unrecognized command")  
        


def author_search(args):
    """Query PubMed for publications by author.
    
    Reads in the JSON config file, authors JSON file, previous publications JSON file, and checks for errors.
    Then searches PubMed, ORCID, Google Scholar, and Crossref for publications for each author.
    Emails are then created and sent to project leaders or individual authors. Emails and
    publications are saved to file and emails are sent depending on the options entered by the user. 
    See the program docstring for options details.
    
    Args:
        args (dict): args from DocOpt CLI
    """
    
    user_input_checking.cli_inputs_check(args)
        
    ## read in config file
    config_dict = fileio.load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.config_file_check(config_dict)

    ## Overwrite values in config_dict if command line options were used.
    ## Note the replacement is after checking both inputs and config_dict independently. If done before config_file_check then CLI errors will display as config_dict errors.
#    config_dict = helper_functions.overwrite_config_with_CLI(config_dict, args)
    
    ## Create an authors_json for each project in the config_dict and update those authors attributes with the project attributes.
    authors_by_project_dict = helper_functions.create_authors_by_project_dict(config_dict)
                
    ## Find minimum cutoff_year, and take the union of affiliations and grants for each author.
    helper_functions.adjust_author_attributes(authors_by_project_dict, config_dict)
                    
    ## Look for authors not in any projects and warn user.
    authors_in_projects = {author for project_attributes in config_dict["project_descriptions"].values() for author in project_attributes["authors"] if "authors" in project_attributes }
    authors_not_in_projects = set(config_dict["Authors"].keys()) - authors_in_projects
    projects_without_authors = [project for project, project_attributes in config_dict["project_descriptions"].items() if not "authors" in project_attributes]
    
    if authors_not_in_projects and projects_without_authors:
        print("Warning: The following authors in the Authors JSON file are not in any project.")
        for author in authors_not_in_projects:
            print(author)
    
        
    ## read in previous publications to ignore
    has_previous_pubs, prev_pubs = fileio.read_previous_publications(args)
    if has_previous_pubs:
        user_input_checking.prev_pubs_file_check(prev_pubs)
            
            
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
    
    
    email_messages = athr_srch_emails_and_reports.create_emails_dict(authors_by_project_dict, publication_dict, config_dict)
    
    
    ## Build the save directory name.
    if args["--test"]:
        save_dir_name = "tracker-test-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
    else:
        save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
        
    
    ## save email messages to file
    fileio.save_emails_to_file(email_messages, save_dir_name)
            
    ## send emails
    if not args["--test"]:
        webio.send_emails(email_messages)
    
    ## Create summmary report and save to file.
    fileio.save_author_summary_report_to_file(template_string, publication_dict, config_dict, authors_by_project_dict, save_dir_name)
    
    ## combine previous and new publications lists and save
    fileio.save_publications_to_file(save_dir_name, publication_dict, prev_pubs)
    
    print("Success. Publications, reports, and emails saved in " + save_dir_name)



def reference_search(args):
    """
    """
    
    user_input_checking.cli_inputs_check(args)
    ## read in config file
    config_dict = fileio.load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
    ## TODO change this so it only checks the sections of the config actually used.
    has_email_keys = user_input_checking.ref_config_file_check(config_dict)
    
    if args["--prev_pub"]:
        if args["--prev_pubs"].lower() == "ignore":
            prev_pubs = {}
            has_previous_pubs = False
        else:
            prev_pubs = fileio.load_json(args["--prev_pub"])
            has_previous_pubs = True
        
            
    ## Check the reference file input and see if it is a URL
    if re.match(r"http.*", args["<reference_file_or_URL>"]):
        if re.match(r".*ncbi.nlm.nih.gov/myncbi.*", args["<reference_file_or_URL>"]):
            tokenized_citations, reference_lines = webio.parse_myncbi_citations(args["<reference_file_or_URL>"], args["--verbose"])
        else:
            document_string = webio.get_text_from_url(args["<reference_file_or_URL>"])
            
            if not document_string:
                print("Nothing was read from the URL. Make sure the address is correct.")
                sys.exit()
            
            tokenized_citations, reference_lines = citation_parsing.parse_text_for_citations(document_string)
    else:
        # Check the file extension and call the correct read in function.
        extension = os.path.splitext(args["<reference_file_or_URL>"])[1][1:]
        if extension == "docx":
            document_string = fileio.read_text_from_docx(args["<reference_file_or_URL>"])
        elif extension == "txt":
            document_string = fileio.read_text_from_txt(args["<reference_file_or_URL>"])
        else:
            print("Unknown file type for reference file.")
            sys.exit()
    
        if not document_string:
            print("Nothing was read from the reference file. Make sure the file is not empty or is a supported file type.")
            sys.exit()
        
        if args["--MEDLINE_reference"]:
            tokenized_citations = citation_parsing.parse_MEDLINE_format(document_string)
            reference_lines = []
        else:
            tokenized_citations, reference_lines = citation_parsing.parse_text_for_citations(document_string)
            
    if not tokenized_citations:
        print("Warning: Could not tokenize any citations in provided reference. Check setup and formatting and try again.")
        sys.exit()
    
    ## Look for duplicates in citations.
    duplicate_citations = helper_functions.find_duplicate_citations(tokenized_citations)
    if duplicate_citations:
        print("Warning: The following citations in the reference file or URL appear to be duplicates based on identical DOI, PMID, or similar titles. They will only appear once in any outputs.")
        print("Duplicates:")
        for index_list in duplicate_citations:
            for index in index_list:
                if reference_lines:
                    pretty_print = reference_lines[index].split("\n")
                    pretty_print = " ".join([line.strip() for line in pretty_print])
                    print(pretty_print)
                else:
                    print(tokenized_citations[index]["title"])
                print()
            print("\n")
        
        indexes_to_remove = [index for duplicate_set in duplicate_citations for index in duplicate_set[1:]]
        
        tokenized_citations = [citation for count, citation in enumerate(tokenized_citations) if not count in indexes_to_remove]
        reference_lines = [citation for count, citation in enumerate(reference_lines) if not count in indexes_to_remove]
        
    
    print("Finding publications. This could take a while.")
    print("Searching PubMed.")
    PubMed_publication_dict, PubMed_matching_key_for_citation = ref_srch_webio.search_references_on_PubMed(tokenized_citations, config_dict["PubMed_search"]["PubMed_email"], args["--verbose"])
#    if not args["--no_GoogleScholar"]:
#        print("Searching Google Scholar.")
#        Google_Scholar_publication_dict, Google_Scholar_matching_key_for_citation = webio.search_references_on_Google_Scholar(tokenized_citations, config_dict["Crossref_search"]["Crossref_email"], args["--verbose"])
    if not args["--no_Crossref"]:
        print("Searching Crossref.")
        Crossref_publication_dict, Crossref_matching_key_for_citation = ref_srch_webio.search_references_on_Crossref(tokenized_citations, config_dict["Crossref_search"]["Crossref_email"], args["--verbose"])
    
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
            
    ## Compare citations to prev_pubs 
    is_citation_in_prev_pubs_list = []
    if has_previous_pubs:
        user_input_checking.prev_pubs_file_check(prev_pubs)
        is_citation_in_prev_pubs_list = helper_functions.compare_citations_with_list(tokenized_citations, prev_pubs)
        
    
    ## Build the save directory name.
    if args["--test"]:
        save_dir_name = "tracker-test-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
    else:
        save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
    
    if has_email_keys:
        email_messages = ref_srch_emails_and_reports.create_emails_dict(config_dict["project_descriptions"]["default"]["email_template"], publication_dict, matching_key_for_citation, is_citation_in_prev_pubs_list, reference_lines, tokenized_citations, config_dict["project_descriptions"]["default"])    
        ## save email messages to file
        fileio.save_emails_to_file(email_messages, save_dir_name)
                
        ## send emails
        if not args["--test"]:
            webio.send_emails(email_messages)
    
    ## Create report and save to file.
    fileio.save_reference_summary_report_to_file(config_dict["project_descriptions"]["default"]["report_ref_template"], publication_dict, matching_key_for_citation, is_citation_in_prev_pubs_list, reference_lines, tokenized_citations, save_dir_name)
    
    fileio.save_publications_to_file(save_dir_name, publication_dict, {})
    
    print("Success. Publications and reports saved in " + save_dir_name)



def PMID_reference(args):
    """Create a publications JSON file from a list of PMIDs.
    
    Args:
        args (dict): args from DocOpt CLI
    """
    
    user_input_checking.cli_inputs_check(args)
    
    ## read in config file
    config_dict = fileio.load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.config_file_check(config_dict)
    
    ## Check the DOI file extension and call the correct read in function.
    extension = os.path.splitext(args["<references_file>"])[1][1:]
    if extension == "docx":
        document_string = fileio.read_text_from_docx(args["<references_file>"])
    elif extension == "txt" or extension == "csv":
        document_string = fileio.read_text_from_txt(args["<references_file>"])
    else:
        print("Unknown file type for PMID file.")
        sys.exit()
    
    if not document_string:
        print("Nothing was read from the PMID file. Make sure the file is not empty or is a supported file type.")
        sys.exit()
        
    PMID_list = [line for line in document_string.split("\n") if line]
    print("Querying PubMed and building the publication list.")
    publication_dict = ref_srch_webio.build_pub_dict_from_PMID(PMID_list, config_dict["PubMed_search"]["PubMed_email"])
    
    ## Build the save directory name.
    if args["--test"]:
        save_dir_name = "tracker-test-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
    else:
        save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
    
    ## combine previous and new publications lists and save
    fileio.save_publications_to_file(save_dir_name, publication_dict, {})
    print("Success. Publications saved in " + save_dir_name)
    


def find_ORCID(args):
    """"""
    
    user_input_checking.cli_inputs_check(args)

    ## read in config file
    config_dict = fileio.load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.tracker_validate(config_dict, tracker_schema.ORCID_schema)
        
    ## Overwrite values in config_dict if command line options were used.
    ## Note the replacement is after checking both inputs and config_dict independently. If done before config_dict_check then CLI errors will dispaly as config_dict errors.
#    config_dict = helper_functions.overwrite_config_with_CLI(config_dict, args)
    
    old_authors_json = copy.deepcopy(config_dict["Authors"])
    
    print("Searching ORCID for author's ORCID ids.")
    config_dict["Authors"] = webio.search_ORCID_for_ids(config_dict["ORCID_search"]["ORCID_key"], config_dict["ORCID_search"]["ORCID_secret"], config_dict["Authors"])
    
    if old_authors_json != config_dict["Authors"]:
        ## Build the save directory name.
        if args["--test"]:
            save_dir_name = "tracker-test-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
            os.mkdir(save_dir_name)
        else:
            save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
            os.mkdir(save_dir_name)
    
        fileio.save_config_to_file(save_dir_name, config_dict)
        print("Success! configuration.json saved in " + save_dir_name)
    else:
        print("No authors were matched from the ORCID results. No new file saved.")



def find_Google_Scholar(args):
    """"""
    
    user_input_checking.cli_inputs_check(args)
    
    ## read in config file
    config_dict = fileio.load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.tracker_validate(config_dict, tracker_schema.PubMed_schema)
        
    old_authors_json = copy.deepcopy(config_dict["Authors"])
    
    print("Searching Google Scholar for author's scholar ids.")
    config_dict["Authors"] = webio.search_Google_Scholar_for_ids(config_dict["Authors"])
    
    if old_authors_json != config_dict["Authors"]:
        ## Build the save directory name.
        if args["--test"]:
            save_dir_name = "tracker-test-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
            os.mkdir(save_dir_name)
        else:
            save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
            os.mkdir(save_dir_name)
    
        fileio.save_config_to_file(save_dir_name, config_dict)
        print("Success! authors.json saved in " + save_dir_name)
    else:
        print("No authors were matched from the Google Scholar results. No new file saved.")



def create_author_JSON(args):
    """"""
    
    user_input_checking.cli_inputs_check(args)
    
    ## Check the file extension and call the correct read in function.
    extension = os.path.splitext(args["<author_file>"])[1][1:]
    if extension == "csv":
        document_string = fileio.read_text_from_txt(args["<author_file>"])
    else:
        print("Unknown file type for author file.")
        sys.exit()
    
    if not document_string:
        print("Nothing was read from the author file. Make sure the file is not empty or is a supported file type.")
        sys.exit()
        
    
    lines = document_string.split("\n")
    keys = lines.pop(0).split(",")
    if not "author_id" in keys:
        print("author_id is not a column in the author_file. It is required.")
        sys.exit()

               
                
if __name__ == "__main__":
    
    main()
