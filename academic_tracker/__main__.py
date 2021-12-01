"""   
Usage:
    academic_tracker search_by_author <config_json_file> <authors_json_file> [options]
    academic_tracker search_by_DOI <config_json_file> <to_email> <DOI_file> [options]
    academic_tracker create_publication_json <PMID_file> <from_email> [options]
    
Options:
    -h --help                         Show this screen.
    --version                         Show version.
    --verbose                         Print hidden error messages.
    --test                            Generate pubs and email texts, but do not send emails.
    --grants=<nums>...                Grant numbers to filter publications by. Must be a comma separated list with no spaces.
    --cutoff_year=<num>               YYYY year before which to ignore publications.
    --from_email=<email>              Send authors email from provided email address.
    --cc_email=<emails>...            Email addresses to cc on the sent emails. Must be a comma separated list with no spaces.
    --prev_pub=<file-path>            Filepath to json or csv with publication ids to ignore.
    --affiliations=<affiliations>...  An affiliation to filter publications by. Must be a comma separated list with no spaces.   
"""


## TODO add master option to send an email or print file with all publications found.
## TODO add pull from myncbi.
## TODO add usage case for reading in a author csv or excel file and creating json.
## TODO add use case for reading in an authors json and searching Google Scholar for their scholar id.
## TODO add options to ignore google scholar and orcid
## TODO add functionality to more easily handle verbose option, and add more messages when it is in use.


from . import fileio
from . import user_input_checking
from . import webio
from . import helper_functions
import re
import os
import datetime
import docopt
import sys
from . import __version__



def create_publication_json(args):
    """
    
    """
    
    user_input_checking.cli_inputs_check(args)
    
    ## Check the DOI file extension and call the correct read in function.
    extension = os.path.splitext(args["<PMID_file>"])[1][1:]
    if extension == "docx":
        document_string = fileio.read_text_from_docx(args["<PMID_file>"])
    elif extension == "txt" or extension == "csv":
        document_string = fileio.read_text_from_txt(args["<PMID_file>"])
    else:
        print("Unknown file type for PMID file.")
        sys.exit()
    
    if not document_string:
        print("Nothing was read from the PMID file. Make sure the file is not empty or is a supported file type.")
        sys.exit()
        
    PMID_list = [line for line in document_string.split("\n") if line]
    print("Querying PubMed and building the publication list.")
    publication_dict = webio.build_pub_dict_from_PMID(PMID_list, args["<from_email>"])
    
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



def search_by_DOI(args):
    """
    """
    
    user_input_checking.cli_inputs_check(args)
    ## read in config file
    config_file = fileio.load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.config_file_check(config_file)
        
    ## Overwrite values in config_file if command line options were used.
    ## Note the replacement is after checking both inputs and config_file independnetly. If done before config_file_check then CLI errors will dispaly as config_file errors.
    config_file = helper_functions.overwrite_config_with_CLI(config_file, args)
            
    ## Check the DOI file extension and call the correct read in function.
    extension = os.path.splitext(args["<DOI_file>"])[1][1:]
    if extension == "docx":
        document_string = fileio.read_text_from_docx(args["<DOI_file>"])
    elif extension == "txt":
        document_string = fileio.read_text_from_txt(args["<DOI_file>"])
    else:
        print("Unknown file type for DOI file.")
        sys.exit()
    
    if not document_string:
        print("Nothing was read from the DOI file. Make sure the file is not empty or is a supported file type.")
        sys.exit()
        
    DOI_list = helper_functions.parse_string_for_pub_info(document_string, r"(?i).*doi:\s*([^\s]+\w).*", r"(?i).*pmid:\s*(\d+).*", r"(?i).*pmcid:\s*(pmc\d+).*")
    
    print("Querying PubMed and building the publication list.")
    publications_with_no_PMCID_list = webio.search_DOIs_on_pubmed(DOI_list, config_file["PubMed_search"]["PubMed_email"])
    
    email_messages = webio.create_email_dict_for_no_PMCID_pubs(publications_with_no_PMCID_list, config_file, args["<to_email>"])
    
    ## send emails
    if not args["--test"]:
        webio.send_emails(email_messages)



def search_by_author(args):
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
    
    ## read in authors
    authors_json_file = fileio.load_json(args["<authors_json_file>"])
    user_input_checking.author_file_check(authors_json_file)
    
    ## read in config file
    config_file = fileio.load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.config_file_check(config_file)

    ## Overwrite values in config_file if command line options were used.
    ## Note the replacement is after checking both inputs and config_file independnetly. If done before config_file_check then CLI errors will dispaly as config_file errors.
    config_file = helper_functions.overwrite_config_with_CLI(config_file, args)
    
    
    ## Create an authors_json_file for each project in the config_file and update those authors attributes with the project attributes.
    authors_by_project_dict = {project:{} for project in config_file["project_descriptions"]}
    for project, project_attributes in config_file["project_descriptions"].items():
        if "authors" in project_attributes:
            for author in project_attributes["authors"]:
                if author in authors_json_file:
                    authors_by_project_dict[project][author] = authors_json_file[author]
                else:
                    print("Warning: " + author + " in the " + project + " project of the project tracking configuration file could not be found in the authors' JSON file.")
        else:
            authors_by_project_dict[project] = authors_json_file
    
        for author_attr in authors_by_project_dict[project].values():
            for key in project_attributes:
                author_attr.setdefault(key, project_attributes[key])
                
                
    ## Look for authors not in any projects and warn user.
    authors_in_projects = {author for project_attributes in config_file["project_descriptions"].values() for author in project_attributes["authors"] if "authors" in project_attributes }
    authors_not_in_projects = set(authors_json_file.keys()) - authors_in_projects
    projects_without_authors = [project for project, project_attributes in config_file["project_descriptions"].items() if not "authors" in project_attributes]
    
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
    PubMed_publication_dict = webio.search_PubMed_for_pubs(prev_pubs, authors_by_project_dict, config_file["PubMed_search"]["PubMed_email"], args["--verbose"])
    prev_pubs.update(PubMed_publication_dict)
    print("Searching ORCID.")
    ORCID_publication_dict = webio.search_ORCID_for_pubs(prev_pubs, config_file["ORCID_search"]["ORCID_key"], config_file["ORCID_search"]["ORCID_secret"], authors_by_project_dict, args["--verbose"])
    prev_pubs.update(ORCID_publication_dict)
    print("Searching Google Scholar.")
    Google_Scholar_publication_dict = webio.search_Google_Scholar_for_pubs(prev_pubs, authors_json_file, authors_by_project_dict, args["--verbose"])
    prev_pubs.update(Google_Scholar_publication_dict)
    print("Searching Crossref.")
    Crossref_publication_dict = webio.search_Crossref_for_pubs(prev_pubs, authors_json_file, authors_by_project_dict, config_file["Crossref_search"]["mailto_email"], args["--verbose"])
    prev_pubs.update(Crossref_publication_dict)
    
    publication_dict = PubMed_publication_dict
    publication_dict.update(ORCID_publication_dict)
    publication_dict.update(Google_Scholar_publication_dict)
    publication_dict.update(Crossref_publication_dict)
        
        
    if len(publication_dict) == 0:
        print("No new publications found.")
    
    
    email_messages = helper_functions.create_emails_dict(authors_by_project_dict, publication_dict, config_file)
    
    
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
    
    ## Create project reports and save to file.
    fileio.save_project_reports_to_file(publication_dict, save_dir_name, config_file["project_descriptions"])
    
    ## combine previous and new publications lists and save
    fileio.save_publications_to_file(save_dir_name, publication_dict, prev_pubs)
    
    print("Success. Publications and emails saved in " + save_dir_name)



def main():
    
    args = docopt.docopt(__doc__, version=str("Academic Tracker ") + __version__)
    
    if len(sys.argv) > 1 and sys.argv[1] == "search_by_author":
        search_by_author(args)
    elif len(sys.argv) > 1 and sys.argv[1] == "search_by_DOI":
        search_by_DOI(args)
    elif len(sys.argv) > 1 and sys.argv[1] == "create_publication_json":
        create_publication_json(args)
    else:
        print("Unrecognized command")               
                
                
if __name__ == "__main__":
    
    main()
