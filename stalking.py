"""   
    
Usage:
    stalker.py <config_json_file> <authors_json_file> [options]
    
Options:
    -h --help                         Show this screen.
    --version                         Show version.
    --test                            Generate pubs and email texts, but do not send emails.
    --grants=<nums>...                Grant numbers to filter publications by. Must be a comma separated list with no spaces.
    --cutoff_year=<num>               YYYY year before which to ignore publications.
    --from_email=<email>              Send authors email from provided email address.
    --cc_email=<emails>...            Email addresses to cc on the sent emails. Must be a comma separated list with no spaces.
    --prev_pub=<file-path>            Filepath to json or csv with publication ids to ignore.
    --affiliations=<affiliations>...  An affiliation to filter publications by. Must be a comma separated list with no spaces.
    
    
"""

pub_med_url = "https://pubmed.ncbi.nlm.nih.gov/"
config_file_keys = ["grants", "cutoff_year", "affiliations", "from_email", "cc_email", "email_template", "email_subject"]
__version__ = "1.0.0"




from collections import OrderedDict
from urllib.request import urlopen
from os.path import join
import docopt
#from . import __version__
from fileio import load_json
from time import sleep
from pymed import PubMed
from email.message import EmailMessage
import json
import sys
import re
import os
from datetime import datetime
import subprocess



def create_citation(publication):
    """Build a human readable string describing the publication.
    
    Args:
        publication (dict): dictionary of a publication from PubMed's API
        
    Returns:
        publication_str (str): human readable string with authors names, publication date, title, journal, DOI, and PubMed id
    
    """
    publication_str = ""

    publication_str += ", ".join([auth["lastname"] + " " + auth["initials"] for auth in publication[1]["authors"] if auth["lastname"] and auth["initials"]]) + "."
    publication_str += " {}.".format(publication[1]["publication_date"][:4])
    publication_str += " {}.".format(publication[1]["title"])
    publication_str += " {}.".format(publication[1]["journal"])
    publication_str += " {}".format(publication[1]["doi"])
    publication_str += " PMID:{}".format(publication[1]["pubmed_id"].split("\n")[0])

    return publication_str


def config_file_check(args, config_json):
    """Check that the configuration JSON file is as expected.
    
    The configuration JSON file format is expected to be::
        {
             "grants" : [ "P42ES007380", "P42 ES007380" ],
             "cutoff_year" : "2019",
             "affiliations" : [ "kentucky" ],
             "from_email" : "ptth222@uky.edu",
             "cc_email" : [], # optional
             "email_template" : "<formatted-string>",
             "email_subject" : "<formatted-string>"
        }
    
    Each attribute is checked for type and appropriate values.
    
    Args:
        args (dict): args dict from DocOpt
        config_json (dict): dict with the same structure as the configuration JSON file
        
    Returns:
        grants (list): list of strings to see if publications were cited for
        cutoff_year (int): year before which to filter publications by
        affililations (list): list of strings to filter authors by
        from_email (str): email address for email messages to be sent from
        cc_email (list): list of email addresses to cc each email to
        email_template (str): string used to construct an email message
        email_subject (str): string used to construct an email subject
    
    """
    
    ## Go through each possible key and handle them appropriately.
    ## See if it exists or not and that it is the right type, then do further handling or print an error.
    
    if args["--grants"]:
        grants = args["--grants"].split(",")
    ## If grants is not a list make it one.
    elif not "grants" in config_json:
        print("Error: No \"grants\" detected in JSON configuration file or command line arguments.")
        sys.exit()
    else:
        if type(config_json["grants"]) == list:
            if any(type(value) != str for value in config_json["grants"]):
                print("Error: Non-string type value in \"grants\" list in JSON configuration file.")
                sys.exit()
            
            else:
                grants = config_json["grants"]
        elif type(config_json["grants"]) == str:
            grants = [config_json["grants"]]
        else:
            print("Error: Non-string or list type value for \"grants\" in JSON configuration file.")
            sys.exit()
            
    if len(grants) == 0:
        print("Error: No values found for \"grants\" in JSON configuration file or command line.")
        sys.exit()
        
    if all(len(grants_string) == 0 for grants_string in grants):
        print("Error: All values in \"grants\" are empty strings.")
        sys.exit()
            
    
    ## Make sure cutoff_year con be turned into an int.  
    if args["--cutoff_year"]:
        cutoff_year = args["--cutoff_year"]      
    elif not "cutoff_year" in config_json:
        print("Error: No \"cutoff_year\" detected in JSON configuration file or command line arguments.")
        sys.exit()
    else:
        if type(config_json["cutoff_year"]) != int:
            print("Error: Non-int type value for \"cutoff_year\" in JSON configuration file.")
            sys.exit()
        
        else:
            cutoff_year = config_json["cutoff_year"]
                
        if cutoff_year > 3000:
            print("Error: \"cutoff_year\" in JSON configuration file is greater than 3000.")
            sys.exit()
            
            
    
    if args["--affiliations"]:
        affiliations = args["--affiliations"].lower().split(",")
    elif not "affiliations" in config_json:
        print("Error: No \"affiliations\" detected in JSON configuration file or command line arguments.")
        sys.exit()
    else:
        if type(config_json["affiliations"]) == list:
            if any(type(value) != str for value in  config_json["affiliations"]):
                print("Error: Non-string type value in \"affiliations\" list in JSON configuration file.")
                sys.exit()
            
            else:
                affiliations = config_json["affiliations"]
        elif type(config_json["affiliations"]) == str:
            affiliations = [config_json["affiliations"]]
        else:
            print("Error: Non-string or list type value for \"affiliations\" in JSON configuration file.")
            sys.exit()
            
    if len(affiliations) == 0:
        print("Error: No values found for \"affiliations\" in JSON configuration file or command line.")
        sys.exit()
        
    if all(len(affiliation_string) == 0 for affiliation_string in affiliations):
        print("Error: All values in \"affiliations\" are empty strings.")
        sys.exit()
            

    if args["--from_email"]:
        from_email = args["--from_email"]
    elif not "from_email" in config_json:
        print("Error: No \"from_email\" detected in JSON configuration file or command line arguments.")
        sys.exit()
    else:
        if type(config_json["from_email"]) != str:
            print("Error: Non-string type value for \"from_email\" in JSON configuration file.")
            sys.exit()
        
        else:
            from_email = config_json["from_email"]

    if not re.match(".+@.+\..+", from_email):
        print("Error: The \"from_email\" email attribute in the JSON configuration file does not look like an email.")
        sys.exit()
        
        
    
    if args["--cc_email"]:
        cc_email = args["--cc_email"].split(",")      
    elif not "cc_email" in config_json:
        cc_email = []
    else:
        if type(config_json["cc_email"]) == list:
            if any(type(value) != str for value in  config_json["cc_email"]):
                print("Error: Non-string type value in \"cc_email\" list in JSON configuration file.")
                sys.exit()
            
            else:
                cc_email = config_json["cc_email"]
        elif type(config_json["cc_email"]) == str:
            cc_email = [config_json["cc_email"]]
            
        else:
            print("Error: Non-string or list type value for \"cc_email\" in JSON configuration file.")
            sys.exit()
            
    if any(not re.match(".+@.+\..+", email) for email in cc_email):
            print("Error: An email in the \"cc_email\" attribute in the JSON configuration file does not look like an email.")
            sys.exit()
            
            
    
    if not "email_template" in config_json:
        print("Error: No \"email_template\" detected in JSON configuration file or command line arguments.")
        sys.exit()
    else:
        if type(config_json["email_template"]) != str:
            print("Error: Non-string type value for \"email_template\" in JSON configuration file.")
            sys.exit()
        
        else:
            email_template = config_json["email_template"]
            if len(email_template) == 0:
                print("Error: Empty string detected for \"email_template\" in JSON configuration file.")
                sys.exit()
                
            if not re.match(r".*<total_pubs>.*", email_template, flags=re.DOTALL):
                print("Error: \"email_template\" in JSON configuration file does not indicate where to print the publications. \"<total_pubs>\" must be in the string.")
                sys.exit()
        
        
    
    if not "email_subject" in config_json:
        print("Error: No \"email_subject\" detected in JSON configuration file or command line arguments.")
        sys.exit()
    else:
        if type(config_json["email_subject"]) != str:
            print("Error: Non-string type value for \"email_subject\" in JSON configuration file.")
            sys.exit()
        
        else:
            email_subject = config_json["email_subject"]
            if len(email_subject) == 0:
                print("Error: Empty string detected for \"email_subject\" in JSON configuration file.")
                sys.exit()
        
        
        
        
    return grants, cutoff_year, affiliations, from_email, cc_email, email_template, email_subject
            








def author_file_check(authors_dict):
    """Run input checking on the authors_dict.
    
    The authos_dict read in from the authors JSON file is expected to have the format::
        {
            "Author 1": {  
                           "first_name" : "<first_name>",
                           "last_name" : "<last_name>",
                           "pubmed_name_search" : "<search-str>",
                           "email": "email@uky.edu",
                           "ORCID": "<orcid>" # optional           
                        },
            
            "Author 2": {  
                           "first_name" : "<first_name>",
                           "last_name" : "<last_name>",
                           "pubmed_name_search" : "<search-str>",
                           "email": "email@uky.edu",       
                           "ORCID": "<orcid>" # optional 
                        },
        }
            
    The type of each element and attribute is checked. id is checked to make sure 
    it matches the key of the author, and the email is checked to make sure it looks 
    like an email.
    
    Args:
        authors_dict (dict): dict with the same structure as the authors JSON file.
    
    
    """
    required_author_file_keys = ["first_name", "last_name", "pubmed_name_search", "email"]
    optional_author_file_keys = ["ORCID"]
    
    if type(authors_dict) != dict:
        print("Error: Non-dict type value for authors JSON file.")
        sys.exit()
    
            
    for author, author_attributes  in authors_dict.items():
        
        if type(author_attributes) != dict :
            print("Error: The author, " + author + ", is missing author attributes.")
            sys.exit()
        
        ## Make sure each author has the appropriate attributes.
        if len(set(required_author_file_keys) - set(author_attributes.keys())) > 0:
            print("Error: The author, " + author + ", is missing attribute(s) in authors JSON file.")
            sys.exit()
        
        ## Make sure each attribute we expect has the appropriate value.
        ## For now assuming each attribute just needs to be a string.
        for attribute_name, attribute_value in author_attributes.items():
            if attribute_name in required_author_file_keys or attribute_name in optional_author_file_keys:
                if type(attribute_value) != str:
                    print("Error: Non-string type value in, " + attribute_name + " for, " + author)
                    sys.exit()
                    
                if len(attribute_value.replace(" ", "")) == 0:
                    print("Error: The " + attribute_name + " attribute for author, " + author + ", has no value.")
                    sys.exit()
                
                    
                ## The email attribute needs to look like an email.
                if attribute_name == "email" and not re.match(".+@.+\..+", attribute_value):
                    print("Error: The author, " + author + ", email attribute does not look like an email.")
                    sys.exit()
                    
                    
                ## ORCID must be a certain format.
                if attribute_name == "ORCID" and not re.match(r"\d{4}-\d{4}-\d{4}-\d{3}[0,1,2,3,4,5,6,7,8,9,X]", attribute_value):
                    print("Error: The ORCID for author, " + author + ", is not a valid ORCID.")
                    sys.exit()




## TODO add checks for attributes after figuring out what attributes to keep.
def read_previous_publications(args):
    """Read in the previous publication json file.
    
    If the prev_pub option was given by the user then that filepath is used to read in the file
    and it is checked to make sure the json is a list and each value is a string. If the prev_pub
    option was not given then look for a "tracker-timestamp" directory in the current working 
    directory and if it has a publications.json file in its publications directory then read in 
    that file and check it for errors. If no previous publications are found then None is returned 
    for prev_pubs.
    
    Args:
        args (dict): args dict from DocOpt
        
    Returns:
        has_previous_pubs (bool): True means that a previous publications file was found
        prev_pubs (dict): dict where keys are publication ids and values are a dict of publication attributes
    
    """
    
    has_previous_pubs = False
    if args["--prev_pub"]:
        prev_pubs = load_json(args["--prev_pub"])
        has_previous_pubs = True
                            
    else:
        dir_contents = os.listdir()
        ## find all directories matching the tracker directory structure and convert the timestamps to ints to find the largest one.
        tracker_dirs = [int(re.match(r"tracker-(\d{10})", folder).group(1)) for folder in dir_contents if re.match(r"tracker-(\d{10})", folder)]
        if len(tracker_dirs) > 0:
            latest_dir = max(tracker_dirs)
            current_day = str(datetime.now())[2:10].replace("-","")
            if current_day == str(latest_dir)[:6]:
                print("Warning: The latest tracker directory was made earlier today.")
            prev_publication_filepath = os.path.join(os.getcwd(), "tracker-"+str(latest_dir), "publications", "publications.json")
            if os.path.exists(prev_publication_filepath):
                prev_pubs = load_json(prev_publication_filepath)
                has_previous_pubs = True
            else:
                print("Error: The latest tracker publications directory does not have a previous publications file.")
                sys.exit()
    
    if has_previous_pubs:    
        ## Make sure the previous publication file is the format we expect.
        if type(prev_pubs) != dict:
            print("Error: Non-dict type value for the previous publications JSON.")
            sys.exit()
        
        elif any(type(value) != str for value in prev_pubs):
            print("Error: Non-string type value in previous publications list.")
            sys.exit()
            
        elif len(prev_pubs) == 0:
            print("Error: Previous publications dict is empty.")
            sys.exit()
        
        else:
            for value in prev_pubs:
                try:
                    int(value)
                except:
                    print("Error: Non-numerical value in previous publications list.")
                    sys.exit()
                    
                    
        return has_previous_pubs, prev_pubs
    
    else:
        return has_previous_pubs, None
    





def request_pubs_and_build_emails(has_previous_pubs, prev_pubs, authors_dict, affiliations, cutoff_year, grants, from_email, email_template, email_subject, cc_email):
    """Searhes PubMed for publications by each author and creates email messages to send to each author about the publications.
    
    For each author in authors_dict PubMed is queried for the publications. The list of publications is then filtered 
    by prev_pubs, affiliations, and cutoff_year. If the publication is in the list of prev_pubs then it is skipped. 
    If the author doesn't have at least one matching affiliation then the publication is skipped. If the publication 
    was published before the cutoff_year then it is skipped. Each publication is then determined to have citations 
    for any of the grants in grants and is sorted into 2 lists based on this criteria. An email to any author that 
    had publicaitons found for them is then constructed. The list of publications is broken into 2 sections in the 
    email based on grant citation status.
    
    Args:
        has_previous_pubs (bool): If True then the function uses prev_pubs to filter out found publications
        prev_pubs (list): List of publications ids as strings to filter publications found on PubMed
        authors_dict (dict): keys are author names and values should be a dict with attributes, but only the keys are used
        affililations (list): list of strings used to compare against the author's affiliations 
        cutoff_year (int): if the publication was published before this year it is skipped
        grants (list): list of strings used to see if the publication is cited for
        from_email (str): used in the query to PubMed
        email_template (str): formatted string that is used to build the body of the email to the author
        email_subject (str): formatted string that is used to build the subject of the email of the author
        cc_email (list): list of email addresses to cc each email to
        
    Returns:
        publication_dict (dict): keys are pulication ids and values are a dictionary with publication attributes
        email_messages (dict): keys are author names and values are a dict with the "subject", "body", "from", "to", and "cc" parts of the email
    
    
    """
       
    # initiate PubMed API
    pubmed = PubMed(tool="Publication_Tracker", email=from_email)

    publication_dict = dict()
    
    # key is author and value is a dict of publication ids with a list of grants cited for them.
    pubs_by_author_dict = {}
    
    # dict for email messages. keys are authors and values are the email message
    email_messages = {}

    ########################
    # loop through list of authors and request a list of their publications
    ########################
    for author, author_attributes in authors_dict.items():
        
        author_has_pubs = False
        ##TODO test that ORCID works in query.
        if "ORCID" in author_attributes:
            publications = pubmed.query(author_attributes["ORCID"], max_results=500)
        else:
            publications = pubmed.query(author_attributes["pubmed_name_search"], max_results=500)
        
        ## Unpacking pub from publications appears to be the slowest part of the code.
        ## publications is an iterator that is broken up into batches and there are noticeable slow downs each time a new batch is fetched.
        for pub in publications:
            
            ## Only proceed with publications that have at least one author with an affiliation that is in the given affiliations.
            ## pub.authors are dictionaries with lastname, firstname, initials, and affiliation. firstname can have initials at the end ex "Andrew P"
            ## It might be better to find the author we are looking for and match an affiliation instead of matching to any author.
            publication_has_affiliated_author = False
            for author_items in pub.authors:
                ## affiliations are sets of strings so the intersection should have at least 1 string for a match.
                if len(set(affiliations).intersection(set(re.findall(r"[\w]+", str(author_items.get("affiliation")).lower())))) > 0:
                    publication_has_affiliated_author = True
                    break
                
            
            if publication_has_affiliated_author:
                pub_dict = pub.toDict()
                pub_id = pub_dict.get("pubmed_id").split("\n")[0]
                    
                ## if the publication id is in the list of previously found ones then skip
                ## TODO check and see if prev_pub now has grant citation if it didn't before. Add key to publication_dict to keep track.
                if has_previous_pubs and pub_id in prev_pubs:
                    continue
                
                del pub_dict["xml"]
                pub_dict["publication_date"] = str(pub_dict["publication_date"])

                if int(pub_dict["publication_date"][:4]) >= cutoff_year:
                    author_has_pubs = True

                    # add publications to the publication_dict if not there, else add author to the publication.
                    # author is a dict so that authors are not repeated.
                    if not pub_id in publication_dict.keys():
                        publication_dict[pub_id] = [{author}, pub_dict]
                    else:
                        publication_dict[pub_id][0].add(author)
                        
                    response = urlopen(join(pub_med_url, pub_id))
                    url_str = response.read().decode("utf-8")
                    response.close()
                    
                    
                    ## Add publication to dict under the author.
                    if author not in pubs_by_author_dict:
                        pubs_by_author_dict[author] = {pub_id:[]}
                    else:
                        pubs_by_author_dict[author][pub_id] = []
                    
                    ## Look for each grant_id and if found add it to dict.
                    for grant_id in grants:
                        if grant_id in url_str:
                            pubs_by_author_dict[author][pub_id].append(grant_id)
                    
                    
                    
            
        # don't piss off NCBI
        sleep(1)
        
        
        ################################
        ## build email message for the author
        ###############################
        if author_has_pubs:
            
            pubs_string = ""
            for pub_id in pubs_by_author_dict[author]:
                pubs_string += create_citation(publication_dict[pub_id]) + "\n\n" + "Cited Grants:\n"
                
                if pubs_by_author_dict[author][pub_id]:
                    for grant_id in pubs_by_author_dict[author][pub_id]:
                        pubs_string += grant_id
                        
                else:
                    pubs_string += "None"
                    
                pubs_string += "\n\n\n"
                
           
            body = email_template    
            body = body.replace("<total_pubs>", pubs_string)
            body = body.replace("<author_first_name>", author_attributes["first_name"])
            body = body.replace("<author_last_name>", author_attributes["last_name"])
            
            subject = email_subject
            subject = subject.replace("<author_first_name>", author_attributes["first_name"])
            subject = subject.replace("<author_last_name>", author_attributes["last_name"])
            
            
            
            cc_string = ""
            for email in cc_email:
                cc_string += email + ","
            email_messages[author] = {"body": body, "subject": subject, "from": from_email, "to": authors_dict[author]["email"], "cc":cc_string}
        
        

    # convert author dict to list, it was only a dict to get unique names easily.
    for key in publication_dict.keys():
        publication_dict[key][0] = list(publication_dict[key][0])

    publication_dict = OrderedDict(sorted(publication_dict.items(), key=lambda x: x[1][1]["publication_date"], reverse=True))
    
    return publication_dict, email_messages




def save_emails_to_file(email_messages, save_dir_name):
    """Save email_messages to "emails.json" in save_dir_name in the current working directory.
    
    Args:
        email_messages (dict): keys are author names and values are the subject, body, from, to, and cc parts of the email
        save_dir_name (str): directory name to append to the current working directory to save the emails.json file in
    
    """
    
    email_save_path = os.path.join(os.getcwd(), save_dir_name, "emails.json")
    
    with open(email_save_path, 'w') as outFile:
        print(json.dumps(email_messages, indent=2, sort_keys=True), file=outFile)

                


def send_emails(email_messages):
    """Uses sendmail to send email_messages to authors.
    
    Only works on systems with sendmail installed. Pulls the authors' email 
    from the authors_dict and sends the corresponding email in email_messages
    to the author. Every email will have the cc_emails cc'd.
    
    Args:
        email_messages (dict): keys are author names and values are the message
    
    """
    
    # build and send each message by looping over the email_messages dict
    for author, email_parts in email_messages.items():
        msg = EmailMessage()
        msg["Subject"] = email_parts["subject"]
        msg["From"] = email_parts["from"]
        msg["To"] = email_parts["to"]
        msg["Cc"] = email_parts["cc"]
        msg.set_content(email_parts["body"])
        
        sendmail_location = "/usr/sbin/sendmail"
        subprocess.run([sendmail_location, "-t", "-oi"], input=msg.as_bytes())
            


def save_publications_to_file(save_dir_name, publication_dict, has_previous_pubs, prev_pubs):
    """Saves the publication_dict to file.
    
    If has_previous_pubs is True then prev_pubs and publication_dict will be combined before saving.
    
    Args:
        save_dir_name (str): directory name to append to the current working directory to save the publications.json file in
        publication_dict (dict): dictionary with publication ids as the keys to the dict
        has_previous_pubs (bool): True means that there are previous publications and they should be combined with new ones before saving
        prev_pubs (list): List of publication ids that are publications previously found.
    
    """
    
    publications_save_path = os.path.join(os.getcwd(), save_dir_name, "publications.json")
        
    if has_previous_pubs: 
        with open(publications_save_path, 'w') as outFile:
            print(json.dumps(prev_pubs.update(publication_dict), indent=2, sort_keys=True), file=outFile)
    else:
        with open(publications_save_path, 'w') as outFile:
            print(json.dumps(publication_dict, indent=2, sort_keys=True), file=outFile)





def find_publications(args):
    """Main function that links everything together and runs the program.
    
    Reads in the JSON config file, authors JSON file, previous publications JSON file, and checks for errors.
    Then requests publications from PubMed and builds the emails to go to each author. Then saves them emails
    and publications to file and sends emails depending on the options entered by the user. See the program 
    docstring for options details.
    
    Args:
        args (dict): args from DocOpt CLI
    
    """
    ## read in authors
    authors_dict = load_json(args["<authors_json_file>"])
    author_file_check(authors_dict)
    
    ## read in config file
    config_file = load_json(args["<config_json_file>"])
    
    ## Get inputs from config file and check them for errors.
#    json_config_inputs = dict.fromkeys(config_file_keys)
    grants, cutoff_year, affiliations, from_email, cc_email, email_template, email_subject = config_file_check(args, config_file)
    
   
        
    ## read in previous publications to ignore
    has_previous_pubs, prev_pubs = read_previous_publications(args)
            
            
    ## Get publications from PubMed and build email messages
    publication_dict, email_messages = request_pubs_and_build_emails(has_previous_pubs, prev_pubs, authors_dict, affiliations, cutoff_year, grants, from_email, email_template, email_subject, cc_email)
    
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
    save_publications_to_file(save_dir_name, publication_dict, has_previous_pubs, prev_pubs)



def main(args):
    if args["--help"]:
        print(__doc__)
    elif args["--version"]:
        print(__version__)
    elif args["<authors_json_file>"] and args["<config_json_file>"]:
        find_publications(args)
    else:
        print("Unrecognized command")               
                
                
if __name__ == "__main__":
    args = docopt.docopt(__doc__, version=str("Publication Tracker ") + __version__)
    main(args)