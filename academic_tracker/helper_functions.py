# -*- coding: utf-8 -*-
"""
This module contains helper functions.
"""

import pdfplumber
import bs4
import re
import datetime


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




def create_emails_dict(pubs_by_author_dict, authors_dict, publication_dict):
    """Create emails for each author.
    
    For each author in pubs_by_author create an email with publication citations. 
    Information in authors_dict is used to get information about the author, and 
    publication_dict is used to get information about publications. 
    
    Args:
        pubs_by_author_dict (dict): keys are author_ids that match keys in authors_dict, values are a dict of pubmed_ids that match keys in publication_dict, and values are a set of grant_ids for each pub.
        authors_dict (dict): keys and values match the authors JSON file.
        publication_dict (dict): keys and values match the publications JSON file.
        
    Returns:
        email_messages (dict): keys and values match the email JSON file.
    """
    
    # dict for email messages.
    email_messages = {"creation_date" : str(datetime.datetime.now())[0:16]}
    
    email_messages["emails"] = [{"body":replace_body_magic_words(pubs_by_author_dict[author], authors_dict[author], publication_dict),
                                 "subject":replace_subject_magic_words(authors_dict[author]),
                                 "from":authors_dict[author]["from_email"],
                                 "to":authors_dict[author]["email"],
                                 "cc":",".join([email for email in authors_dict[author]["cc_email"]]),
                                 "author":author}
                                 for author in pubs_by_author_dict]       
    
    return email_messages




def create_email_dict_for_no_PMCID_pubs(publications_with_no_PMCID_list, config_json, to_email):
    """Create an email with the publications information in it.
    
    For each publication in publications_with_no_PMCID_list add it's information 
    to the body of an email. Pull the subject, from, and cc emails from the 
    config_json, and to from to_email.
    
    Args:
        publications_with_no_PMCID_list (list): A list of dictionaries.
        [{"DOI":"publication DOI", "PMID": "publication PMID", "line":"short description of the publication", "Grants":"grants funding the publication"}]
        config_json (dict): dict with the same structure as the configuration JSON file
        
    Returns:
        email_messages (dict): keys and values match the email JSON file.
        
    """
    
    email_messages = {"creation_date" : str(datetime.datetime.now())[0:16]}
    
    pubs_string = "\n\n\n".join([dictionary["line"] + "\n\n" + 
                          "PMID: " + (dictionary["PMID"] if dictionary["PMID"] else "None") + "\n\n" + 
                          "Cited Grants:\n" + ("\n".join(dictionary["Grants"]) if dictionary["Grants"] else "None") for dictionary in publications_with_no_PMCID_list])
    
    body = config_json["email_template"]
    body = body.replace("<total_pubs>", pubs_string)
    
    email_messages["emails"] = [{"body":body,
                                 "subject":config_json["email_subject"],
                                 "from":config_json["from_email"],
                                 "to":to_email,
                                 "cc":",".join([email for email in config_json["cc_email"]])}]       
    
    return email_messages



def replace_body_magic_words(authors_pubs, authors_attributes, publication_dict):
    """Replace the magic words in email body with appropriate values.
    
    Args:
        authors_pubs (dict): A dict where the keys are publication IDs associated with the author and the values are a set of any grants cited for the publication.
        authors_attributes (dict): A dict where the keys are attributes associated with the author such as first and last name.
        publication_dict (dict): A dict where the keys are publication IDs and the values are attributes of the publication such as the authors.
        
    Returns:
        body (str): A string with the text for the body of the email to be sent to the author.
    """
    pubs_string = create_citations_for_author(authors_pubs, publication_dict)
    
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




def extract_pdf_text(path_to_pdf):
    """
    """
    
    with pdfplumber.open(path_to_pdf) as pdf:
        pdf_text = " ".join([pdf_page.extract_text() for pdf_page in pdf.pages if pdf_page.extract_text()])
#        pdf_text = " ".join(["".join([char["text"] for char in pdf_page.chars]) for pdf_page in pdf.pages])
        
    return pdf_text




def parse_pubmed_full_text_links(pubmed_html):
    """
    """
    
    ## Note that you have to change the headers so PubMed thinks you are a browser or you won't be sent the full page with full text links.
    soup = bs4.BeautifulSoup(pubmed_html, "html.parser")
    link_list = soup.find("div", class_ = "full-text-links-list")
    return [link["href"] for link in link_list.find_all("a")]



def create_citations_for_author(authors_pubs, publication_dict):
    """Create a publication citation with cited grants for each publication in authors_pubs.
    
    Args:
        authors_pubs (dict): A dict where the keys are publication IDs associated with the author and the values are a set of any grants cited for the publication.
        publication_dict (dict): A dict where the keys are publication IDs and the values are attributes of the publication such as the authors.
        
    Returns:
        (str): A string of the citations and cited grants for each publication.
    """
    
    return "\n\n\n".join([create_citation(publication_dict[pub_id]) + "\n\nCited Grants:\n" + 
                             "\n".join([grant_id for grant_id in authors_pubs[pub_id]] if authors_pubs[pub_id] else ["None"]) 
                             for pub_id in authors_pubs])



def parse_string_for_pub_info(document_string, DOI_regex, PMID_regex, PMCID_regex):
    """Pull out the DOIs and PMIDs from each line of a string.
    
    Split document_string on newline character and attempt to pull out the DOI and PMID from each line.
    Each regex is delivered to re.match(). The DOI_regex and PMID_regex are expected to have 1 group 
    that will contain the DOI and PMID when matched, respectively. If the DOI_regex is not matched 
    on the line then the line is ignored. The PMCID_regex is used to ignore lines that have a PMCID in them.
    
    Returns a list of dictionaries. Each item in the list is a line in the document_string and contains the 
    DOI and PMID found on the line.
    [{"DOI":"found DOI", "PMID": "found PMID", "line":"full text of the line where each was found"}]
    
    Args:
        document_string (str): A string that represents the contents of a document.
        DOI_regex (str): A string with a regular expression to be delivered to re.match(). This will confirm that the line has a DOI and have a group to pull out the DOI.
        PMID_regex (str): A string with a regular expression to be delivered to re.match(). Must have a group to pull out the PMID.
        PMCID_regex (str): A string with a regular expression to be delivered to re.match(). Used to ignore lines that contain a PMCID.
        
    Returns:
        (list): A list of dictionaries. A description of the keys and values are in the description of the function.
    """
    
    lines = document_string.split("\n")
#    return [{"DOI": regex_match_return(r"(?i).*doi:\s*([^\s]+\w).*", line), "PMID": regex_match_return(r"(?i).*pmid:\s*(\d+).*", line), "line":line} for line in lines if re.match(r"(?i).*doi:\s*([^\s]+\w).*", line) and not re.match(r"(?i).*pmcid:\s*(pmc\d+).*", line)]
#    [{"DOI": regex_match_return(r"(?i).*doi:\s*([^\s]+\w).*", line), "PMID": regex_match_return(r"(?i).*pmid:\s*(\d+).*", line), "line":line} for line in lines if re.match(r"(?i).*doi:.*", line) or re.match(r"(?i).*pmid:.*", line)]
    return [{"DOI": regex_match_return(DOI_regex, line), "PMID": regex_match_return(PMID_regex, line), "line":line} for line in lines if re.match(DOI_regex, line) and not re.match(PMCID_regex, line)]


    
def regex_match_return(regex, string_to_match):
    """Return the first gorup matched in the regex if the regex matches.
    
    regex is delivered to re.match() with string_to_match, and if there is a match 
    the match.group(1) is returned, otherwise an empty string is returned.
    
    Args:
        regex (str): A string with a regular expression to be delivered to re.match(). Must have a group.
        string_to_search (str): The string to match with the regex.
    """
    
    match = re.match(regex, string_to_match)
    if match:
        return match.group(1)
    else:
        return ""



def modify_pub_dict_for_saving(pub):
    """Convert pymed.PubMedArticle to a dictionary and modify it for saving.
    
    Converts a pymed.PubMedArticle to a dictionary, deletes the "xml" key, and 
    converts the "publication_date" key to a string.
    
    Args:
        pub (pymed.PubMedArticle): publication to convert to a dictionary.
        
    Returns:
        pub_dict (dict): pub converted to a dictionary. Keys are "pubmed_id", "title", "abstract", 
        "keywords", "journal", "publication_date", "authors", "methods", "conclusions", "results", "copyrights", and "doi"
    """
    
    pub_dict = pub.toDict()
        
    del pub_dict["xml"]
    pub_dict["publication_date"] = str(pub_dict["publication_date"])
    
    return pub_dict




"""
uksrc_rppr_list = [{"DOI": regex_match_return(r"(?i).*doi:\s*([^\s]+\w).*", line), "PMID": regex_match_return(r"(?i).*pmid:\s*(\d+).*", line), "line":line} for line in lines if re.match(r"(?i).*doi:.*", line) or re.match(r"(?i).*pmid:.*", line)]
uksrc_rppr_pmid = {dictionary["PMID"] for dictionary in uksrc_rppr_list}

biblio 288
uksrc 264

pmids in biblio that aren't in uksrc 
'18028363',
 '18441810',
 '18717615',
 '19418819',
 '20664816',
 '21344848',
 '21770469',
 '22776832',
 '22922135',
 '23252837',
 '23278296',
 '23293835',
 '23359620',
 '23360069',
 '23595851',
 '23752876',
 '23832638',
 '23950637',
 '24034829',
 '24083557',
 '24170970',
 '24197079',
 '24619471',
 '24795543'
"""

