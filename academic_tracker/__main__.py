"""   
Usage:
    academic_tracker author_search <config_json_file> [--test --prev_pub=<file-path> --no_GoogleScholar --no_ORCID --no_Crossref]
    academic_tracker reference_search <config_json_file> <references_file_or_URL> [--test --prev_pub=<file-path> --PMID_reference --MEDLINE_reference --no_Crossref]
    academic_tracker find_ORCID <config_json_file> 
    academic_tracker find_Google_Scholar <config_json_file>  
    academic_tracker add_authors <config_json_file> <authors_file> 
    academic_tracker tokenize_reference <references_file_or_URL> 
    academic_tracker gen_reports_and_emails_auth <config_json_file> <publication_json_file> [--test]
    academic_tracker gen_reports_and_emails_ref <config_json_file> <references_file_or_URL> <publication_json_file> [--test --prev_pub=<file-path> --MEDLINE_reference]
    
Options:
    -h --help                         Show this screen.
    --version                         Show version.
    --verbose                         Print hidden error messages.
    --test                            Generate pubs and email texts, but do not send emails.
    --prev_pub=<file-path>            Filepath to json or csv with publication ids to ignore. Enter "ignore" for the <file_path> to not look for previous publications.json files in tracker directories.
    
Reference Type Options:    
    --PMID_reference                  Indicates that the reference_file is a PMID file and only PubMed info will be returned.
    --MEDLINE_reference               Indicates that the reference_file is a MEDLINE file.

Search Options:
    --no_GoogleScholar                Don't search Google Scholar.
    --no_ORCID                        Don't search ORCID.
    --no_Crossref                     Don't search Crossref.
"""


## In documentation add a section about how citations are matched, ie one author with matching last name and fuzzy title match > 90.
## In documentation make sure to mention that gen_reports for ref tries to match pub_dict keys in reference if not in reference.
## Should email be required for authors? Should project report still have option to make one for each author and emailed? If no then change the code that generates reports so author_first and author_last aren't available outside of author_loop.
## Still want default report template? If we do default then user can't turn off generating them.

## Less important or far future things:
## TODO improve reference search to see if every author on the pub has the pub associated with them on ORCID
## TODO add functionality to more easily handle verbose option, and add more messages when it is in use.



import re
import os
import datetime
import sys
import copy

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
    elif len(sys.argv) > 1 and sys.argv[1] == "add_authors":
        add_authors(args)
    elif len(sys.argv) > 1 and sys.argv[1] == "tokenize_reference":
        tokenize_reference(args)
    elif len(sys.argv) > 1 and sys.argv[1] == "gen_reports_and_emails_auth":
        gen_reports_and_emails_auth(args)
    elif len(sys.argv) > 1 and sys.argv[1] == "gen_reports_and_emails_ref":
        gen_reports_and_emails_ref(args)
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
    
    config_dict = athr_srch_modularized.input_reading_and_checking(args)
    
    ## Create an authors_json for each project in the config_dict and update those authors attributes with the project attributes.
    authors_by_project_dict, config_dict = athr_srch_modularized.generate_internal_data_and_check_authors(args, config_dict)
                
    ## read in previous publications to ignore
    has_previous_pubs, prev_pubs = fileio.read_previous_publications(args)
    if has_previous_pubs:
        user_input_checking.prev_pubs_file_check(prev_pubs)
            
    ## Query sources and build publication_dict.
    publication_dict, prev_pubs = athr_srch_modularized.build_publication_dict(args, config_dict, prev_pubs)            
    
    save_dir_name = athr_srch_modularized.save_and_send_reports_and_emails(args, authors_by_project_dict, publication_dict, config_dict)
    
    ## combine previous and new publications lists and save
    fileio.save_publications_to_file(save_dir_name, publication_dict, prev_pubs)
    
    print("Success. Publications, reports, and emails saved in " + save_dir_name)



def reference_search(args):
    """
    """
    
    config_dict, tokenized_citations, has_previous_pubs, prev_pubs = ref_srch_modularized.input_reading_and_checking(args)       

    publication_dict, tokenized_citations = ref_srch_modularized.build_publication_dict(args, config_dict, tokenized_citations)
            
    save_dir_name = ref_srch_modularized.save_and_send_reports_and_emails(args, config_dict, tokenized_citations, publication_dict, prev_pubs, has_previous_pubs)
            
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
            
    old_authors_json = copy.deepcopy(config_dict["Authors"])
    
    print("Searching ORCID for author's ORCID ids.")
    config_dict["Authors"] = webio.search_ORCID_for_ids(config_dict["ORCID_search"]["ORCID_key"], config_dict["ORCID_search"]["ORCID_secret"], config_dict["Authors"])
    
    if old_authors_json != config_dict["Authors"]:
        ## Build the save directory name.
        save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
    
        fileio.save_json_to_file(save_dir_name, "configuration.json", config_dict)
        print("Success! configuration.json saved in " + save_dir_name)
    else:
        print("No authors were matched from the ORCID results. No new file saved.")



def find_Google_Scholar(args):
    """"""
    
    user_input_checking.cli_inputs_check(args)
    
    ## read in config file
    config_dict = fileio.load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.tracker_validate(config_dict, tracker_schema.Authors_schema)
        
    old_authors_json = copy.deepcopy(config_dict["Authors"])
    
    print("Searching Google Scholar for author's scholar ids.")
    config_dict["Authors"] = webio.search_Google_Scholar_for_ids(config_dict["Authors"])
    
    if old_authors_json != config_dict["Authors"]:
        ## Build the save directory name.
        save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
        os.mkdir(save_dir_name)
    
        fileio.save_json_to_file(save_dir_name, "configuration.json", config_dict)
        print("Success! configuration.json saved in " + save_dir_name)
    else:
        print("No authors were matched from the Google Scholar results. No new file saved.")



def add_authors(args):
    """"""
    
    user_input_checking.cli_inputs_check(args)
    
    ## read in config file
    config_dict = fileio.load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.tracker_validate(config_dict, tracker_schema.Authors_schema)
    
    ## Check the file extension and call the correct read in function.
    extension = os.path.splitext(args["<author_file>"])[1][1:]
    if extension == "csv":
        df = fileio.read_csv(args["<author_file>"])
    else:
        print("Unknown file type for author file.")
        sys.exit()
            
    
    required_columns = tracker_schema.config_schema["properties"]["Authors"]["additionalProperties"]["required"] + ["author_id"]
    missing_required = [column for column in required_columns if column not in df.columns]
    if not missing_required:
        print("Error: The following columns are required but are missing:\n" + "\n".join(missing_required))
        sys.exit()
        
    missing_values = [column for column in required_columns if df.loc[:, column].isnull().values.any()]
    if not missing_values:
        print("Error: The following columns have null values:\n" + "\n".join(missing_values))
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
    authors_dict = df.to_dict("index")
    config_dict["Authors"].update(authors_dict)
    
    save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
    os.mkdir(save_dir_name)

    fileio.save_json_to_file(save_dir_name, "configuration.json", config_dict)
    print("Success! configuration.json saved in " + save_dir_name)
    
  
    
def tokenize_reference(args):
    """"""
    
    user_input_checking.cli_inputs_check(args)
    
    tokenized_citations = ref_srch_webio.tokenize_reference_input(args["<reference_file_or_URL>"], args["--MEDLINE_reference"], args["--verbose"])
    
    report_string = ref_srch_emails_and_reports.create_tokenization_report(tokenized_citations)
    
    save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.datetime.now())[2:16])
    os.mkdir(save_dir_name)
        
    fileio.save_string_to_file(report_string, save_dir_name, "tokenization_report.txt")
            
    fileio.save_json_to_file(save_dir_name, "tokenized_reference.json", tokenized_citations)
    
    print("Success! Tokenization files saved in " + save_dir_name)
    


def gen_reports_and_emails_auth(args):
    """"""
    
    config_dict = athr_srch_modularized.input_reading_and_checking(args)
    
    ## Create an authors_json for each project in the config_dict and update those authors attributes with the project attributes.
    authors_by_project_dict, config_dict = athr_srch_modularized.generate_internal_data_and_check_authors(args, config_dict)
    
    ## Read in publications.json
    publication_dict = fileio.load_json(args["<publication_json_file>"])
    user_input_checking.prev_pubs_file_check(publication_dict)
                
    
    save_dir_name = athr_srch_modularized.save_and_send_reports_and_emails(args, authors_by_project_dict, publication_dict, config_dict)
    
    print("Success! Reports and emails saved in " + save_dir_name)
    
    


def gen_reports_and_emails_ref(args):
    """"""
    
    config_dict, tokenized_citations, has_previous_pubs, prev_pubs = ref_srch_modularized.input_reading_and_checking(args)       

    ## Read in publications.json
    publication_dict = fileio.load_json(args["<publication_json_file>"])
    user_input_checking.prev_pubs_file_check(publication_dict)
    
    matching_key_for_citation = []
    for citation in tokenized_citations:
        if not citation["pub_dict_key"]:
            if citation["DOI"] and citation["DOI"] in publication_dict:
                citation["pub_dict_key"] = citation["DOI"]
                matching_key_for_citation.append(citation["DOI"])
            elif citation["PMID"] and citation["PMID"] in publication_dict:
                citation["pub_dict_key"] = citation["PMID"]
                matching_key_for_citation.append(citation["PMID"])
            elif citation["title"] and citation["title"] in publication_dict:
                citation["pub_dict_key"] = citation["title"]
                matching_key_for_citation.append(citation["title"])
        else:
            matching_key_for_citation.append(citation["pub_dict_key"])
            
    for key in list(publication_dict.keys()):
        if not key in matching_key_for_citation:
            del publication_dict[key]
            
    if not publication_dict:
        print("Error: No entries in the publication JSON matched any reference in the provided reference.")
        sys.exit()
            
    
    save_dir_name = ref_srch_modularized.save_and_send_reports_and_emails(args, config_dict, tokenized_citations, publication_dict, prev_pubs, has_previous_pubs)
    
    print("Success! Reports and emails saved in " + save_dir_name)


               
                
if __name__ == "__main__":
    
    main()
