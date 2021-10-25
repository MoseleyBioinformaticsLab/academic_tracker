"""   
    
Usage:
    academic_tracker <config_json_file> <authors_json_file> [options]
    
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
## TODO test on Mac OS



from .fileio import load_json, read_previous_publications, save_emails_to_file, save_publications_to_file
from .user_input_checking import author_file_check, config_file_check, prev_pubs_file_check, cli_inputs_check
from .webio import request_pubs_from_pubmed, send_emails, create_emails_dict
import re
import os
from datetime import datetime






def find_publications(args):
    """Main function that links everything together and runs the program.
    
    Reads in the JSON config file, authors JSON file, previous publications JSON file, and checks for errors.
    Then requests publications from PubMed and builds the emails to go to each author. Then saves them emails
    and publications to file and sends emails depending on the options entered by the user. See the program 
    docstring for options details.
    
    Args:
        args (dict): args from DocOpt CLI
    
    """
    
    cli_inputs_check(args)
    
    ## read in authors
    authors_dict = load_json(args["<authors_json_file>"])
    author_file_check(authors_dict)
    
    ## read in config file
    config_file = load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
    config_file_check(config_file)
    
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
    has_previous_pubs, prev_pubs = read_previous_publications(args)
    if has_previous_pubs:
        prev_pubs_file_check(prev_pubs)
            
            
    ## Get publications from PubMed and build email messages
    print("Finding author's publications. This could take a while.")
    publication_dict, pubs_by_author_dict = request_pubs_from_pubmed(prev_pubs, authors_dict, config_file["from_email"], args["--verbose"])
    if len(publication_dict) == 0:
        print("No new publications found.")
    
    
    email_messages = create_emails_dict(pubs_by_author_dict, authors_dict, publication_dict)
    
    
    ## Build the save directory name.
    if args["--test"]:
        save_dir_name = "tracker-test-" + re.sub(r"\-| |\:", "", str(datetime.now())[2:16])
        os.mkdir(save_dir_name)
    else:
        save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.now())[2:16])
        os.mkdir(save_dir_name)
        
    
    
    ## save email messages to file
    save_emails_to_file(email_messages, save_dir_name)
            
    
    ## send emails
    if not args["--test"]:
        send_emails(email_messages)
    
    
    ## combine previous and new publications lists and save
    save_publications_to_file(save_dir_name, publication_dict, prev_pubs)
    
    print("Success. Publications and emails saved in " + save_dir_name)



