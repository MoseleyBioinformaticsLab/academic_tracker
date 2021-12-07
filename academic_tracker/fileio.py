"""
This module contains the functions that read and write files.
"""


import os.path
import json
import re
import os
import datetime
import sys
import docx
from . import emails_and_reports


def load_json(filepath):
    """Adds error checking around loading a json file.
    
    Args:
        filepath (str): filepath to the json file
        
    Returns:
        internal_data (dict): json read from file in a dictionary
    """
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                internal_data = json.loads(f.read())
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
            current_day = str(datetime.datetime.now())[2:10].replace("-","")
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
    """Save email_messages to "emails.json" and "emails.txt" in save_dir_name in the current working directory.
    
    Args:
        email_messages (dict): keys are author names and values are the subject, body, from, to, and cc parts of the email
        save_dir_name (str): directory name to append to the current working directory to save the emails.json file in
    """
    
    email_save_path = os.path.join(os.getcwd(), save_dir_name, "emails.json")
    
    with open(email_save_path, 'w') as outFile:
        print(json.dumps(email_messages, indent=2, sort_keys=True), file=outFile)
        
    email_save_path = os.path.join(os.getcwd(), save_dir_name, "emails.txt")
    
    with open(email_save_path, 'wb') as outFile:
        save_string = "\n\n\n".join(["Subject: " + email_parts["subject"] + "\n" + 
                                   "To: " + email_parts["to"] + "\n" +
                                   "From: " + email_parts["subject"] + "\n" + 
                                   "CC: " + email_parts["cc"] + "\n" + 
                                   "Body:\n" + email_parts["body"] for email_parts in email_messages["emails"]])
        outFile.write(save_string.encode("utf-8"))

                
            


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




def save_new_pubs_to_file(publication_dict, pubs_by_author_dict, save_dir_name):
    """
    """
    
    save_path = os.path.join(os.getcwd(), save_dir_name, "new_pubs_by_author.txt")
    
    text_to_save = "\n\n".join([author + ":\n" + emails_and_reports.add_indention_to_string(emails_and_reports.create_citations_for_author(pubs_by_author_dict[author], publication_dict)) for author in pubs_by_author_dict])
    
    with open(save_path, 'wb') as outFile:
        outFile.write(text_to_save.encode("utf-8"))



def save_project_reports_to_file(publication_dict, save_dir_name, project_dicts):
    """Creates one text file with all projects and thier associated authors in it.
    
    Loops through the project_dicts and grabs publication information for each 
    author from publication_dict. Ultimately saves a file named summary_report.txt 
    into the save_dir_name of the current working directory.
    
    Args:
        publication_dict (dict): dictionary with publication ids as the keys, schema matches the publications JSON file
        pubs_by_author_dict (dict): dictionary where the keys are authors and the values are a dictionary of pub_ids with thier associated grants.
        project_dicts(dict): dictionary where the keys are project names and the values are attributes for the projects such as the authors associated with the project.
    """
    
    save_path = os.path.join(os.getcwd(), save_dir_name, "summary_report.txt")
    
    pubs_by_author_dict = emails_and_reports.create_pubs_by_author_dict(publication_dict)
    
    text_to_save = "\n\n\n\n".join([project + ":\n" + emails_and_reports.create_indented_project_report(project_dict, pubs_by_author_dict, publication_dict) for project, project_dict in project_dicts.items()])
            
    
    with open(save_path, 'wb') as outFile:
        outFile.write(text_to_save.encode("utf-8"))
        
        


def read_text_from_docx(doc_path):
    """Open docx file at doc_path and read contents into a string.
    
    Args:
        doc_path (str): path to docx file.
        
    Returns:
        (str): A string of the contents of the docx file. Each line concatenated with a newline character.
    """
    
    ## https://stackoverflow.com/questions/25228106/how-to-extract-text-from-an-existing-docx-file-using-python-docx
    if os.path.exists(doc_path):
        try:
            document = docx.Document(doc_path)
            return u"\n".join([u"".join([r.text for r in paragraph._element.xpath(".//w:t")]) for paragraph in document.paragraphs])
        except Exception as e:
            raise e



def read_text_from_txt(doc_path):
    """Open txt or csv file at doc_path and read contents into a string.
    
    Args:
        doc_path (str): path to txt or csv file.
        
    Returns:
        (str): A string of the contents of the txt or csv file. Each line concatenated with a newline character. 
    """
    
    if os.path.exists(doc_path):
        try:
            with open(doc_path, encoding = "utf-8") as document:
                lines = document.readlines()
        except Exception as e:
            raise e
        
        return "".join(lines)

    
#def read_text_from_csv(doc_path):
#    """
#    """
#    
#    with open(doc_path) as csvfile:
#        reader = csv.reader(csvfile)
#        doc_string = "\n".join([row[0] for row in reader])
#    
#    return doc_string
        




