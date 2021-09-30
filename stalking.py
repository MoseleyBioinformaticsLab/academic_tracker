"""   
    
Usage:
    stalker.py <config_json_file> <authors_json_file> [options]
    
Options:
    -h --help                         Show this screen.
    --version                         Show version.
    --test                            Generate pubs and email texts, but do not send emails.
    --grants=<nums>...                Grant numbers to filter publications by. Must be a comma separated list with no spaces.
    --cutoff-year=<num>               YYYY year before which to ignore publications.
    --from_email=<email>              Send authors email from provided email address.
    --cc_email=<emails>...            Email addresses to cc on the sent emails. Must be a comma separated list with no spaces.
    --prev-pub=<file-path>            Filepath to json or csv with publication ids to ignore.
    --affiliations=<affiliations>...  An affiliation to filter publications by. Must be a comma separated list with no spaces.
    
    
"""

pub_med_url = "https://pubmed.ncbi.nlm.nih.gov/"
config_file_keys = ["grants", "cutoff_year", "affiliations", "from_email", "cc_email", "email_template", "email_subject"]
author_file_keys = ["name", "email"]
email_word_replacements = {"<author>":"author", "<from_email>":"from_email"}

## TODO add Sphinx style comments to each function.
## TODO check that cutoff_year is between 1900 and 3000.

"""
Are all fields in config required?
How much error checking with values in config and CLI?
If cutoff_year is not an int, ignore or exit?
If from_email and cc_emails don't look like emails, error?

What to do about publications with no grant info on PubMed? Christian was hand checking.

Format of previous publications JSON? Is list okay?
Format of the authors JSON file? Repeat name in values? How hard to check author's email? Possible regex .*@.*\..*?

Strucutre of publication and email files in the directories?

If there are multiple tracker dirs and the largest doesn't have a previous publications file, go to second largest or ignore?

Any other variables in the email format string? <author> and <from_email> already.

Is exiting with sys.exit() okay for invalid input?
How big of a timestamp? Include hours and minutes? 
Should default behavior be to combine previous publications and new publications when saving? Option to save only new?

"""



from collections import OrderedDict
from urllib.request import urlopen
from urllib.error import HTTPError
from os.path import join
import docopt
from ._version import __version__
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
    """

    :param publication:
    :return:
    """
    publication_str = ""

    publication_str += ", ".join([auth["lastname"] + " " + auth["initials"] for auth in publication[1]["authors"]]) + "."
    publication_str += " {}.".format(publication[1]["publication_date"][:4])
    publication_str += " {}.".format(publication[1]["title"])
    publication_str += " {}.".format(publication[1]["journal"])
    publication_str += " {}".format(publication[1]["doi"])
    publication_str += " PMID:{}".format(publication[1]["pubmed_id"].split("\n")[0])

    return publication_str


def config_file_check(config_json):
    
    ## Go through each possible key and handle them appropriately.
    ## See if it exists or not and that it is the right type, then do further handling or print an error.
    
    ## If grants is not a list make it one.
    if not "grants" in config_json:
        grants = None
    else:
        if type(config_json["grants"]) == list:
            if any(type(value) != str for value in  config_json["grants"]):
                print("Error: Non-string type value in \"grants\" list in JSON configuration file.")
                sys.exit()
            
            else:
                grants = config_json["grants"]
        elif type(config_json["grants"]) == str:
            grants = [config_json["grants"]]
        else:
            print("Error: Non-string or list type value for \"grants\" in JSON configuration file.")
            sys.exit()
            
    
    ## Make sure cutoff_year con be turned into an int.        
    if not "cutoff_year" in config_json:
        cutoff_year = 0
    else:
        if type(config_json["cutoff_year"]) != str:
            print("Error: Non-string type value for \"cutoff_year\" in JSON configuration file.")
            sys.exit()
        
        else:
            cutoff_year = config_json["cutoff_year"]
            try:
                cutoff_year = int(cutoff_year)
            except:
                cutoff_year = 0
                print("Warning: \"cutoff_year\" in JSON configuration file is not an int, it will be ignored.")
            
    
    ## If affiliations is not a list make it one.        
    if not "affiliations" in config_json:
        affiliations = None
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
            
 ## TODO either require at least 1 string in affiliations or add code to skip the filter.           
    
    if not "from_email" in config_json:
        from_email = None
    else:
        if type(config_json["from_email"]) != str:
            print("Error: Non-string type value for \"from_email\" in JSON configuration file.")
            sys.exit()
        
        else:
            from_email = config_json["from_email"]
            if not re.match(".*@.*\..*", from_email):
                print("Error: The \"from_email\" email attribute in the JSON configuration file does not look like an email.")
                sys.exit()
        
        
    
    ## If cc_email is not a list make it one.        
    if not "cc_email" in config_json:
        cc_email = None
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
            
        if any(not re.match(".*@.*\..*", email) for email in cc_email):
                print("Error: An email in the \"cc_email\" attribute in the JSON configuration file does not look like an email.")
                sys.exit()
            
            
    
    if not "email_template" in config_json:
        email_template = None
    else:
        if type(config_json["email_template"]) != str:
            print("Error: Non-string type value for \"email_template\" in JSON configuration file.")
            sys.exit()
        
        else:
            email_template = config_json["email_template"]
        
        
    
    if not "email_subject" in config_json:
        email_subject = None
    else:
        if type(config_json["email_subject"]) != str:
            print("Error: Non-string type value for \"email_subject\" in JSON configuration file.")
            sys.exit()
        
        else:
            email_subject = config_json["email_subject"]
        
        
        
        
    return grants, cutoff_year, affiliations, from_email, cc_email, email_template, email_subject
            



def author_file_check(authors_dict):
    
    if type(authors_dict) != dict:
        print("Error: Non-dcit type value for authors JSON file.")
        sys.exit()
    
    elif any(type(value) != dict for value in authors_dict.values()):
            print("Error: Non-dict type value in authors dict.")
            sys.exit()
            
            
    for author, author_attributes  in authors_dict:
        ## Make sure each author has the appropriate attributes.
        if len(set(author_file_keys) - set(author_attributes.keys())) > 0:
            print("Error: Author missing attribute in authors JSON file.")
            sys.exit()
        
        ## Make sure each attribute we expect has the appropriate value.
        ## For now assuming each attribute just needs to be a string.
        for attribute_name, attribute_value in author_attributes:
            if attribute_name in author_file_keys:
                if type(attribute_value) != str:
                    print("Error: Non-string type value in an author's attribute in the authors JSON file.")
                    sys.exit()
                
                ## The name attribute should be the same as the author key.
                if attribute_name == "name" and not attribute_value == author:
                    print("Error: The author's, " + author + ", name attribute does not match his key value.")
                    sys.exit()
                    
                ## The email attribute needs to look like an email.
                if attribute_name == "email" and not re.match(".*@.*\..*", attribute_value):
                    print("Error: The author's, " + author + ", email attribute does not look like an email.")
                    sys.exit()
                    




                

def find_publications(args):
    
    
    # dicts to store which publications had grant info on pubmed page and which need to be checked by hand.
    # key is author and value is a list of publication ids
    grant_dict = {}
    no_grant_dict = {}
    
    # dict for email messages. keys are authors and values are the email message
    email_messages = {}
    
    ## read in authors
    authors_dict = load_json(args["<authors_json_file>"])
    author_file_check(authors_dict)
    
    ## read in config file
    config_file = load_json(args["<config_json_file"])
    
    ## Get inputs from config file and check them for errors.
    grants, cutoff_year, affiliations, from_email, cc_email, email_template, email_subject = config_file_check(config_file)
    
    
    ########################
    ## Overwrite inputs if there are command line options
    ########################
    
    if args["--grants"]:
        grants = args["--grants"].split(",")
        
    if args["--cutoff_year"]:
        cutoff_year = args["--cutoff_year"]
        try:
            cutoff_year = int(cutoff_year)
        except:
            cutoff_year = 0
            print("Warning: \"cutoff_year\" option is not an int, it will be ignored.")
        
    if args["--affiliations"]:
        affiliations = args["--affiliations"].lower().split(",")
    
    if args["--from_email"]:
        from_email = args["--from_email"]
        if not re.match(".*@.*\..*", from_email):
            print("Error: The \"from_email\" option does not look like an email.")
            sys.exit()
        
    if args["--cc_email"]:
        cc_email = args["--cc_email"].split(",")
        if any(not re.match(".*@.*\..*", email) for email in cc_email):
            print("Error: An email in the \"cc_email\" option does not look like an email.")
            sys.exit()
        
    
    ##########################
    ## read in previous publications to ignore
    #########################
    has_previous_pubs = False
    if args["--prev_pub"]:
        prev_pubs = load_json(args["--prev_pub"])
        has_previous_pubs = True
                            
    else:
        dir_contents = os.listdir()
        ## find all directories matching the tracker directory structure and convert the timestamps to ints to find the largest one.
        tracker_dirs = [int(re.match(r"tracker-(\d{6})", folder).group(1)) for folder in dir_contents if re.match(r"tracker-(\d{6})", folder)]
        if len(tracker_dirs) > 0:
            latest_dir = max(tracker_dirs)
            prev_publication_filepath = os.path.join(os.getcwd(), "tracker-"+str(latest_dir), "publications", "publications.json")
            prev_pubs = load_json(prev_publication_filepath)
            has_previous_pubs = True
    
    if has_previous_pubs:    
        ## Make sure the previous publication file is the format we expect.
        if type(prev_pubs) != list:
            print("Error: Non-list type value for the previous publications JSON.")
            sys.exit()
        
        elif any(type(value) != str for value in prev_pubs):
            print("Error: Non-string type value in previous publications list.")
            sys.exit()
            
        else:
            for value in prev_pubs:
                try:
                    int(value)
                except:
                    print("Error: Non-numerical value in previous publications list.")
                    sys.exit()
            
            
            
            
    
    
    # initiate PubMed API
    pubmed = PubMed(tool="Publication_Tracker")

    publication_dict = dict()

    ########################
    # loop through list of authors and request a list of their publications
    ########################
    for author in authors_dict:
        author_has_pubs = False
        publications = pubmed.query(author, max_results=500)
        for pub in publications:
            
            ## Only proceed with publications that have at least one author with an affiliation that is in the given affiliations.
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
            
                    # sort publications by whether they have grant info on the pubmed page or not
                    if any(grant_id in url_str for grant_id in grants):
                        if author not in grant_dict:
                            grant_dict[author] = [pub_id]
                        else:
                            grant_dict[author].append(pub_id)
                            
                            
                    else:
                        if author not in no_grant_dict:
                            no_grant_dict[author] = [pub_id]
                        else:
                            no_grant_dict[author].append(pub_id)
                        
        # don't piss off NCBI
        sleep(1)
        
        ################################
        ## build email message for the author
        ###############################
        
        
        
        
        if author_has_pubs:
            message = "Hey " + author + ",\n\nThese are the publications I was able to find on PubMed. Are any missing?"
            if author in grant_dict:
                message += "\nWith Grant Info:\n\n"
                for pub_id in grant_dict[author]:
                    message += create_citation(publication_dict[pub_id]) + "\n"
            
            if author in no_grant_dict:
                message += "\nWithout Grant Info:\n\n"
                for pub_id in no_grant_dict[author]:
                    message += create_citation(publication_dict[pub_id]) + "\n"
                
            message += "\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator (" + args["-e"] + ")."
            
            email_messages[author] = message
        
        

    # convert author dict to list, it was only a dict to get unique names easily.
    for key in publication_dict.keys():
        publication_dict[key][0] = list(publication_dict[key][0])

    publication_dict = OrderedDict(sorted(publication_dict.items(), key=lambda x: x[1][1]["publication_date"], reverse=True))
    
    
    ######################
    ## save email messages to file
    ######################
    if args["--test"]:
        save_dir_name = "tracker-test-" + str(datetime.now())[2:10].replace("-","")
        os.mkdir(save_dir_name)
        email_save_path = os.path.join(os.getcwd(), save_dir_name, "emails.txt")
    else:
        save_dir_name = "tracker-" + str(datetime.now())[2:10].replace("-","")
        os.mkdir(save_dir_name)
        email_save_path = os.path.join(os.getcwd(), save_dir_name, "emails.txt")
    
    with open(email_save_path, "w") as email_file:
        for author, message in email_messages.items():
            email_file.write(message + "\n\n")
            
    
    #############
    ## send emails
    #############
    if not args["--test"]:
        # build and send each message by looping over the email_messages dict
        cc_string = ""
        for email in cc_email:
            cc_string += email + ","
        for author, message in email_messages.items():
            msg = EmailMessage()
            msg["Subject"] = "Latest PubMed Publications"
            msg["From"] = args["-e"]
            msg["To"] = authors_dict[author]["email"]
            msg["Cc"] = cc_string
            msg.set_content(message)
            
            sendmail_location = "/usr/sbin/sendmail"
            subprocess.run([sendmail_location, "-t", "-oi"], input=msg.as_bytes())
    
    
    
    
    ############
    ## combine previous and new publications lists and save
    ############
    publications_save_path = os.path.join(os.getcwd(), save_dir_name, "publications.json")
        
    if has_previous_pubs: 
        with open(publications_save_path, 'w') as outFile:
            print(json.dumps(prev_pubs + list(publication_dict.keys()), indent=2, sort_keys=True), file=outFile)
    else:
        with open(publications_save_path, 'w') as outFile:
            print(json.dumps(list(publication_dict.keys()), indent=2, sort_keys=True), file=outFile)



def main(args):
    if args["--help"]:
        print(__doc__)
    elif args["--version"]:
        print(__version__)
    elif args["<authors_file>"]:
        find_publications(args)
    else:
        print("Unrecognized command")               
                
                
if __name__ == "__main__":
    args = docopt.docopt(__doc__, version=str("PubMed Pub Grabber ") + __version__)
    main(args)