"""
Fileio
~~~~~~

This module contains the functions that read and write files.
"""


import re
import os
import sys
import json

import docx
import pandas

from . import helper_functions



def load_json(filepath):
    """Adds error checking around loading a json file.
    
    Args:
        filepath (str): filepath to the json file
        
    Returns:
        internal_data (dict): json read from file in a dictionary
        
    Raises:
        Exception: If file opening has a problem will raise an exception.
    """
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                internal_data = json.loads(f.read())
        except Exception as e:
            raise e

        return internal_data
    else:
        helper_functions.vprint("No such file: " + filepath)
        sys.exit()




def read_previous_publications(filepath):
    """Read in the previous publication json file.
    
    If the prev_pub option was given by the user then that filepath is used to read in the file
    and it is checked to make sure the json is a list and each value is a string. If the prev_pub
    option was not given then look for a "tracker-timestamp" directory in the current working 
    directory and if it has a publications.json file then read in that file. 
    If no previous publications are found then an empty dict is returned for prev_pubs.
    
    Args:
        filepath (str or None): path to the publications JSON to read in.
        
    Returns:
        has_previous_pubs (bool): True means that a previous publications file was found
        prev_pubs (dict): dict where keys are publication ids and values are a dict of publication attributes
    """
    
    has_previous_pubs = False
    if filepath:
        
        if filepath.lower() == "ignore":
            return False, {}
        
        prev_pubs = load_json(filepath)
        has_previous_pubs = True
                            
    else:
        dir_contents = os.listdir()
        ## find all directories matching the tracker directory structure and convert the timestamps to ints to find the largest one.
        tracker_dirs = [int(re.match(r"tracker-(\d{10})", folder).group(1)) for folder in dir_contents if re.match(r"tracker-(\d{10})", folder)]
        if len(tracker_dirs) > 0:
            tracker_dirs.sort(reverse=True)
            for latest_dir in tracker_dirs:
                prev_publication_filepath = os.path.join(os.getcwd(), "tracker-"+str(latest_dir), "publications.json")
                if os.path.exists(prev_publication_filepath):
                    prev_pubs = load_json(prev_publication_filepath)
                    has_previous_pubs = True
                    break
    
    if has_previous_pubs:                
                    
        return has_previous_pubs, prev_pubs
    
    else:
        return has_previous_pubs, {}
    
    
    
    

def save_emails_to_file(email_messages, save_dir_name):
    """Save email_messages to "emails.json" in save_dir_name in the current working directory.
    
    Args:
        email_messages (dict): keys are author names and values are the of the email
        save_dir_name (str): directory name to append to the current working directory to save the emails.json file in
    """
    
    email_save_path = os.path.join(os.getcwd(), save_dir_name, "emails.json")
    
    with open(email_save_path, 'w') as outFile:
        print(json.dumps(email_messages, indent=2, sort_keys=False), file=outFile)
        
            


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

        
        

def read_text_from_docx(doc_path):
    """Open docx file at doc_path and read contents into a string.
    
    Args:
        doc_path (str): path to docx file.
        
    Returns:
        (str): A string of the contents of the docx file. Each line concatenated with a newline character.
    
    Raises:
        Exception: If file opening has a problem will raise an exception.
    """
    
    ## https://stackoverflow.com/questions/25228106/how-to-extract-text-from-an-existing-docx-file-using-python-docx
    if os.path.exists(doc_path):
        try:
            document = docx.Document(doc_path)
            return u"\n".join([u"".join([r.text for r in paragraph._element.xpath(".//w:t")]) for paragraph in document.paragraphs])
        except Exception as e:
            raise e
    else:
        helper_functions.vprint("No such file: " + doc_path)
        sys.exit()



def read_text_from_txt(doc_path):
    """Open txt or csv file at doc_path and read contents into a string.
    
    Args:
        doc_path (str): path to txt or csv file.
        
    Returns:
        (str): A string of the contents of the txt or csv file. Each line concatenated with a newline character. 
    
    Raises:
        Exception: If file opening has a problem will raise an exception.
    """
    
    if os.path.exists(doc_path):
        try:
            with open(doc_path, encoding = "utf-8") as document:
                lines = document.readlines()
        except Exception as e:
            raise e
        
        return "".join(lines)
    else:
        helper_functions.vprint("No such file: " + doc_path)
        sys.exit()
    

def read_csv(doc_path):
    """Read csv into a pandas dataframe.
    
    Args:
        doc_path (str): path to the csv file to read in.
        
    Returns:
        df (DataFrame): Pandas dataframe of the csv contents.
    
    Raises:
        Exception: If file opening has a problem will raise an exception.
    """
    
    if os.path.exists(doc_path):
        try:
            df = pandas.read_csv(doc_path)
        except Exception as e:
            raise e
        
        return df
    else:
        helper_functions.vprint("No such file: " + doc_path)
        sys.exit()

         
    

def save_string_to_file(save_dir_name, file_name, text_to_save):
    """Save a string to file.
    
    Args:
        save_dir_name (str): directory in the current working directory to save the string to.
        file_name (str): string to name the file.
        text_to_save (str): the string to put in the file contents.
    """
    
    save_path = os.path.join(os.getcwd(), save_dir_name, file_name)
    
    with open(save_path, 'wb') as outFile:
        outFile.write(text_to_save.encode("utf-8"))
    
    

def save_json_to_file(save_dir_name, file_name, json_dict, sort_keys=True):
    """Saves the json_dict to file_name in save_dir_name in the current working directory.
    
    Args:
        save_dir_name (str): directory name to append to the current working directory to save the json_dict in.
        file_name (str): the name to give the file, should have '.json' as the extension.
        json_dict (dict or list): data to save to file.
        sort_keys (bool): passed to json.dumps, if True sort the dictionary keys before saving.
    """
    
    save_path = os.path.join(os.getcwd(), save_dir_name, file_name)
    
    with open(save_path, 'w') as outFile:
        print(json.dumps(json_dict, indent=2, sort_keys=sort_keys), file=outFile)

