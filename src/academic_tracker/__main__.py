"""
Usage:
    academic_tracker author_search <config_json_file> [--test] 
                                                      [--prev_pub=<file-path> --prev-pub=<file-path>] 
                                                      [--save-all-queries]
                                                      [--no-GoogleScholar --no_GoogleScholar] 
                                                      [--no-ORCID --no_ORCID] 
                                                      [--no-Crossref --no_Crossref] 
                                                      [--no-PubMed --no_PubMed]
                                                      [--verbose --silent]
    academic_tracker reference_search <config_json_file> <references_file_or_URL> [--test] 
                                                                                  [--prev-pub=<file-path> --prev_pub=<file-path>]
                                                                                  [--save-all-queries]
                                                                                  [--PMID-reference --PMID_reference]
                                                                                  [--MEDLINE-reference --MEDLINE_reference]
                                                                                  [--keep-duplicates]
                                                                                  [--no-Crossref --no_Crossref]
                                                                                  [--no-PubMed --no_PubMed]
                                                                                  [--verbose --silent]
    academic_tracker find_ORCID <config_json_file> [--verbose --silent]
    academic_tracker find_Google_Scholar <config_json_file> [--verbose --silent]
    academic_tracker add_authors <config_json_file> <authors_file> [--verbose --silent]
    academic_tracker tokenize_reference <references_file_or_URL> [--MEDLINE-reference --MEDLINE_reference]
                                                                 [--keep-duplicates]
                                                                 [--verbose --silent]
    academic_tracker gen_reports_and_emails_auth <config_json_file> <publication_json_file> [--test --verbose --silent]
    academic_tracker gen_reports_and_emails_ref <config_json_file> <references_file_or_URL> <publication_json_file> [--test]
                                                                                                                    [--prev-pub=<file-path> --prev_pub=<file-path>]
                                                                                                                    [--MEDLINE-reference --MEDLINE_reference]
                                                                                                                    [--keep-duplicates]
                                                                                                                    [--verbose --silent]
    
Options:
    -h --help                         Show this screen.
    -v --version                      Show version.
    --verbose                         Print hidden error messages.
    --silent                          Do not print anything to the screen.
    --test                            Generate pubs and email texts, but do not send emails.
    --prev-pub=<file-path>            Filepath to json or csv with publication ids to ignore. 
                                      Enter "ignore" for the <file_path> to not look for previous publications.json files in tracker directories.
    --prev_pub=<file-path>            Deprecated. Use --prev-pub instead.
    --save-all-queries                Save all queried results from each source in "all_results.json".
    --keep-duplicates                 After references are tokenized duplicate entries are removed, use this option not to remove duplicate entries.
    
Reference Type Options:    
    --PMID-reference                  Indicates that the reference_file is a PMID file and only PubMed info will be returned.
    --PMID_reference                  Deprecated. Use --PMID-reference instead.
    --MEDLINE-reference               Indicates that the reference_file is a MEDLINE file.
    --MEDLINE_reference               Deprecated. Use --MEDLINE-reference instead.

Search Options:
    --no-GoogleScholar                Don't search Google Scholar.
    --no_GoogleScholar                Deprecated. Use --no-GoogleScholar instead.
    --no-ORCID                        Don't search ORCID.
    --no_ORCID                        Deprecated. Use --no-ORCID instead.
    --no-Crossref                     Don't search Crossref.
    --no_Crossref                     Deprecated. Use --no-Crossref instead.
    --no-PubMed                       Don't search PubMed.
    --no_PubMed                       Deprecated. Use --no-PubMed instead.
"""


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

## TODO a
## Make sure in documentation that author affiliation is said to be a newline separated list, was comma, but had to change to match PubMed.
## Change ref and author search to be aware of collective authors, tokenized citations needs to change.
## In the tests for reporting, are the tests using a version of the publication dict that has author affiliations separated with newlines?

def main():
    
    ## Have to modify the doc string so docopt can recognize more options than what is written.
    # options_to_alias = ["--no-PubMed", "--no-ORCID", "--no-Crossref", "--no-GoogleScholar", "--PMID-reference", "--MEDLINE-reference", "--prev-pub"]
    # for option in options_to_alias:
    #     alias = f"--{option[2:].replace('-', '_')}"
    #     doc = __doc__.replace("option", f"{option} {alias}")
        
    # args = docopt.docopt(doc, version=str("Academic Tracker ") + __version__)
    
    args = docopt.docopt(__doc__, version=str("Academic Tracker ") + __version__)
    
    user_input_checking.cli_inputs_check(args)
    
    global VERBOSE
    VERBOSE = args["--verbose"]
    global SILENT
    SILENT = args["--silent"]
    
    if len(sys.argv) > 1 and sys.argv[1] == "author_search":
        author_search(args["<config_json_file>"], 
                      args["--no_ORCID"] or args["--no-ORCID"], 
                      args["--no_GoogleScholar"] or args["--no-GoogleScholar"], 
                      args["--no_Crossref"] or args["--no-Crossref"],
                      args["--no_PubMed"] or args["--no-PubMed"],
                      args["--test"], 
                      args["--prev-pub"] if args["--prev-pub"] else args["--prev_pub"],
                      args["--save-all-queries"])
    elif len(sys.argv) > 1 and sys.argv[1] == "reference_search":
        if args["--PMID_reference"] or args["--PMID-reference"]:
            PMID_reference(args["<config_json_file>"], args["<references_file_or_URL>"], args["--test"])
        else:
            reference_search(args["<config_json_file>"], 
                             args["<references_file_or_URL>"], 
                             args["--MEDLINE_reference"] or args["--MEDLINE-reference"], 
                             args["--no_Crossref"] or args["--no-Crossref"], 
                             args["--no_PubMed"] or args["--no-PubMed"],
                             args["--test"], 
                             args["--prev-pub"] if args["--prev-pub"] else args["--prev_pub"],
                             args["--save-all-queries"],
                             not args["--keep-duplicates"])
    elif len(sys.argv) > 1 and sys.argv[1] == "find_ORCID":
        find_ORCID(args["<config_json_file>"])
    elif len(sys.argv) > 1 and sys.argv[1] == "find_Google_Scholar":
        find_Google_Scholar(args["<config_json_file>"])
    elif len(sys.argv) > 1 and sys.argv[1] == "add_authors":
        add_authors(args["<config_json_file>"], args["<authors_file>"])
    elif len(sys.argv) > 1 and sys.argv[1] == "tokenize_reference":
        tokenize_reference(args["<references_file_or_URL>"], 
                           args["--MEDLINE_reference"] or args["--MEDLINE-reference"],
                           not args["--keep-duplicates"])
    elif len(sys.argv) > 1 and sys.argv[1] == "gen_reports_and_emails_auth":
        gen_reports_and_emails_auth(args["<config_json_file>"], args["<publication_json_file>"], args["--test"])
    elif len(sys.argv) > 1 and sys.argv[1] == "gen_reports_and_emails_ref":
        gen_reports_and_emails_ref(args["<config_json_file>"], 
                                   args["<references_file_or_URL>"], 
                                   args["<publication_json_file>"], 
                                   args["--MEDLINE_reference"] or args["--MEDLINE-reference"], 
                                   args["--test"], 
                                   args["--prev-pub"] if args["--prev-pub"] else args["--prev_pub"],
                                   not args["--keep-duplicates"])
    else:
        print("Unrecognized command")  
        


def author_search(config_json_filepath, no_ORCID, no_GoogleScholar, no_Crossref, no_PubMed, 
                  test, prev_pub_filepath, save_all_results):
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
        save_all_results (bool): if True, save all of the queried publications from each source as "all_results.json"
    """
    
    config_dict = athr_srch_modularized.input_reading_and_checking(config_json_filepath, no_ORCID, no_GoogleScholar, 
                                                                   no_Crossref, no_PubMed)
    
    ## Create an authors_json for each project in the config_dict and update those authors attributes with the project attributes.
    authors_by_project_dict, config_dict = athr_srch_modularized.generate_internal_data_and_check_authors(config_dict)
                
    ## read in previous publications to ignore
    has_previous_pubs, prev_pubs = fileio.read_previous_publications(prev_pub_filepath)
    if has_previous_pubs:
        user_input_checking.prev_pubs_file_check(prev_pubs)
            
    ## Query sources and build publication_dict.
    publication_dict, all_queries = athr_srch_modularized.build_publication_dict(config_dict, prev_pubs, no_ORCID, no_GoogleScholar, no_Crossref, no_PubMed)            
    
    save_dir_name = athr_srch_modularized.save_and_send_reports_and_emails(authors_by_project_dict, publication_dict, config_dict, test)
    
    ## combine previous and new publications lists and save
    fileio.save_publications_to_file(save_dir_name, publication_dict, prev_pubs)
    
    if save_all_results:
        fileio.save_json_to_file(save_dir_name, "all_results.json", all_queries)
    
    helper_functions.vprint("Success. Publications, reports, and emails saved in " + save_dir_name)



def reference_search(config_json_filepath, ref_path_or_URL, MEDLINE_reference, no_Crossref, no_PubMed, 
                     test, prev_pub_filepath, save_all_results, remove_duplicates):
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
        save_all_results (bool): if True, save all of the queried publications from each source as "all_results.json".
        remove_duplicates (bool): if True, remove duplicate entries in tokenized citations.
    """
    
    config_dict, tokenized_citations, has_previous_pubs, prev_pubs = \
        ref_srch_modularized.input_reading_and_checking(config_json_filepath, ref_path_or_URL, 
                                                        MEDLINE_reference, no_Crossref, no_PubMed, 
                                                        prev_pub_filepath,
                                                        remove_duplicates)       

    publication_dict, tokenized_citations, all_queries = ref_srch_modularized.build_publication_dict(config_dict, tokenized_citations, no_Crossref, no_PubMed)
            
    save_dir_name = ref_srch_modularized.save_and_send_reports_and_emails(config_dict, tokenized_citations, publication_dict, prev_pubs, has_previous_pubs, test)
            
    fileio.save_publications_to_file(save_dir_name, publication_dict, {})
    fileio.save_json_to_file(save_dir_name, "tokenized_reference.json", tokenized_citations)
    
    if save_all_results:
        fileio.save_json_to_file(save_dir_name, "all_results.json", all_queries)
    
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
    user_input_checking.ref_config_file_check(config_dict, True, False)
    user_input_checking.config_report_check(config_dict)
    
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
    
    PMID_list = [line for line in file_contents.split("\n") if line] if type(file_contents) == str else file_contents
    
    user_input_checking.tracker_validate(PMID_list, tracker_schema.PMID_reference_schema)
    
    helper_functions.vprint("Querying PubMed and building the publication list.")
    publication_dict = ref_srch_webio.build_pub_dict_from_PMID(PMID_list, config_dict["PubMed_search"]["PubMed_email"])
    
    ## Build the save directory name.
    if test:
        save_dir_name = "tracker-test-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
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
        
    
    if "first_name" in df.columns and not "last_name" in df.columns:
        helper_functions.vprint("Error: There is a 'first_name' column without a matching 'last_name' column.")
        sys.exit()
    
    if "last_name" in df.columns and not "first_name" in df.columns:
        helper_functions.vprint("Error: There is a 'last_name' column without a matching 'first_name' column.")
        sys.exit()
    
    if not "last_name" in df.columns and not "first_name" in df.columns and not "collective_name" in df.columns:
        helper_functions.vprint("Error: There must be either a 'collective_name' column or 'first_name' and 'last_name' columns.")
        sys.exit()
        
    
    if not "collective_name" in df.columns: 
        missing_first_or_last_names = df.loc[:, ["first_name", "last_name"]].isnull().any(axis=1)
        missing_names_indexes = missing_first_or_last_names[missing_first_or_last_names==True].index.values
    else:
        missing_collective_names = df.loc[:, "collective_name"].isnull()
        if "first_name" in df.columns and "last_name" in df.columns:
            missing_first_or_last_names = df.loc[:, ["first_name", "last_name"]].isnull().any(axis=1)
            missing_names = missing_collective_names & missing_first_or_last_names
            missing_names_indexes = missing_names[missing_names==True].index.values
        else:
            missing_names_indexes = missing_collective_names[missing_collective_names==True].index.values
        
    if len(missing_names_indexes) > 0:
        message = ("Error: The following rows have incomplete name columns:\n" +
                   "\n".join([str(index+1) for index in missing_names_indexes]) +
                   "\nEach row must have values in either the 'collective_name' column "
                   "or the 'first_name' and 'last_name' columns.")
        helper_functions.vprint(message)
        sys.exit()
        
        
    
    for column in required_columns:
        df.loc[:, column] = df.loc[:, column].astype(str)
    
    ## Assuming all list types are string lists.
    author_keys = tracker_schema.config_schema["properties"]["Authors"]["additionalProperties"]["properties"]
    list_type_keys = [key for key in author_keys if "type" in author_keys[key] and author_keys[key]["type"] == "array"]
    author_keys = tracker_schema.config_schema["properties"]["Authors"]["additionalProperties"]["then"]["properties"]
    list_type_keys += [key for key in author_keys if "type" in author_keys[key] and author_keys[key]["type"] == "array"]
    author_keys = tracker_schema.config_schema["properties"]["Authors"]["additionalProperties"]["else"]["properties"]
    list_type_keys += [key for key in author_keys if "type" in author_keys[key] and author_keys[key]["type"] == "array"]
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

    fileio.save_json_to_file(save_dir_name, "configuration.json", config_dict, False)
    helper_functions.vprint("Success! configuration.json saved in " + save_dir_name)
    
  
    
def tokenize_reference(ref_path_or_URL, MEDLINE_reference, remove_duplicates):
    """Tokenize input reference file.
    
    Args:
        ref_path_or_URL (str): either a filepath to file to tokenize or a URL to tokenize.
        MEDLINE_reference (bool): True indicates that ref_path_or_URL is in MEDLINE format.
        remove_duplicates (bool): if True, remove duplicate entries in tokenized citations.
    """
    
    tokenized_citations = ref_srch_webio.tokenize_reference_input(ref_path_or_URL, MEDLINE_reference, remove_duplicates)
    
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
    user_input_checking.config_report_check(config_dict)
    
    ## Create an authors_json for each project in the config_dict and update those authors attributes with the project attributes.
    authors_by_project_dict, config_dict = athr_srch_modularized.generate_internal_data_and_check_authors(config_dict)
    
    ## Read in publications.json
    publication_dict = fileio.load_json(publication_json_filepath)
    user_input_checking.prev_pubs_file_check(publication_dict)
                
    
    save_dir_name = athr_srch_modularized.save_and_send_reports_and_emails(authors_by_project_dict, publication_dict, config_dict, test)
    
    helper_functions.vprint("Success! Reports and emails saved in " + save_dir_name)
    
    


def gen_reports_and_emails_ref(config_json_filepath, 
                               ref_path_or_URL, 
                               publication_json_filepath, 
                               MEDLINE_reference, 
                               test, 
                               prev_pub_filepath,
                               remove_duplicates):
    """Generate reports and emails for input publications and reference as if reference_search was ran.
    
    Args:
        config_json_filepath (str): filepath to the configuration JSON.
        ref_path_or_URL (str): either a filepath to file to tokenize or a URL to tokenize.
        publication_json_filepath (str): filepath to the publication JSON to read in.
        MEDLINE_reference (bool): If True re_path_or_URL is a filepath to a MEDLINE formatted file.
        test (bool): If True save_dir_name is tracker-test instead of tracker- and emails are not sent.
        prev_pub_filepath (str or None): filepath to the publication JSON to read in.
        remove_duplicates (bool): if True, remove duplicate entries in tokenized citations.
    """
    
    ## read in config file
    config_dict = fileio.load_json(config_json_filepath)
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.tracker_validate(config_dict, tracker_schema.gen_reports_ref_schema)
    user_input_checking.config_report_check(config_dict)
    
    if not prev_pub_filepath or prev_pub_filepath.lower() == "ignore":
        prev_pubs = {}
        has_previous_pubs = False
    else:
        prev_pubs = fileio.load_json(prev_pub_filepath)
        has_previous_pubs = True
    
    if has_previous_pubs:
        user_input_checking.prev_pubs_file_check(prev_pubs)
        
    tokenized_citations = ref_srch_webio.tokenize_reference_input(ref_path_or_URL, MEDLINE_reference, remove_duplicates) 
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
