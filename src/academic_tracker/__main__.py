"""   
Usage:
    academic_tracker author_search <config_json_file> [--test --prev_pub=<file-path> --no_GoogleScholar --no_ORCID --no_Crossref --no_PubMed --verbose --silent]
    academic_tracker reference_search <config_json_file> <references_file_or_URL> [--test --prev_pub=<file-path> --PMID_reference --MEDLINE_reference --no_Crossref --no_PubMed --verbose --silent]
    academic_tracker find_ORCID <config_json_file> [--verbose --silent]
    academic_tracker find_Google_Scholar <config_json_file> [--verbose --silent]
    academic_tracker add_authors <config_json_file> <authors_file> [--verbose --silent]
    academic_tracker tokenize_reference <references_file_or_URL> [--MEDLINE_reference --verbose --silent]
    academic_tracker gen_reports_and_emails_auth <config_json_file> <publication_json_file> [--test --verbose --silent]
    academic_tracker gen_reports_and_emails_ref <config_json_file> <references_file_or_URL> <publication_json_file> [--test --prev_pub=<file-path> --MEDLINE_reference --verbose --silent]
    
Options:
    -h --help                         Show this screen.
    --version                         Show version.
    --verbose                         Print hidden error messages.
    --silent                          Do not print anything to the screen.
    --test                            Generate pubs and email texts, but do not send emails.
    --prev_pub=<file-path>            Filepath to json or csv with publication ids to ignore. Enter "ignore" for the <file_path> to not look for previous publications.json files in tracker directories.
    
Reference Type Options:    
    --PMID_reference                  Indicates that the reference_file is a PMID file and only PubMed info will be returned.
    --MEDLINE_reference               Indicates that the reference_file is a MEDLINE file.

Search Options:
    --no_GoogleScholar                Don't search Google Scholar.
    --no_ORCID                        Don't search ORCID.
    --no_Crossref                     Don't search Crossref.
    --no_PubMed                       Don't search PubMed.
"""


## Need help with pycharm UML diagram.
## add defulat pandas excel engine to required packages xlsxwriter I think

## take docs/_build  out of gitignore and point GitHub pages there for documentation.
## Add the url of this page to the about section on gitHub.
## When to merge to master?
## When to create github pages?
## Is BSD license okay?
## Putting on pypi? When?
## Does the lab have github actions for sphinx documentation? 


import re
import os
import datetime
import sys
import copy
import warnings

warnings.filterwarnings("ignore", module="fuzzywuzzy")

import docopt

from . import __version__
from . import fileio
from . import user_input_checking
from . import ref_srch_webio
from . import webio
from . import ref_srch_emails_and_reports
from . import tracker_schema
from . import athr_srch_modularized
from . import ref_srch_modularized
from . import helper_functions


VERBOSE = True
SILENT = False

def main():
    
    args = docopt.docopt(__doc__, version=str("Academic Tracker ") + __version__)
    
    user_input_checking.cli_inputs_check(args)
    
    global VERBOSE
    VERBOSE = args["--verbose"]
    global SILENT
    SILENT = args["--silent"]
    
    if len(sys.argv) > 1 and sys.argv[1] == "author_search":
        author_search(args["<config_json_file>"], args["--no_ORCID"], 
                      args["--no_GoogleScholar"], args["--no_Crossref"],
                      args["--no_PubMed"],
                      args["--test"], args["--prev_pub"])
    elif len(sys.argv) > 1 and sys.argv[1] == "reference_search":
        if args["--PMID_reference"]:
            PMID_reference(args["<config_json_file>"], args["<references_file_or_URL>"], args["--test"])
        else:
            reference_search(args["<config_json_file>"], args["<references_file_or_URL>"], 
                             args["--MEDLINE_reference"], args["--no_Crossref"], 
                             args["--no_PubMed"],
                             args["--test"], args["--prev_pub"])
    elif len(sys.argv) > 1 and sys.argv[1] == "find_ORCID":
        find_ORCID(args["<config_json_file>"])
    elif len(sys.argv) > 1 and sys.argv[1] == "find_Google_Scholar":
        find_Google_Scholar(args["<config_json_file>"])
    elif len(sys.argv) > 1 and sys.argv[1] == "add_authors":
        add_authors(args["<config_json_file>"], args["<authors_file>"])
    elif len(sys.argv) > 1 and sys.argv[1] == "tokenize_reference":
        tokenize_reference(args["<references_file_or_URL>"], args["--MEDLINE_reference"])
    elif len(sys.argv) > 1 and sys.argv[1] == "gen_reports_and_emails_auth":
        gen_reports_and_emails_auth(args["<config_json_file>"], args["<publication_json_file>"], args["--test"])
    elif len(sys.argv) > 1 and sys.argv[1] == "gen_reports_and_emails_ref":
        gen_reports_and_emails_ref(args["<config_json_file>"], args["<references_file_or_URL>"], 
                                   args["<publication_json_file>"], args["--MEDLINE_reference"], 
                                   args["--test"], args["--prev_pub"])
    else:
        print("Unrecognized command")  
        


def author_search(config_json_filepath, no_ORCID, no_GoogleScholar, no_Crossref, no_PubMed, test, prev_pub_filepath):
    """Query sources for publications by author.
    
    Reads in the JSON config file, previous publications JSON file, and checks for errors.
    Then searches PubMed, ORCID, Google Scholar, and Crossref for publications for each author.
    Emails are then created and sent to project leaders or individual authors. Emails and
    publications are saved to file and emails are sent depending on the options entered by the user. 
    See the program docstring for options details.
    
    Args:
        config_json_filepath (str): filepath to the configuration JSON.
        no_ORCID (bool): If True search ORCID else don't. Reduces checking on config JSON if True.
        no_GoogleScholar (bool): if True search Google Scholar else don't. Reduces checking on config JSON if True.
        no_Crossref (bool): If True search Crossref else don't. Reduces checking on config JSON if True.
        no_PubMed (bool): If True search PubMed else don't. Reduces checking on config JSON if True.
        test (bool): If True save_dir_name is tracker-test instead of tracker- and emails are not sent.
        prev_pub_filepath (str or None): filepath to the publication JSON to read in.
    """
    
    config_dict = athr_srch_modularized.input_reading_and_checking(config_json_filepath, no_ORCID, no_GoogleScholar, no_Crossref, no_PubMed)
    
    ## Create an authors_json for each project in the config_dict and update those authors attributes with the project attributes.
    authors_by_project_dict, config_dict = athr_srch_modularized.generate_internal_data_and_check_authors(config_dict)
                
    ## read in previous publications to ignore
    has_previous_pubs, prev_pubs = fileio.read_previous_publications(prev_pub_filepath)
    if has_previous_pubs:
        user_input_checking.prev_pubs_file_check(prev_pubs)
            
    ## Query sources and build publication_dict.
<<<<<<< Updated upstream:academic_tracker/__main__.py
    publication_dict, prev_pubs = athr_srch_modularized.build_publication_dict(config_dict, prev_pubs, no_ORCID, no_GoogleScholar, no_Crossref)            
=======
    publication_dict = athr_srch_modularized.build_publication_dict(config_dict, prev_pubs, no_ORCID, no_GoogleScholar, no_Crossref, no_PubMed)            
>>>>>>> Stashed changes:src/academic_tracker/__main__.py
    
    save_dir_name = athr_srch_modularized.save_and_send_reports_and_emails(authors_by_project_dict, publication_dict, config_dict, test)
    
    ## combine previous and new publications lists and save
    fileio.save_publications_to_file(save_dir_name, publication_dict, prev_pubs)
    
    helper_functions.vprint("Success. Publications, reports, and emails saved in " + save_dir_name)



def reference_search(config_json_filepath, ref_path_or_URL, MEDLINE_reference, no_Crossref, no_PubMed, test, prev_pub_filepath):
    """Query PubMed and Crossref for publications matching a reference.
    
    Read in user inputs and check for error, query sources based on inputs, build 
    emails and reports, save emails, reports, and publications.
    
    Args:
        config_json_filepath (str): filepath to the configuration JSON.
        ref_path_or_URL (str): either a filepath to file to tokenize or a URL to tokenize.
        MEDLINE_reference (bool): If True re_path_or_URL is a filepath to a MEDLINE formatted file.
        no_Crossref (bool): If True search Crossref else don't. Reduces checking on config JSON if True.
        no_PubMed (bool): If True search PubMed else don't. Reduces checking on config JSON if True.
        test (bool): If True save_dir_name is tracker-test instead of tracker- and emails are not sent.
        prev_pub_filepath (str or None): filepath to the publication JSON to read in.
    """
    
    config_dict, tokenized_citations, has_previous_pubs, prev_pubs = ref_srch_modularized.input_reading_and_checking(config_json_filepath, ref_path_or_URL, MEDLINE_reference, no_Crossref, no_PubMed, prev_pub_filepath)       

    publication_dict, tokenized_citations = ref_srch_modularized.build_publication_dict(config_dict, tokenized_citations, no_Crossref, no_PubMed)
            
    save_dir_name = ref_srch_modularized.save_and_send_reports_and_emails(config_dict, tokenized_citations, publication_dict, prev_pubs, has_previous_pubs, test)
            
    fileio.save_publications_to_file(save_dir_name, publication_dict, {})
    fileio.save_json_to_file(save_dir_name, "tokenized_reference.json", tokenized_citations)
    
    helper_functions.vprint("Success. Publications and reports saved in " + save_dir_name)



def PMID_reference(config_json_filepath, ref_path_or_URL, test):
    """Query PubMed to create a publications JSON file from a list of PMIDs.
    
    Args:
        config_json_filepath (str): filepath to the configuration JSON.
        ref_path_or_URL (str): either a filepath to file to tokenize or a URL to tokenize.
        test (bool): If True save_dir_name is tracker-test instead of tracker- and emails are not sent.
    """
    
    ## read in config file
    config_dict = fileio.load_json(config_json_filepath)
    
    ## Get inputs from config file and check them for errors.
<<<<<<< Updated upstream:academic_tracker/__main__.py
    user_input_checking.ref_config_file_check(config_dict, True)
=======
    user_input_checking.ref_config_file_check(config_dict, True, False)
    user_input_checking.config_report_check(config_dict)
>>>>>>> Stashed changes:src/academic_tracker/__main__.py
    
    ## Check the DOI file extension and call the correct read in function.
    extension = os.path.splitext(ref_path_or_URL)[1][1:].lower()
    if extension == "docx":
        file_contents = fileio.read_text_from_docx(ref_path_or_URL)
    elif extension == "txt":
        file_contents = fileio.read_text_from_txt(ref_path_or_URL)
    elif extension == "json":
        file_contents = fileio.load_json(ref_path_or_URL)
    else:
        helper_functions.vprint("Unknown file type for PMID file.")
        sys.exit()
    
    if not file_contents:
        helper_functions.vprint("Nothing was read from the PMID file. Make sure the file is not empty or is a supported file type.")
        sys.exit()
    
    if type(file_contents) == str:
        PMID_list = [line for line in file_contents.split("\n") if line]
    else:
        PMID_list = file_contents
    user_input_checking.tracker_validate(PMID_list, tracker_schema.PMID_reference_schema)
    
    helper_functions.vprint("Querying PubMed and building the publication list.")
    publication_dict = ref_srch_webio.build_pub_dict_from_PMID(PMID_list, config_dict["PubMed_search"]["PubMed_email"])
    
    ## Build the save directory name.
    if test:
        save_dir_name = "tracker-test-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
    else:
        save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
    
    ## combine previous and new publications lists and save
    fileio.save_publications_to_file(save_dir_name, publication_dict, {})
    helper_functions.vprint("Success. Publications saved in " + save_dir_name)
    


def find_ORCID(config_json_filepath):
    """Query ORCID to find ORCID IDs for authors.
    
    Args:
        config_json_filepath (str): filepath to the configuration JSON.
    """
    
    ## read in config file
    config_dict = fileio.load_json(config_json_filepath)
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.tracker_validate(config_dict, tracker_schema.ORCID_schema)
            
    old_authors_json = copy.deepcopy(config_dict["Authors"])
    
    helper_functions.vprint("Searching ORCID for author's ORCID ids.")
    config_dict["Authors"] = webio.search_ORCID_for_ids(config_dict["ORCID_search"]["ORCID_key"], config_dict["ORCID_search"]["ORCID_secret"], config_dict["Authors"])
    
    if old_authors_json != config_dict["Authors"]:
        ## Build the save directory name.
        save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
    
        fileio.save_json_to_file(save_dir_name, "configuration.json", config_dict)
        helper_functions.vprint("Success! configuration.json saved in " + save_dir_name)
    else:
        helper_functions.vprint("No authors were matched from the ORCID results. No new file saved.")



def find_Google_Scholar(config_json_filepath):
    """Query Google Scholar to find Scholar IDs for authors.
    
    Args:
        config_json_filepath (str): filepath to the configuration JSON.
    """
    
    ## read in config file
    config_dict = fileio.load_json(config_json_filepath)
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.tracker_validate(config_dict, tracker_schema.Authors_schema)
        
    old_authors_json = copy.deepcopy(config_dict["Authors"])
    
    helper_functions.vprint("Searching Google Scholar for author's scholar ids.")
    config_dict["Authors"] = webio.search_Google_Scholar_for_ids(config_dict["Authors"])
    
    if old_authors_json != config_dict["Authors"]:
        ## Build the save directory name.
        save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
    
        fileio.save_json_to_file(save_dir_name, "configuration.json", config_dict)
        helper_functions.vprint("Success! configuration.json saved in " + save_dir_name)
    else:
        helper_functions.vprint("No authors were matched from the Google Scholar results. No new file saved.")



def add_authors(config_json_filepath, authors_filepath):
    """Add authors from csv to config JSON.
    
    Args:
        config_json_filepath (str): filepath to the configuration JSON.
        authors_filepath (str): filepath to the csv file with authors to add or modify.
    """
    
    ## read in config file
    config_dict = fileio.load_json(config_json_filepath)
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.tracker_validate(config_dict, tracker_schema.Authors_schema)
    
    ## Check the file extension and call the correct read in function.
    extension = os.path.splitext(authors_filepath)[1][1:]
    if extension == "csv":
        df = fileio.read_csv(authors_filepath)
    else:
        helper_functions.vprint("Unknown file type for author file.")
        sys.exit()
            
    
    required_columns = tracker_schema.config_schema["properties"]["Authors"]["additionalProperties"]["required"] + ["author_id"]
    missing_required = [column for column in required_columns if column not in df.columns]
    if missing_required:
        helper_functions.vprint("Error: The following columns are required but are missing:\n" + "\n".join(missing_required))
        sys.exit()
        
    missing_values = [column for column in required_columns if df.loc[:, column].isnull().values.any()]
    if missing_values:
        helper_functions.vprint("Error: The following columns have null values:\n" + "\n".join(missing_values))
        sys.exit()
    
    for column in required_columns:
        df.loc[:, column] = df.loc[:, column].astype(str)
    
    ## Assuming all list types are string lists.
    author_keys = tracker_schema.config_schema["properties"]["Authors"]["additionalProperties"]["properties"]
    list_type_keys = [key for key in author_keys if "type" in author_keys[key] and author_keys[key]["type"] == "array"]
    for key in list_type_keys:
        if key in df.columns:
            df.loc[:, key] = df.loc[:, key].astype(str)
            df.loc[:, key] = df.loc[:, key].apply(lambda x: x.split(","))
    
    df.index = df.loc[:, "author_id"]
    df = df.drop(["author_id"], axis=1)
    authors_dict = df.to_dict("index")
    config_dict["Authors"].update(authors_dict)
    
    save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
    os.mkdir(save_dir_name)

    fileio.save_json_to_file(save_dir_name, "configuration.json", config_dict)
    helper_functions.vprint("Success! configuration.json saved in " + save_dir_name)
    
  
    
def tokenize_reference(ref_path_or_URL, MEDLINE_reference):
    """Tokenize input reference file.
    
    Args:
        ref_path_or_URL (str): either a filepath to file to tokenize or a URL to tokenize.
    """
    
    tokenized_citations = ref_srch_webio.tokenize_reference_input(ref_path_or_URL, MEDLINE_reference)
    
    report_string = ref_srch_emails_and_reports.create_tokenization_report(tokenized_citations)
    
    save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
    os.mkdir(save_dir_name)
        
    fileio.save_string_to_file(save_dir_name, "tokenization_report.txt", report_string)
            
    fileio.save_json_to_file(save_dir_name, "tokenized_reference.json", tokenized_citations)
    
    helper_functions.vprint("Success! Tokenization files saved in " + save_dir_name)
    


def gen_reports_and_emails_auth(config_json_filepath, publication_json_filepath, test):
    """Generate reports and emails for input publications as if author_search was ran.
    
    Args:
        config_json_filepath (str): filepath to the configuration JSON.
        publication_json_filepath (str): filepath to the publication JSON to read in.
        test (bool): If True save_dir_name is tracker-test instead of tracker- and emails are not sent.
    """
    
    config_dict = fileio.load_json(config_json_filepath)
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.tracker_validate(config_dict, tracker_schema.gen_reports_auth_schema)
    
    ## Create an authors_json for each project in the config_dict and update those authors attributes with the project attributes.
    authors_by_project_dict, config_dict = athr_srch_modularized.generate_internal_data_and_check_authors(config_dict)
    
    ## Read in publications.json
    publication_dict = fileio.load_json(publication_json_filepath)
    user_input_checking.prev_pubs_file_check(publication_dict)
                
    
    save_dir_name = athr_srch_modularized.save_and_send_reports_and_emails(authors_by_project_dict, publication_dict, config_dict, test)
    
    helper_functions.vprint("Success! Reports and emails saved in " + save_dir_name)
    
    


def gen_reports_and_emails_ref(config_json_filepath, ref_path_or_URL, publication_json_filepath, MEDLINE_reference, test, prev_pub_filepath):
    """Generate reports and emails for input publications and reference as if reference_search was ran.
    
    Args:
        config_json_filepath (str): filepath to the configuration JSON.
        ref_path_or_URL (str): either a filepath to file to tokenize or a URL to tokenize.
        publication_json_filepath (str): filepath to the publication JSON to read in.
        MEDLINE_reference (bool): If True re_path_or_URL is a filepath to a MEDLINE formatted file.
        test (bool): If True save_dir_name is tracker-test instead of tracker- and emails are not sent.
        prev_pub_filepath (str or None): filepath to the publication JSON to read in.
    """
    
    ## read in config file
    config_dict = fileio.load_json(config_json_filepath)
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.tracker_validate(config_dict, tracker_schema.gen_reports_ref_schema)
    
    if not prev_pub_filepath or prev_pub_filepath.lower() == "ignore":
        prev_pubs = {}
        has_previous_pubs = False
    else:
        prev_pubs = fileio.load_json(prev_pub_filepath)
        has_previous_pubs = True
    
    if has_previous_pubs:
        user_input_checking.prev_pubs_file_check(prev_pubs)
        
    tokenized_citations = ref_srch_webio.tokenize_reference_input(ref_path_or_URL, MEDLINE_reference) 
    ## Read in publications.json
    publication_dict = fileio.load_json(publication_json_filepath)
    user_input_checking.prev_pubs_file_check(publication_dict)
    
    pub_titles_to_keys = {pub["title"]:pub_id  for pub_id, pub in publication_dict.items() if pub["title"]}
    pub_titles = list(pub_titles_to_keys.keys())
    
    matching_key_for_citation = []
    for citation in tokenized_citations:
        if not citation["pub_dict_key"] or not citation["pub_dict_key"] in publication_dict:
            if citation["DOI"] and webio.DOI_URL + citation["DOI"] in publication_dict:
                citation["pub_dict_key"] = webio.DOI_URL + citation["DOI"]
                matching_key_for_citation.append(webio.DOI_URL + citation["DOI"])
            elif citation["PMID"] and citation["PMID"] in publication_dict:
                citation["pub_dict_key"] = citation["PMID"]
                matching_key_for_citation.append(citation["PMID"])
            elif citation["title"]:
                matches = helper_functions.fuzzy_matches_to_list(citation["title"], pub_titles)
                if matches:    
                    citation["pub_dict_key"] = pub_titles_to_keys[pub_titles[matches[0][0]]]
                    matching_key_for_citation.append(pub_titles_to_keys[pub_titles[matches[0][0]]])
        else:
            matching_key_for_citation.append(citation["pub_dict_key"])
            
    for key in list(publication_dict.keys()):
        if not key in matching_key_for_citation:
            del publication_dict[key]
            
    if not publication_dict:
        helper_functions.vprint("Error: No entries in the publication JSON matched any reference in the provided reference.")
        sys.exit()
            
    
    save_dir_name = ref_srch_modularized.save_and_send_reports_and_emails(config_dict, tokenized_citations, publication_dict, prev_pubs, has_previous_pubs, test)
    
    fileio.save_json_to_file(save_dir_name, "tokenized_reference.json", tokenized_citations)
    
    helper_functions.vprint("Success! Reports and emails saved in " + save_dir_name)


               
                
if __name__ == "__main__":
    
    main()
