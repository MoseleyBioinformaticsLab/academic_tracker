"""
This module contains the functions that read and write files.
"""


from os.path import exists
from json import loads
import json
import re
import os
from datetime import datetime
import sys


def load_json(filepath):
    """Adds error checking around loading a json file.
    
    Args:
        filepath (str): filepath to the json file
        
    Returns:
        internal_data (dict): json read from file in a dictionary
        
    """
    if exists(filepath):
        try:
            with open(filepath, "r") as f:
                internal_data = loads(f.read())
        except Exception as e:
            raise e

        return internal_data




def read_previous_publications(args):
    """Read in the previous publication json file.
    
    If the prev_pub option was given by the user then that filepath is used to read in the file
    and it is checked to make sure the json is a list and each value is a string. If the prev_pub
    option was not given then look for a "tracker-timestamp" directory in the current working 
    directory and if it has a publications.json file then read in that file. 
    If no previous publications are found then an empty dict is returned for prev_pubs.
    
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
            prev_publication_filepath = os.path.join(os.getcwd(), "tracker-"+str(latest_dir), "publications.json")
            if os.path.exists(prev_publication_filepath):
                prev_pubs = load_json(prev_publication_filepath)
                has_previous_pubs = True
            else:
                print("Error: The latest tracker directory does not have a previous publications file.")
                sys.exit()
    
    if has_previous_pubs:                
                    
        return has_previous_pubs, prev_pubs
    
    else:
        return has_previous_pubs, {}
    
    
    
    
    


def save_emails_to_file(email_messages, save_dir_name):
    """Save email_messages to "emails.json" in save_dir_name in the current working directory.
    
    Args:
        email_messages (dict): keys are author names and values are the subject, body, from, to, and cc parts of the email
        save_dir_name (str): directory name to append to the current working directory to save the emails.json file in
    
    """
    
    email_save_path = os.path.join(os.getcwd(), save_dir_name, "emails.json")
    
    with open(email_save_path, 'w') as outFile:
        print(json.dumps(email_messages, indent=2, sort_keys=True), file=outFile)

                


            


def save_publications_to_file(save_dir_name, publication_dict, prev_pubs):
    """Saves the publication_dict to "publications.json" in save_dir_name in the current working directory.
    
    prev_pubs and publication_dict will be combined before saving.
    
    Args:
        save_dir_name (str): directory name to append to the current working directory to save the publications.json file in
        publication_dict (dict): dictionary with publication ids as the keys to the dict
        prev_pubs (list): List of publication ids that are publications previously found.
    
    """
    
    publications_save_path = os.path.join(os.getcwd(), save_dir_name, "publications.json")
    
        
    prev_pubs.update(publication_dict)
    with open(publications_save_path, 'w') as outFile:
        print(json.dumps(prev_pubs, indent=2, sort_keys=True), file=outFile)



