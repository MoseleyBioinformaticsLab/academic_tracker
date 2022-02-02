# -*- coding: utf-8 -*-
"""
This module contains helper functions.
"""

import re
import copy

import fuzzywuzzy.fuzz



def create_authors_by_project_dict(config_dict):
    """Create the authors_by_project_dict dict from the config_dict.
    
    Creates a dict where the keys are the projects in the config_dict and the values
    are the authors associated with that project from config_dict["Authors"].
    
    Args:
        config_dict (dict): schema matches the JSON Project Tracking Configuration file.
        
    Returns:
        authors_by_project_dict (dict): keys are the projects in the config_dict and the values are the authors associated with that project from config_dict["Authors"].
    """
    
    authors_by_project_dict = {project:{} for project in config_dict["project_descriptions"]}
    for project, project_attributes in config_dict["project_descriptions"].items():
        if "authors" in project_attributes:
            for author in project_attributes["authors"]:
                if author in config_dict["Authors"]:
                    authors_by_project_dict[project][author] = copy.deepcopy(config_dict["Authors"][author])
                else:
                    print("Warning: The author, " + author + ", in the " + project + " project of the project tracking configuration file could not be found in the Authors section of the Configuration JSON file.")
        else:
            authors_by_project_dict[project] = copy.deepcopy(config_dict["Authors"])
    
        for author_attr in authors_by_project_dict[project].values():
            for key in project_attributes:
                author_attr.setdefault(key, project_attributes[key])
                
    return authors_by_project_dict


def adjust_author_attributes(authors_by_project_dict, config_dict):
    """Modifies config_dict with values from authors_by_project_dict
    
    Go through the authors in authors_by_project_dict and find the lowest cutoff_year.
    Also find affiliations and grants and create a union of them across projects.
    Update the authors in config_dict["Authors"].
    
    Args:
        authors_by_project_dict (dict): keys are the projects in the config_dict and the values are the authors associated with that project from config_dict["Authors"].
        config_dict (dict): schema matches the JSON Project Tracking Configuration file.
        
    Returns:
        config_dict (dict): schema matches the JSON Project Tracking Configuration file.
    """
    
    for author, author_attr in config_dict["Authors"].items():
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
        grants.sort()
        affiliations.sort()
        config_dict["Authors"][author]["cutoff_year"] = cutoff_year
        config_dict["Authors"][author]["affiliations"] = affiliations
        config_dict["Authors"][author]["grants"] = grants
        
    return config_dict["Authors"]



    
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
    
    Returns:
        (tuple): either the tuple of the matched groups in the regex or an empty tuple if a match wasn't found.
    """
    
    match = re.search(regex, string_to_search)
    if match:
        return match.groups()
    else:
        return ()



    
def match_authors_in_pub_PubMed(authors_json, author_list):
    """Look for matching authors in PubMed pub data.
    
    Goes through the author list from PubMed and tries matching to an author in 
    authors_json using firstname, lastname, and affiliations.
    
    Args:
        authors_json (dict): keys are authors and values are author attributes. Matches authors JSON schema.
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
        
        for author, author_attributes in authors_json.items():
        
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

    
    
    
def match_authors_in_pub_Crossref(authors_json, author_list):
    """Look for matching authors in Crossref pub data.
    
    Goes through the author list from Crossref and tries matching to an author in 
    authors_json using firstname, lastname, and affiliations, or ORCID if ORCID
    is present.
    
    Args:
        authors_json (dict): keys are authors and values are author attributes. Matches authors JSON schema.
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
        
        for author, author_attributes in authors_json.items():
        
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



def fuzzy_matches_to_list(str_to_match, list_to_match):
    """Return strings and indexes for strings with match ratio that is 90 or higher.
    
    Args:
        str_to_match (str): string to compare with list
        list_to_match (list): list of strings to compare with str_to_match
        
    Returns:
        (list): list of matches (tuples) with each element being the string and its index in list_to_match. [(9, "title 1"), ...]
    """
    str_to_match = str_to_match.lower()
    list_to_match = [list_string.lower() for list_string in list_to_match]
    
    return [(index, list_string) for index, list_string in enumerate(list_to_match) if fuzzywuzzy.fuzz.ratio(str_to_match, list_string) >= 90]



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
        titles = [pub_attr["title"] for pub_attr in publication_dict.values() if pub_attr["title"]]
    
    if is_fuzzy_match_to_list(title, titles):
        return True
    else:
        return False



def find_duplicate_citations(tokenized_citations):
    """Find citations that are duplicates of each other in tokenized_citations.
    
    Citations can be duplicates in 3 ways. Same PMID, same DOI, or similar enough titles.
    The function goes through each citation and looks for matches on these criteria.
    Then the matches are compared to create unique sets. For instance if citation 1
    matches the PMID in citation 2, and citation 2 matches the DOI in citation 3, but 
    citation 1 and 3 don't match a duplicate set containing all 3 is created. The 
    unique duplicate sets are returned as a list of sorted lists.
    
    Args:
        tokenized_citation (list): list of dictionaries where each dictionary is a citation. Matches the tokenized_reference.json schema.
        
    Returns:
        unique_duplicate_sets (list): list of lists where each element is a list of indexes in tokenized_citations that match each other. The list of indexes is sorted in ascending order.
    """
    
    titles_list = [citation["title"] for citation in tokenized_citations if citation["title"]]
    
    pmids = {}
    dois = {}
    titles = {}
    for count, citation in enumerate(tokenized_citations):
        
        if citation["PMID"]:
            if citation["PMID"] in pmids:
                pmids[citation["PMID"]].append(count)
            else:
                pmids[citation["PMID"]] = [count]
                
        if citation["DOI"]:
            doi = citation["DOI"].lower()
            if doi in dois:
                dois[doi].append(count)
            else:
                dois[doi] = [count]
                
        if citation["title"]:
            fuzzy_matches = fuzzy_matches_to_list(citation["title"], titles_list)
            if len(fuzzy_matches) > 1 and fuzzy_matches[0][1] in titles:
                titles[fuzzy_matches[0][1]].append(count)
            else:
                titles[citation["title"]] = [count]
                
    
    matching_pmids = {tuple(indexes) for pmid, indexes in pmids.items() if len(indexes) > 1}
    matching_dois = {tuple(indexes) for doi, indexes in dois.items() if len(indexes) > 1}
    matching_titles = {tuple(indexes) for title, indexes in titles.items() if len(indexes) > 1}
    
    all_matches = matching_pmids | matching_dois | matching_titles
    
    ## Matches need to be matched recursively to find true sets of matches.
    ## For example if 1 and 2 are found to match on title and 2 and 3 are found to match 
    ## on PMID then we need 1 set of (1,2,3) instead of 2 sets of (1,2) (2,3).
    duplicates_dict = {}
    for index_tuple in list(all_matches):
        for index in index_tuple:
            if index in duplicates_dict:
                for index2 in index_tuple:
                    if index2 != index:
                        duplicates_dict[index].add(index2)
            else:
                duplicates_dict[index] = set()
                for index2 in index_tuple:
                    if index2 != index:
                        duplicates_dict[index].add(index2)
                        
    for index, matches in duplicates_dict.items():
        temp_set = matches
        set_before_loop = matches
        while(True):
            for match in matches:
                temp_set = temp_set | duplicates_dict[match]
            
            if set_before_loop == temp_set:
                break
            else:
                set_before_loop = temp_set
                
        duplicates_dict[index] = temp_set
        
    unique_duplicate_sets = {tuple(duplicate_set) for duplicate_set in duplicates_dict.values()}
    unique_duplicate_sets = [list(duplicate_set) for duplicate_set in unique_duplicate_sets]
    for duplicate_set in unique_duplicate_sets:
        duplicate_set.sort()
    
    return unique_duplicate_sets
    
    

def are_citations_in_pub_dict(tokenized_citations, pub_dict):
    """Determine which citations in tokenized_citations are in pub_dict.
    
    For each citation in tokenized_citations see if it is in pub_dict. Will be 
    True for a citation if the PMID matches, DOI matches, or the title is similar 
    enough.
    
    Args:
        tokenized_citation (list): list of dictionaries where each dictionary is a citation. Matches the tokenized_reference.json schema.
        pub_dict (dict): schema matches the publication.json schema.
    
    Returns:
        (list): list of bools, True if the citation at that index is in pub_dict, False otherwise.
    """
    
    pub_titles = [pub["title"] for pub in pub_dict.values() if pub["title"]]
    pub_dois = [pub["doi"].lower() for pub in pub_dict.values() if pub["doi"]]
    pub_pmids = [pub["pubmed_id"] for pub in pub_dict.values() if pub["pubmed_id"]]
    
    return [True if citation["PMID"] in pub_pmids or citation["DOI"].lower() in pub_dois or is_fuzzy_match_to_list(citation["title"], pub_titles) else False for citation in tokenized_citations]








