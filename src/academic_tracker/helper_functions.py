# -*- coding: utf-8 -*-
"""
Helper Functions
~~~~~~~~~~~~~~~~

This module contains helper functions, such as printing, and regex searching.
"""

import re
import copy
import collections.abc
import xml.etree.ElementTree as ET

import fuzzywuzzy.fuzz

from . import __main__
from . import webio

DOI_URL = webio.DOI_URL


def vprint(*args, verbosity=0):
    """Print depending on the state of VERBOSE, SILENT, and verbosity.
    
    If the global SILENT is True don't print anything. If verbosity is 0 then 
    print. If verbosity is 1 then VERBOSE must be True to print.
    
    Args:
        verbosity (int): Either 0 or 1 for different levels of verbosity.
    """
    
    VERBOSE = __main__.VERBOSE
    SILENT = __main__.SILENT
    
    if SILENT:
        return
    
    if verbosity == 0:
        print(*args)
    elif VERBOSE and verbosity == 1:
        print(*args)



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
                    vprint("Warning: The author, " + author + ", in the " + project + " project of the project tracking configuration file could not be found in the Authors section of the Configuration JSON file.")
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
        cutoff_year = author_attr["cutoff_year"] if "cutoff_year" in author_attr else 9999
        
        affiliations = set(author_attr["affiliations"]) if "affiliations" in author_attr else set()
        
        grants = set(author_attr["grants"]) if "grants" in author_attr else set()
        
        for project, authors_dict in authors_by_project_dict.items():
            if author in authors_dict:
                if "cutoff_year" in authors_dict[author] and authors_dict[author]["cutoff_year"] < cutoff_year:
                    cutoff_year = authors_dict[author]["cutoff_year"]
                    
                if "affiliations" in authors_dict[author]:
                    affiliations |= set(authors_dict[author]["affiliations"])
                    
                if "grants" in authors_dict[author]:
                    grants |= set(authors_dict[author]["grants"])
                    
                if "collaborator_report" in authors_dict[author]:
                    config_dict["Authors"][author]["collaborator_report"] = authors_dict[author]["collaborator_report"]
                    
        affiliations = list(affiliations)
        grants = list(grants)
        grants.sort()
        affiliations.sort()
        config_dict["Authors"][author]["cutoff_year"] = cutoff_year
        config_dict["Authors"][author]["affiliations"] = affiliations
        config_dict["Authors"][author]["grants"] = grants
        
    return config_dict



    
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
    return match.groups() if match else ()



def regex_group_return(regex_groups, group_index):
    """Return the group in the regex_groups indicated by group_index if it exists, else return empty string.
    
    If group_index is out of range of the regex_groups an empty string is retruned.
    
    Args:
        regex_groups (tuple): A tuple returned from a matched regex.groups() call.
        group_number (int): The index of the regex_groups to return.
        
    Returns:
        (str): Either emtpy string or the group string matched by the regex.
    """
    
    return regex_groups[group_index] if group_index < len(regex_groups) and regex_groups[group_index] else ""



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
    return match.groups() if match else ()



    
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
        author_items_first_name = str(author_items.get("firstname")).replace(".","").lower()
        author_items_last_name = str(author_items.get("lastname")).replace(".","").lower()
        
        for author, author_attributes in authors_json.items():
            author_json_first_name = author_attributes["first_name"].replace(".","").lower()
            author_json_last_name = author_attributes["last_name"].replace(".","").lower()
        
            ## Match the author's first and last name and then match affiliations.
            ## The first name is matched with an additional .* to try and allow for the addition of initials, but this could cause bad matches. 
            ## For example the name Hu will match Hubert. Counting on the last name to reduce errors.
            ## Note that the PubMed query will return publications where the author is just a collaborater, so not finding a match in the authors isn't uncommon.
            if re.match(".* " + author_json_first_name + "|" + author_json_first_name + " .*", author_items_first_name) and \
               author_json_last_name == author_items_last_name:
                ## affiliations are sets of strings so the intersection should have at least 1 string for a match.
                
                if any([affiliation.lower() in author_items_affiliation for affiliation in author_attributes["affiliations"]]):
                    publication_has_affiliated_author = True
                    author_items["author_id"] = author
                    break
                
    return author_list if publication_has_affiliated_author else []

    
    
    
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
        
        author_items_first_name = str(author_items.get("given")).replace(".","").lower() if "given" in author_items else ""
        author_items_last_name = str(author_items.get("family")).replace(".","").lower()
        
        if "ORCID" in author_items:
            ORCID_id = regex_search_return(r"(\d{4}-\d{4}-\d{4}-\d{3}[0,1,2,3,4,5,6,7,8,9,X])", author_items["ORCID"])[0]
        else:
            ORCID_id = ""
        
        for author, author_attributes in authors_json.items():
            author_json_first_name = author_attributes["first_name"].replace(".","").lower()
            author_json_last_name = author_attributes["last_name"].replace(".","").lower()
        
            ## Match the author's first and last name and then match affiliations.
            ## The first name is matched with an additional .* to try and allow for the addition of initials, but this could cause bad matches. 
            ## For example the name Hu will match Hubert. Counting on the last name to reduce errors.
            ## Note that the PubMed query will return publications where the author is just a collaborater, so not finding a match in the authors isn't uncommon.
            if re.match(".* " + author_json_first_name + "|" + author_json_first_name + " .*", author_items_first_name) and \
               author_json_last_name == author_items_last_name:
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



def match_authors_in_prev_pub(prev_author_list, new_author_list):
    """Look for matching authors in previous pub data.
    
    Goes through the new_author_list and tries to find a match for each author 
    in the prev_author_list. Any authors that aren't matched are added to a 
    combined list. Both lists are expected to be a list of a dicts.
    
    {"firstname": author's first name,
     "lastname": author's last name,
     "author_id" : author's ID}
    
    If author_id is missing or None in the prev_author_list, it will be updated 
    in the combined_author_list if the matched author in new_author_list has it.
    
    Args:
        prev_author_list (list): list of dicts where each dict is the attributes of an author.
        new_author_list (list): list of dicts where each dict is the attributes of an author.
        
    Returns:
        combined_author_list (list): the prev_author_list updated with "author_id" for dictionaries in the list that matched the given author.
    """
    combined_author_list = copy.deepcopy(prev_author_list)
    for new_author_attributes in new_author_list:
        new_firstname_adjusted = new_author_attributes["firstname"].replace(".","").lower()
        new_lastname_adjusted = new_author_attributes["lastname"].replace(".","").lower()
        new_author_matched = False
        for i, prev_author_attributes in enumerate(prev_author_list):
            if new_author_attributes.get("author_id", 0) == prev_author_attributes.get("author_id", 1):
                new_author_matched = True
                break
            
            prev_firstname_adjusted = prev_author_attributes["firstname"].replace(".","").lower()
            prev_lastname_adjusted = prev_author_attributes["lastname"].replace(".","").lower()
            
            if re.match(".* " + new_firstname_adjusted + "|" + new_firstname_adjusted + " .*", prev_firstname_adjusted) and \
               new_lastname_adjusted == prev_lastname_adjusted:
                    if (author_id := new_author_attributes.get("author_id")) and not prev_author_attributes.get("author_id"):
                        combined_author_list[i]["author_id"] = author_id
                        new_author_matched = True
                        break
        if not new_author_matched:
            combined_author_list.append(new_author_attributes)
                
    return combined_author_list



def _match_references_in_prev_pub(prev_reference_list, new_reference_list, citation_match_ratio):
    """Look for matching references in previous pub data.
    
    Goes through the new_reference_list and tries to find a match for each reference 
    in the prev_reference_list. Any references that aren't matched are added to a 
    combined list. Both lists are expected to be a list of a dicts.
    
    {"citation": reference citation,
     "doi": reference DOI,
     "pubmed_id" : reference PMID,
     "PMCID": reference PMCID}
    
    Fields that are missing or None in the prev_reference_list will be updated 
    in the combined_reference_list if the matched reference in new_reference_list has it.
    
    Args:
        prev_reference_list (list): list of dicts where each dict is the attributes of a reference.
        new_reference_list (list): list of dicts where each dict is the attributes of a reference.
        citation_match_ratio (int): if the fuzzy ratio between the prev and new citations is greater 
                                    than or equal to this, then consider them to match.
        
    Returns:
        combined_reference_list (list): the prev_reference_list updated with keys for dictionaries in the list that matched the given reference.
    """
    combined_reference_list = copy.deepcopy(prev_reference_list)
    for new_reference_attributes in new_reference_list:
        new_reference_matched = False
        for i, prev_reference_attributes in enumerate(prev_reference_list):
            new_doi = new_reference_attributes.get("doi")
            prev_doi = prev_reference_attributes.get("doi")
            new_pmid = new_reference_attributes.get("pubmed_id")
            prev_pmid = prev_reference_attributes.get("pubmed_id")
            new_pmcid = new_reference_attributes.get("PMCID")
            prev_pmcid = prev_reference_attributes.get("PMCID")
            new_citation = new_reference_attributes.get("citation")
            prev_citation = prev_reference_attributes.get("citation")
            new_title = new_reference_attributes.get("title")
            prev_title = prev_reference_attributes.get("title")
            
            if (new_doi and prev_doi and new_doi.lower() == prev_doi.lower()) or\
               (new_pmid and prev_pmid and new_pmid == prev_pmid) or\
               (new_pmcid and prev_pmcid and new_pmcid == prev_pmcid) or\
               (new_title and prev_title and \
               (fuzzywuzzy.fuzz.ratio(new_title.lower(), prev_title.lower()) >= 90 or\
               fuzzywuzzy.fuzz.ratio(prev_title.lower(), new_title.lower()) >= 90)) or\
               (new_title and prev_citation and new_title.lower() in prev_citation.lower()) or\
               (new_citation and prev_title and prev_title.lower() in new_citation.lower()) or\
               (new_citation and prev_citation and \
               (fuzzywuzzy.fuzz.ratio(new_citation.lower(), prev_citation.lower()) >= citation_match_ratio or\
               fuzzywuzzy.fuzz.ratio(prev_citation.lower(), new_citation.lower()) >= citation_match_ratio)):
                _update(combined_reference_list[i], new_reference_list[i])
                new_reference_matched = True
                break
            
        if not new_reference_matched:
            combined_reference_list.append(new_reference_attributes)
                
    return combined_reference_list



def modify_pub_dict_for_saving(pub, include_xml=False):
    """Convert pymed.PubMedArticle to a dictionary and modify it for saving.
    
    Converts a pymed.PubMedArticle to a dictionary, deletes the "xml" key if include_xml is False, and 
    converts the "publication_date" key to a string.
    
    Args:
        pub (pymed.PubMedArticle): publication to convert to a dictionary.
        include_xml (bool): if True, include the raw XML query in the key "xml".
        
    Returns:
        pub_dict (dict): pub converted to a dictionary. Keys are "pubmed_id", "title", "abstract", 
        "keywords", "journal", "publication_date", "authors", "methods", "conclusions", "results", "copyrights", and "doi"
    """
    
    pub_dict = pub.toDict()
    
    if (pmid := pub_dict["xml"].find("PubmedData/ArticleIdList/ArticleId[@IdType='pubmed']")) is not None:
        pub_dict["pubmed_id"] = pmid.text
    else:
        pub_dict["pubmed_id"] = None
    
    if (doi := pub_dict["xml"].find("PubmedData/ArticleIdList/ArticleId[@IdType='doi']")) is not None:
        pub_dict["doi"] = DOI_URL + doi.text.lower()
    else:
        pub_dict["doi"] = None
        
    if (pmc := pub_dict["xml"].find("PubmedData/ArticleIdList/ArticleId[@IdType='pmc']")) is not None:
        pub_dict["PMCID"] = pmc.text
    else:
        pub_dict["PMCID"] = None
    
    pub_dict["grants"] = [grant.text for grant in pub.xml.findall(".//GrantID")]
    
    references = []
    for reference in pub_dict["xml"].findall(".//Reference"):
        if (text := reference.find("Citation")) is not None:
            citation = text.text
        else:
            citation = None
        
        if (text := reference.find("ArticleId[@IdType='pmc']")) is not None:
            ref_pmc = text.text
        else:
            ref_pmc = None
        
        if (text := reference.find("ArticleId[@IdType='pubmed']")) is not None:
            ref_pmid = text.text
        else:
            ref_pmid = None
        
        if (text := reference.find("ArticleId[@IdType='doi']")) is not None:
            ref_doi = text.text.lower()
        else:
            ref_doi = None
        
        references.append({"citation":citation,
                           "title": None,
                           "PMCID":ref_pmc,
                           "pubmed_id":ref_pmid,
                           "doi":ref_doi})
    pub_dict["references"] = references
        
    if not include_xml:
        del pub_dict["xml"]
    else:
        pub_dict["xml"] = str(ET.tostring(pub_dict["xml"]), encoding="utf-8")
    
    if pub_dict["publication_date"]:
        pub_dict["publication_date"] = {"year":pub_dict["publication_date"].year, "month":pub_dict["publication_date"].month, "day":pub_dict["publication_date"].day}
    else:
        pub_dict["publication_date"] = {"year":None, "month":None, "day":None}
    
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
    
    return any([fuzzywuzzy.fuzz.ratio(str_to_match, list_string) >= 90 or fuzzywuzzy.fuzz.ratio(list_string, str_to_match) >= 90 for list_string in list_to_match])



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
    
    return [(index, list_string) for index, list_string in enumerate(list_to_match) if fuzzywuzzy.fuzz.ratio(str_to_match, list_string) >= 90 or fuzzywuzzy.fuzz.ratio(list_string, str_to_match) >= 90]



def is_pub_in_publication_dict(pub_id, title, publication_dict, titles=None):
    """True if pub_id is in publication_dict or title is a fuzzy match to titles in titles.
    
    Check whether the pub_id is in publication_dict. If it isn't then see if there is 
    a fuzzy match in titles. If titles is not provided then get a list of titles 
    from publication_dict.
    
    Args:
        pub_id (str): pub_id to check against in publication_dict to see if it already exists.
        title (str): title corresponding to pub_id to check against titles in publication_dict.
        publication_dict (dict): keys are pub_ids and values are pub attributes.
        titles (list|None): list of strings that should be titles to fuzzy match to title.
        
    Returns:
        (bool): True if the pub_id is in publication_dict or title is fuzzy matched in titles, False otherwise
    """
    
    if pub_id.lower() in publication_dict:
        return True
    
    if not titles:
        titles = [pub_attr["title"] for pub_attr in publication_dict.values() if pub_attr["title"]]
    
    return True if is_fuzzy_match_to_list(title, titles) else False



def get_pub_id_in_publication_dict(pub_id, title, publication_dict):
    """Get the pub_id in publication_dict for the publication that matches the given pub_id or fuzzy matches a title.
    
    Check whether the pub_id is in publication_dict. If it isn't then see if there is 
    a fuzzy match in titles. It is assumed every dictionary in publication_dict will 
    have a "title" key with a string value.
    
    Args:
        pub_id (str): pub_id to check against in publication_dict to see if it already exists.
        title (str): title corresponding to pub_id to check against titles in publication_dict.
        publication_dict (dict): keys are pub_ids and values are pub attributes.
        
    Returns:
        (str|None): the pub_id matched in publication_dict or None if nothing was found.
    """
    
    if pub_id.lower() in publication_dict:
        return pub_id.lower()
    
    for key, value in publication_dict.items():
        if fuzzywuzzy.fuzz.ratio(title.lower(), value["title"].lower()) >= 90 or\
           fuzzywuzzy.fuzz.ratio(value["title"].lower(), title.lower()) >= 90:
            return key
    
    return None



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



# def _update_nulls(original_dict, upgrade_dict):
#     """Update a dictionary in a nested fashion.
    
#     Only updates original_dict if original_dict has a None value for a key. 
#     This is recursive, so if a dicitonary type is seen for the value then this 
#     is called on that nested dictionary.
    
#     Args:
#         original_dict (dict): the dictionary to update.
#         upgrade_dict (dict): the dictionary to update values from.
        
#     Returns:
#         original_dict (dict): the updated original_dict
#     """
#     for key, value in original_dict.items():
#         if isinstance(value, collections.abc.Mapping):
#             original_dict[key] = _update_nulls(original_dict[key], upgrade_dict[key])
#         elif value is None and upgrade_dict.get(key) is not None:
#             original_dict[key] = upgrade_dict[key]
    
#     return original_dict



def _update(original_dict, upgrade_dict):
    """Update a dictionary in a nested fashion.
    
    Only updates original_dict if original_dict has a None value for a key, or 
    if the key does not already exist in original_dict.
    This is recursive, so if a dicitonary type is seen for the value then this 
    is called on that nested dictionary.
    
    Args:
        original_dict (dict): the dictionary to update.
        upgrade_dict (dict): the dictionary to update values from.
        
    Returns:
        original_dict (dict): the updated original_dict
    """
    for key, value in upgrade_dict.items():
        if key not in original_dict:
            original_dict[key] = value
        elif isinstance(value, collections.abc.Mapping) and isinstance(original_dict[key], collections.abc.Mapping):
            original_dict[key] = _update(original_dict[key], upgrade_dict[key])
        elif value is not None and original_dict[key] is None:
            original_dict[key] = upgrade_dict[key]
    
    return original_dict



def _merge_pub_dicts(prev_dict, new_dict, citation_match_ratio):
    """Merge information from 2 unified pub_dicts.
    
    Args:
        prev_dict (dict): the dictionary whose values will be updated.
        new_dict (dict): the dictionary whose values will be used to update prev_dict.
        citation_match_ratio (int): if the fuzzy ratio between 2 citations is greater than or equal to this, then consider them to match.
    
    Returns:
        prev_dict (dict): prev_dict with updated values
    """
    _update(prev_dict, new_dict)
    prev_dict["authors"] = match_authors_in_prev_pub(prev_dict["authors"], new_dict["authors"])
    prev_dict["references"] = _match_references_in_prev_pub(prev_dict["references"], new_dict["references"], citation_match_ratio)
    new_grants = [grant for grant in new_dict["grants"] if grant not in prev_dict["grants"]]
    prev_dict["grants"] += new_grants
    
    return prev_dict

