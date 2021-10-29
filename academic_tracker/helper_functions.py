# -*- coding: utf-8 -*-
"""
This module contains helper functions.
"""


def create_citation(publication):
    """Build a human readable string describing the publication.
    
    Args:
        publication (dict): dictionary of a publication from PubMed's API
        
    Returns:
        publication_str (str): human readable string with authors names, publication date, title, journal, DOI, and PubMed id
    """
    publication_str = ""

    publication_str += ", ".join([auth["lastname"] + " " + auth["initials"] for auth in publication["authors"] if auth["lastname"] and auth["initials"]]) + "."
    publication_str += " {}.".format(publication["publication_date"][:4])
    publication_str += " {}.".format(publication["title"])
    publication_str += " {}.".format(publication["journal"])
    publication_str += " {}".format(publication["doi"])
    publication_str += " PMID:{}".format(publication["pubmed_id"].split("\n")[0])
    
    return publication_str



def replace_body_magic_words(authors_pubs, authors_attributes, publication_dict):
    """Replace the magic words in email body with appropriate values.
    
    Args:
        authors_pubs (dict): A dict where the keys are publication IDs associated with the author and the values are a set of any grants cited for the publication.
        authors_attributes (dict): A dict where the keys are attributes associated with the author such as first and last name.
        publication_dict (dict): A dict where the keys are publication IDs and the values are attributes of the publication such as the authors.
        
    Returns:
        body (str): A string with the text for the body of the email to be sent to the author.
    """
    pubs_string = "\n\n\n".join([create_citation(publication_dict[pub_id]) + "\n\nCited Grants:\n" + 
                                     "\n".join([grant_id for grant_id in authors_pubs[pub_id]] if authors_pubs[pub_id] else ["None"]) 
                                     for pub_id in authors_pubs])
    
    body = authors_attributes["email_template"]
    body = body.replace("<total_pubs>", pubs_string)
    body = body.replace("<author_first_name>", authors_attributes["first_name"])
    body = body.replace("<author_last_name>", authors_attributes["last_name"])
    
    return body




def replace_subject_magic_words(authors_attributes):
    """Replace the magic words in email subject with appropriate values.
    
    Args:
        authors_attributes (dict): A dict where the keys are attributes associated with the author such as first and last name.
        
    Returns:
        subject (str): A string with the text for the subject of the email to be sent to the author.
    """
    subject = authors_attributes["email_subject"]
    subject = subject.replace("<author_first_name>", authors_attributes["first_name"])
    subject = subject.replace("<author_last_name>", authors_attributes["last_name"])
    
    return subject