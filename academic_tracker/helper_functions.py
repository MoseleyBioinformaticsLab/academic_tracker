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






