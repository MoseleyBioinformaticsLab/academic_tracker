# -*- coding: utf-8 -*-
"""
This module contains helper functions.
"""

import pdfplumber
import bs4
import re
import datetime
import fuzzywuzzy


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
    publication_str += " DOI:{}".format(publication["doi"])
    publication_str += " PMID:{}".format(publication["pubmed_id"])
    publication_str += " PMCID:{}".format(publication["PMCID"])
    
    return publication_str



def add_indention_to_string(string_to_indent):
    """
    """
    
    return "\n".join(["\t" + line for line in string_to_indent.split("\n")])



def create_emails_dict(authors_json_file, publication_dict, config_file):
    """Create emails for each author.
    
    For each author in pubs_by_author create an email with publication citations. 
    Information in authors_json_file is used to get information about the author, and 
    publication_dict is used to get information about publications. 
    
    Args:
        authors_json_file (dict): keys and values match the authors JSON file.
        publication_dict (dict): keys and values match the publications JSON file.
        
    Returns:
        email_messages (dict): keys and values match the email JSON file.
    """
    
    # dict for email messages.
    email_messages = {"creation_date" : str(datetime.datetime.now())[0:16]}
    email_messages["emails"] = []
    
    for project, project_attributes in config_file["project_descriptions"].items():
        if "to_email" in project_attributes:
            email_messages["emails"].append({"body":replace_body_magic_words(pubs_by_author_dict[author], authors_json_file[author], publication_dict),
                                             "subject":replace_subject_magic_words(authors_json_file[author]),
                                             "from":authors_json_file[author]["from_email"],
                                             "to":authors_json_file[author]["email"],
                                             "cc":",".join([email for email in authors_json_file[author]["cc_email"]])})
    
    email_messages["emails"] = [{"body":replace_body_magic_words(pubs_by_author_dict[author], authors_json_file[author], publication_dict),
                                 "subject":replace_subject_magic_words(authors_json_file[author]),
                                 "from":authors_json_file[author]["from_email"],
                                 "to":authors_json_file[author]["email"],
                                 "cc":",".join([email for email in authors_json_file[author]["cc_email"]]),
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
    
    lines = [line for line in document_string.split("\n") if line]
#    return [{"DOI": regex_match_return(r"(?i).*doi:\s*([^\s]+\w).*", line), "PMID": regex_match_return(r"(?i).*pmid:\s*(\d+).*", line), "line":line} for line in lines if re.match(r"(?i).*doi:\s*([^\s]+\w).*", line) and not re.match(r"(?i).*pmcid:\s*(pmc\d+).*", line)]
#    [{"DOI": regex_match_return(r"(?i).*doi:\s*([^\s]+\w).*", line), "PMID": regex_match_return(r"(?i).*pmid:\s*(\d+).*", line), "line":line} for line in lines if re.match(r"(?i).*doi:.*", line) or re.match(r"(?i).*pmid:.*", line)]
    return [{"DOI": regex_group_return(regex_match_return(DOI_regex, line), 0), 
             "PMID": regex_group_return(regex_match_return(PMID_regex, line), 0), "line":line} 
             for line in lines if re.match(DOI_regex, line) and not re.match(PMCID_regex, line)]


    
def regex_match_return(regex, string_to_match):
    """Return the groups matched in the regex if the regex matches.
    
    regex is delivered to re.match() with string_to_match, and if there is a match 
    the match.groups() is returned, otherwise an empty tuple is returned.
    
    Args:
        regex (str): A string with a regular expression to be delivered to re.match().
        string_to_match (str): The string to match with the regex.
    """
    
    match = re.match(regex, string_to_match)
    if match:
        return match.groups()
    else:
        return ()



def regex_group_return(regex_groups, group_index):
    """Return the group in the regex_groups indicated by group_index if it exists, else return empty string.
    
    If group_index is out of range of the regex_groups an empty string is retruned.
    
    Args:
        regex_groups (tuple): A tuple returned from a matched regex.groups() call.
        group_number (int): The index of the regex_groups to return.
        
    Returns:
        (str): Either emtpy string or the group string matched by the regex.
    """
    
    if group_index < len(regex_groups) and regex_groups[group_index]:
        return regex_groups[group_index]
    else:
        return ""



def regex_search_return(regex, string_to_search):
    """Return the groups matched in the regex if the regex matches.
    
    regex is delivered to re.search() with string_to_search, and if there is a match 
    the match.groups() is returned, otherwise an empty tuple is returned.
    
    Args:
        regex (str): A string with a regular expression to be delivered to re.search().
        string_to_search (str): The string to match with the regex.
    """
    
    match = re.search(regex, string_to_search)
    if match:
        return match.groups()
    else:
        return ()



    
    
def match_authors_in_pub_PubMed(authors_json_file, author_list):
    """
    """
    
    ## pub.authors are dictionaries with lastname, firstname, initials, and affiliation. firstname can have initials at the end ex "Andrew P"
    publication_has_affiliated_author = False
    for author_items in author_list:
        author_items_affiliation = str(author_items.get("affiliation")).lower()
        author_items_first_name = str(author_items.get("firstname")).lower()
        author_items_last_name = str(author_items.get("lastname")).lower()
        
        for author, author_attributes in authors_json_file.items():
        
            ## Match the author's first and last name and then match affiliations.
            ## The first name is matched with an additional .* to try and allow for the addition of initials, but this could cause bad matches. 
            ## For example the name Hu will match Hubert. Counting on the last name to reduce errors.
            ## Note that the PubMed query will return publications where the author is just a collaborater, so not finding a match in the authors isn't uncommon.
            if re.match(author_attributes["first_name"].lower() + ".*", author_items_first_name) and author_attributes["last_name"].lower() == author_items_last_name:
                ## affiliations are sets of strings so the intersection should have at least 1 string for a match.
                
                if any([affiliation.lower() in author_items_affiliation for affiliation in author_attributes["affiliations"]]):
                    publication_has_affiliated_author = True
                    author_items["author_id"] = author
                    break
                
    if publication_has_affiliated_author:
        return author_list
    else:
        return []




def match_authors_in_pub_Crossref(authors_json_file, author_list):
    """
    """
    
    ## pub.authors are dictionaries with lastname, firstname, initials, and affiliation. firstname can have initials at the end ex "Andrew P"
    publication_has_affiliated_author = False
    for author_items in author_list:
        author_items_affiliation = author_items["affiliation"][0]["name"].lower()
        if "given" in author_items:
            author_items_first_name = str(author_items.get("given")).lower()
        else:
            author_items_first_name = ""
        author_items_last_name = str(author_items.get("family")).lower()
        
        if "ORCID" in author_items:
            ORCID_id = regex_search_return(r"(\d{4}-\d{4}-\d{4}-\d{3}[0,1,2,3,4,5,6,7,8,9,X])", author_items["ORCID"])[0]
        else:
            ORCID_id = ""
        
        for author, author_attributes in authors_json_file.items():
        
            ## Match the author's first and last name and then match affiliations.
            ## The first name is matched with an additional .* to try and allow for the addition of initials, but this could cause bad matches. 
            ## For example the name Hu will match Hubert. Counting on the last name to reduce errors.
            ## Note that the PubMed query will return publications where the author is just a collaborater, so not finding a match in the authors isn't uncommon.
            if re.match(author_attributes["first_name"].lower() + ".*", author_items_first_name) and author_attributes["last_name"].lower() == author_items_last_name:
                ## affiliations are sets of strings so the intersection should have at least 1 string for a match.
                if any([affiliation.lower() in author_items_affiliation for affiliation in author_attributes["affiliations"]]):
                    publication_has_affiliated_author = True
                    author_items["author_id"] = author
                    break
                
            elif ORCID_id and ORCID_id == author_attributes["ORCID"]:
                publication_has_affiliated_author = True
                author_items["author_id"] = author
                break
                
    if publication_has_affiliated_author:
        return author_list
    else:
        return []




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
    
    pub_dict["grants"] = [grant.text for grant in pub.xml.findall(".//GrantID")]
    PMC_id_elements = pub.xml.findall(".//ArticleId[@IdType='pmc']")
    if PMC_id_elements:
        pub_dict["PMCID"] = PMC_id_elements[0].text
    else:
        pub_dict["PMCID"] = None
        
    del pub_dict["xml"]
    pub_dict["publication_date"] = {"year":pub_dict["publication_date"].year, "month":pub_dict["publication_date"].month, "day":pub_dict["publication_date"].day}
    pub_dict["pubmed_id"] = pub_dict["pubmed_id"].split("\n")[0]
    
    return pub_dict




def overwrite_config_with_CLI(config_file, args):
    """Overwrite keys in config_file if command line options were used.
    
    """
    
    overwriting_options = ["--grants", "--cutoff_year", "--from_email", "--cc_email", "--affiliations"]
    for option in overwriting_options:
        for project in config_file["project_descriptions"]:
            if args[option]:
                config_file["project_descriptions"][project][option.replace("-","")] = args[option]
                
    return config_file



## TODO are "Correction" publications unique ones? If so we need to add a special case to not filter them out.
def is_fuzzy_match_to_list(str_to_match, list_to_match):
    """
    """
    str_to_match = str_to_match.lower()
    list_to_match = [list_string.lower() for list_string in list_to_match]
    
    return any([fuzzywuzzy.fuzz.ratio(str_to_match, list_string) >= 90 for list_string in list_to_match])




def classify_pub_id(pub_id):
    """
    """
    
    if re.match(r".*doi.*", pub_id):
        return "DOI"
    elif re.match(r"\d+", pub_id):
        return "PMID"
    else:
        return "URL"





def classify_publication_dict_keys(publication_dict):
    """
    """
    
    key_classifier = {"DOI":[], "PMID":[], "URL":[]}
    
    for pub_id in publication_dict:
        key_classifier[classify_pub_id(pub_id)].append(pub_id)
            
    return key_classifier



def classify_publication_dict_titles(publication_dict):
    """
    """
    
    title_classifier = {"DOI":[], "PMID":[], "URL":[]}

    for pub_id, pub_attributes in publication_dict.items():
        title_classifier[classify_pub_id(pub_id)].append(pub_attributes["title"])
            
    return title_classifier




def is_pub_in_publication_dict(pub_id, publication_dict, title_classifier):
    """
    """
    
    if pub_id in publication_dict:
        return True
    
    pub_id_class = classify_pub_id(pub_id)
    
    if pub_id_class == "DOI":
        if is_fuzzy_match_to_list(pub_id, title_classifier["PMID"]) or is_fuzzy_match_to_list(pub_id, title_classifier["URL"]):
            return True
        else:
            return False
    
    elif pub_id_class == "PMID":
        if is_fuzzy_match_to_list(pub_id, title_classifier["DOI"]) or is_fuzzy_match_to_list(pub_id, title_classifier["URL"]):
            return True
        else:
            return False
    
    elif pub_id_class == "URL":
        if is_fuzzy_match_to_list(pub_id, title_classifier["PMID"]) or is_fuzzy_match_to_list(pub_id, title_classifier["DOI"]):
            return True
        else:
            return False
        
    else:
        return False




