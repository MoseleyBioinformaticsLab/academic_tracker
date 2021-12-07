# -*- coding: utf-8 -*-
"""
This module contains helper functions.
"""

import pdfplumber
import bs4
import re
import fuzzywuzzy.fuzz
import copy


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



def create_authors_by_project_dict(config_file, authors_json_file):
    """Create the authors_by_project_dict dict from the config_file and authors_json_file.
    
    Creates a dict where the keys are the projects in the config_file and the values 
    are the authors associated with that project from authors_json_file.
    
    Args:
        config_file (dict): schema matches the JSON Project Tracking Configuration file.
        authors_json_file (dict): keys are authors and values are author attributes. Matches authors JSON schema.
        
    Returns:
        authors_by_project_dict (dict): keys are the projects in the config_file and the values are the authors associated with that project from authors_json_file.
    """
    
    authors_by_project_dict = {project:{} for project in config_file["project_descriptions"]}
    for project, project_attributes in config_file["project_descriptions"].items():
        if "authors" in project_attributes:
            for author in project_attributes["authors"]:
                if author in authors_json_file:
                    authors_by_project_dict[project][author] = copy.deepcopy(authors_json_file[author])
                else:
                    print("Warning: The author, " + author + ", in the " + project + " project of the project tracking configuration file could not be found in the authors' JSON file.")
        else:
            authors_by_project_dict[project] = copy.deepcopy(authors_json_file)
    
        for author_attr in authors_by_project_dict[project].values():
            for key in project_attributes:
                author_attr.setdefault(key, project_attributes[key])
                
    return authors_by_project_dict


def adjust_author_attributes(authors_by_project_dict, authors_json_file):
    """Modifies authors_json_file with values from authors_by_project_dict
    
    Go through the authors in authors_by_project_dict and find the lowest cutoff_year.
    Also find affiliations and grants and create a union of them across projects.
    Update the authors in authors_json_file.
    
    Args:
        authors_by_project_dict (dict): keys are the projects in the config_file and the values are the authors associated with that project from authors_json_file.
        authors_json_file (dict): keys are authors and values are author attributes. Matches authors JSON schema.
        
    Returns:
        authors_json_file (dict): keys are authors and values are author attributes. Matches authors JSON schema.
    """
    
    for author, author_attr in authors_json_file.items():
        if "cutoff_year" in author_attr:
            cutoff_year = author_attr["cutoff_year"]
        else:
            cutoff_year = 99999999
        
        if "affiliations" in author_attr:
            affiliations = set(author_attr["affiliations"])
        else:
            affiliations = set()
        
        if "grants" in author_attr:
            grants = set(author_attr["grants"])
        else:
            grants = set()
        
        for project, authors_dict in authors_by_project_dict.items():
            if author in authors_dict:
                if "cutoff_year" in authors_dict[author] and authors_dict[author]["cutoff_year"] < cutoff_year:
                    cutoff_year = authors_dict[author]["cutoff_year"]
                    
                if "affiliations" in authors_dict[author]:
                    affiliations |= set(authors_dict[author]["affiliations"])
                    
                if "grants" in authors_dict[author]:
                    grants |= set(authors_dict[author]["grants"])
                    
        affiliations = list(affiliations)
        grants = list(grants)
        author_attr["cutoff_year"] = cutoff_year
        author_attr["affiliations"] = affiliations
        author_attr["grants"] = grants
        
    return authors_json_file



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
             "PMID": regex_group_return(regex_match_return(PMID_regex, line), 0), 
             "line":line} 
             for line in lines if re.match(DOI_regex, line) and not re.match(PMCID_regex, line)]


    
def regex_match_return(regex, string_to_match):
    """Return the groups matched in the regex if the regex matches.
    
    regex is delivered to re.match() with string_to_match, and if there is a match 
    the match.groups() is returned, otherwise an empty tuple is returned.
    
    Args:
        regex (str): A string with a regular expression to be delivered to re.match().
        string_to_match (str): The string to match with the regex.
        
    Returns:
        (tuple): either the tuple of the matched groups in the regex or an empty tuple if a match wasn't found.
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
    """Look for matching authors in PubMed pub data.
    
    Goes through the author list from PubMed and tries matching to an author in 
    authors_json_file using firstname, lastname, and affiliations.
    
    Args:
        authors_json_file (dict): keys are authors and values are author attributes. Matches authors JSON schema.
        author_list (list): list of dicts where each dict is attributes of an author.
        
    Returns:
        author_list (list): either the author list with matched authors containing an additional author_id attribute, or an empty list if no authors were matched.
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
    """Look for matching authors in Crossref pub data.
    
    Goes through the author list from Crossref and tries matching to an author in 
    authors_json_file using firstname, lastname, and affiliations, or ORCID if ORCID
    is present.
    
    Args:
        authors_json_file (dict): keys are authors and values are author attributes. Matches authors JSON schema.
        author_list (list): list of dicts where each dict is attributes of an author.
        
    Returns:
        author_list (list): either the author list with matched authors containing an additional author_id attribute, or an empty list if no authors were matched.
    """
    
    ## pub.authors are dictionaries with lastname, firstname, initials, and affiliation. firstname can have initials at the end ex "Andrew P"
    publication_has_affiliated_author = False
    for author_items in author_list:
        ## If the author has no affiliation or ORCID id then go to the next.
        if not author_items["affiliation"] and not "ORCID" in author_items:
            continue
        
        if author_items["affiliation"] and "name" in author_items["affiliation"][0]:
            author_items_affiliation = author_items["affiliation"][0]["name"].lower()
        else:
            author_items_affiliation = []
        
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
                
            elif ORCID_id and "ORCID" in author_attributes and ORCID_id == author_attributes["ORCID"]:
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
    
    Args:
        config_file (dict): schema matches the JSON Project Tracking Configuration file.
        args (dict): input arguments from DocOpt.
        
    Returns:
        config_file (dict): returns the config_file with any relevant command line arguments overwritten.
    
    """
    
    overwriting_options = ["--grants", "--cutoff_year", "--from_email", "--cc_email", "--affiliations"]
    for option in overwriting_options:
        for project in config_file["project_descriptions"]:
            if args[option]:
                config_file["project_descriptions"][project][option.replace("-","")] = args[option]
                
    return config_file



## TODO are "Correction" publications unique ones? If so we need to add a special case to not filter them out.
def is_fuzzy_match_to_list(str_to_match, list_to_match):
    """True if string is a 90 or higher ratio match to any string in list, False otherwise.
    
    Args:
        str_to_match (str): string to compare with list
        list_to_match (list): list of strings to compare with str_to_match
        
    Returns:
        (bool): True if str_to_match is a match to any string in list_tp_match, False otherwise.
    """
    str_to_match = str_to_match.lower()
    list_to_match = [list_string.lower() for list_string in list_to_match]
    
    return any([fuzzywuzzy.fuzz.ratio(str_to_match, list_string) >= 90 for list_string in list_to_match])




def is_pub_in_publication_dict(pub_id, title, publication_dict, titles=[]):
    """True if pub_id is in publication_dict or title is a fuzzy match to titles in titles.
    
    Check whether the pub_id is in publication_dict. If it isn't then see if there is 
    a fuzzy match in titles. If titles is not provided then get a list of titles 
    from publication_dict.
    
    Args:
        pub_id (str): pub_id to check against in publication_dict to see if it already exists.
        title (str): title corresponding to pub_id to check against titles in publication_dict.
        publication_dict (dict): keys are pub_ids and values are pub attributes.
        titles (list): list of strings that should be titles to fuzzy match to title.
        
    Returns:
        (bool): True if the pub_id is in publication_dict or title is fuzzy matched in titles, False otherwise
    """
    
    if pub_id.lower() in publication_dict:
        return True
    
    if not titles:
        titles = [pub_attr["title"] for pub_attr in publication_dict.values()]
    
    if is_fuzzy_match_to_list(title, titles):
        return True
    else:
        return False









## 2021-12-02
## I thought the fuzzy matching was super slow so this code tried to mitigate that by classifying pub_ids and reducing the amount of titles to fuzzy match.
#def classify_pub_id(pub_id):
#    """Classify given pub_d as either DOI, PMID, or URL.
#    
#    To classify as DOI doi must be in the string. PMID must be only numbers.
#    Everything else is considered a URL.
#    
#    Args:
#        pub_id (str): pub_id to classify
#        
#    Returns:
#        (str): one of DOI, PMID, or URL
#    """
#    
#    if re.match(r".*doi.*", pub_id):
#        return "DOI"
#    elif re.match(r"\d+", pub_id):
#        return "PMID"
#    else:
#        return "URL"
#
#
#
#
#
#def classify_publication_dict_keys(publication_dict):
#    """Classify all of the keys of publication_dict as either DOI, PMID, or URL.
#    
#    Args:
#        publication_dict (dict): keys are pub_ids and values are pub attributes
#        
#    Returns:
#        key_classifier (dict): {"DOI":[], "PMID":[], "URL":[]} each key is added to the appropriate list.
#    """
#    
#    key_classifier = {"DOI":[], "PMID":[], "URL":[]}
#    
#    for pub_id in publication_dict:
#        key_classifier[classify_pub_id(pub_id)].append(pub_id)
#            
#    return key_classifier
#
#
#
#def classify_publication_dict_titles(publication_dict):
#    """Classify all of the title of publication_dict as either DOI, PMID, or URL.
#    
#    Args:
#        publication_dict (dict): keys are pub_ids and values are pub attributes
#        
#    Returns:
#        title_classifier (dict): {"DOI":[], "PMID":[], "URL":[]} each title is added to the appropriate list.
#    """
#    
#    title_classifier = {"DOI":[], "PMID":[], "URL":[]}
#
#    for pub_id, pub_attributes in publication_dict.items():
#        title_classifier[classify_pub_id(pub_id)].append(pub_attributes["title"])
#            
#    return title_classifier
#
#
#
#
#def is_pub_in_publication_dict(pub_id, title, publication_dict, title_classifier):
#    """True if pub_id is in publication_dict or title is a fuzzy match to different class titles in title_classifier.
#    
#    pub_ids can be either a DOI, a PMID, or URL. Since a publication can have all three of 
#    these and multiple DOIs and URLs simply checking that the pub_id already exists in publication_dict
#    is not enough. The title needs to be fuzzy matched with all the titles to be more confident. 
#    Since fuzzy matching is slow only titles of different classes are compared except for 
#    URLs, which is compared with all titles.
#    
#    Args:
#        pub_id (str): pub_id to check against in publication_dict to see if it already exists.
#        title (str): title corresponding to pub_id to check against titles in publication_dict.
#        publication_dict (dict): keys are pub_ids and values are pub attributes.
#        title_classifier (dict): {"DOI":[], "PMID":[], "URL":[]} each title in publication_dict should already be in this dict.
#        
#    Returns:
#        (bool): True if the pub_id is in publication_dict or title is in title_classifier, False otherwise
#    """
#    
#    if pub_id in publication_dict:
#        return True
#    
#    pub_id_class = classify_pub_id(pub_id)
#    
#    if pub_id_class == "DOI":
#        if is_fuzzy_match_to_list(title, title_classifier["PMID"]) or is_fuzzy_match_to_list(title, title_classifier["URL"]):
#            return True
#        else:
#            return False
#    
#    elif pub_id_class == "PMID":
#        if is_fuzzy_match_to_list(title, title_classifier["DOI"]) or is_fuzzy_match_to_list(title, title_classifier["URL"]):
#            return True
#        else:
#            return False
#    
#    ## DOI and PMID won't share titles or it is extremely unlikely, but URLs can so check against every title.
#    elif pub_id_class == "URL":
#        titles = [pub_attr["title"] for pub_attr in publication_dict.values()]
#        if is_fuzzy_match_to_list(title, titles):
#            return True
#        else:
#            return False
#        
#    else:
#        return False




