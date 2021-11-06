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
        
    PMID_list = document_string.split("\n")
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



def search_by_DOI(args):
    """
    """
    
    user_input_checking.cli_inputs_check(args)
    ## read in config file
    config_file = fileio.load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.config_file_check(config_file)
    
    ## TODO either add a to email to config here, or figure out better way to get it from user.
    
    ## Overwrite values in config_file if command line options were used.
    ## Note the replacement is after checking both inputs and config_file independnetly. If done before config_file_check then CLI errors will dispaly as config_file errors.
    overwriting_options = ["--grants", "--cutoff_year", "--from_email", "--cc_email", "--affiliations"]
    for option in overwriting_options:
        if args[option]:
            config_file[option.replace("-","")] = args[option]
            
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
    
    publications_with_no_PMCID_list = webio.search_DOIs_on_pubmed(DOI_list, config_file["from_email"])
    
    email_messages = webio.create_email_dict_for_no_PMCID_pubs(publications_with_no_PMCID_list, config_file, args["<to_email>"])
    
    ## send emails
    if not args["--test"]:
        webio.send_emails(email_messages)



def search_by_author(args):
    """Main function that links everything together and runs the program.
    
    Reads in the JSON config file, authors JSON file, previous publications JSON file, and checks for errors.
    Then requests publications from PubMed and builds the emails to go to each author. Then saves them emails
    and publications to file and sends emails depending on the options entered by the user. See the program 
    docstring for options details.
    
    Args:
        args (dict): args from DocOpt CLI
    
    """
    
    user_input_checking.cli_inputs_check(args)
    
    ## read in authors
    authors_dict = fileio.load_json(args["<authors_json_file>"])
    user_input_checking.author_file_check(authors_dict)
    
    ## read in config file
    config_file = fileio.load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
    user_input_checking.config_file_check(config_file)
    
    ## Overwrite values in config_file if command line options were used.
    ## Note the replacement is after checking both inputs and config_file independnetly. If done before config_file_check then CLI errors will dispaly as config_file errors.
    overwriting_options = ["--grants", "--cutoff_year", "--from_email", "--cc_email", "--affiliations"]
    for option in overwriting_options:
        if args[option]:
            config_file[option.replace("-","")] = args[option]
    

    ## Loop over the authors and add values from the config_file if not there.
    for author_attr in authors_dict.values():
        for key in config_file:
            author_attr.setdefault(key, config_file[key])
    
    
        
    ## read in previous publications to ignore
    has_previous_pubs, prev_pubs = fileio.read_previous_publications(args)
    if has_previous_pubs:
        user_input_checking.prev_pubs_file_check(prev_pubs)
            
            
    ## Get publications from PubMed and build email messages
    print("Finding author's publications. This could take a while.")
    publication_dict, pubs_by_author_dict = webio.request_pubs_from_pubmed(prev_pubs, authors_dict, config_file["from_email"], args["--verbose"])
    if len(publication_dict) == 0:
        print("No new publications found.")
    
    
    email_messages = webio.create_emails_dict(pubs_by_author_dict, authors_dict, publication_dict)
    
    
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
    
    
    ## combine previous and new publications lists and save
    fileio.save_publications_to_file(save_dir_name, publication_dict, prev_pubs)
    
    print("Success. Publications and emails saved in " + save_dir_name)



def main():
    
    args = docopt.docopt(__doc__, version=str("Academic Tracker ") + __version__)
    
    if len(sys.argv) > 1 and sys.argv[1] == "search_by_author":
        search_by_author(args)
    elif len(sys.argv) > 1 and sys.agrv[1] == "search_by_DOI":
        search_by_DOI(args)
    elif len(sys.argv) > 1 and sys.argv[1] == "create_publication_json":
        create_publication_json(args)
    else:
        print("Unrecognized command")               
                
                
if __name__ == "__main__":
    
    main()
