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
    
    """
    pubs_string = "\n\n\n".join([create_citation(publication_dict[pub_id]) + "\n\nCited Grants:\n" + 
                                     "\n".join([grant_id for grant_id in authors_pubs[pub_id]] if authors_pubs[pub_id] else ["None"]) 
                                     for pub_id in authors_pubs])
    
    body = authors_attributes["email_template"]
    body = body.replace("<total_pubs>", pubs_string)
    body = body.replace("<author_first_name>", authors_attributes["first_name"])
    body = body.replace("<author_last_name>", authors_attributes["last_name"])


