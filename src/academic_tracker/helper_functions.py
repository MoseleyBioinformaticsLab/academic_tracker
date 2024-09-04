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
PUBLICATION_TEMPLATE = webio.PUBLICATION_TEMPLATE


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


def _generate_first_name_match_regex(name):
    """Generate a regular expression to match the given first name.
    
    Args:
        name (str): first name to generate regex for.
    
    Returns:
        (str) regular expression to use with re.match().
    """
    return ".* " + name + "|" + name + " .*|" + name


def do_strings_fuzzy_match(string1, string2, match_ratio=90):
    """Fuzzy match the 2 strings and if the ratio is greater than or equal to match_ratio, return True.
    
    Args:
        string1 (str|None): a string to fuzzy match.
        string2 (str|None): a string to fuzzy match.
        match_ratio (int): the ratio (0-100) that the match must be greater than to return True.
    
    Returns:
        (bool): True if strings match, False otherwise.
    """
    if string1 is None or string2 is None:
        return False
    
    string1 = string1.lower()
    string2 = string2.lower()
    if fuzzywuzzy.fuzz.ratio(string1, string2) >= match_ratio or\
       fuzzywuzzy.fuzz.ratio(string2, string1) >= match_ratio:
           return True
    return False



    
# def match_authors_in_pub_PubMed(authors_json, author_list):
#     """Look for matching authors in PubMed pub data.
    
#     Goes through the author list from PubMed and tries matching to an author in 
#     authors_json using firstname, lastname, and affiliations.
    
#     Args:
#         authors_json (dict): keys are authors and values are author attributes. Matches authors JSON schema.
#         author_list (list): list of dicts where each dict is attributes of an author.
        
#     Returns:
#         author_list (list): either the author list with matched authors containing an additional author_id attribute, or an empty list if no authors were matched.
#     """
    
#     ## pub.authors are dictionaries with lastname, firstname, initials, and affiliation. firstname can have initials at the end ex "Andrew P"
#     publication_has_affiliated_author = False
#     for author_items in author_list:
#         author_items_affiliation = str(author_items.get("affiliation")).lower()
#         author_items_first_name = str(author_items.get("firstname")).replace(".","").lower()
#         author_items_last_name = str(author_items.get("lastname")).replace(".","").lower()
        
#         for author, author_attributes in authors_json.items():
#             author_json_first_name = author_attributes["first_name"].replace(".","").lower()
#             author_json_last_name = author_attributes["last_name"].replace(".","").lower()
        
#             ## Match the author's first and last name and then match affiliations.
#             ## The first name is matched with an additional .* to try and allow for the addition of initials, but this could cause bad matches. 
#             ## For example the name Hu will match Hubert. Counting on the last name to reduce errors.
#             ## Note that the PubMed query will return publications where the author is just a collaborater, so not finding a match in the authors isn't uncommon.
#             if re.match(_generate_first_name_match_regex(author_json_first_name), author_items_first_name) and \
#                author_json_last_name == author_items_last_name:
#                 ## affiliations are sets of strings so the intersection should have at least 1 string for a match.
                
#                 if any([affiliation.lower() in author_items_affiliation for affiliation in author_attributes["affiliations"]]):
#                     publication_has_affiliated_author = True
#                     author_items["author_id"] = author
#                     break
                
#     return author_list if publication_has_affiliated_author else []


    
    
# def match_authors_in_pub_Crossref(authors_json, author_list):
#     """Look for matching authors in Crossref pub data.
    
#     Goes through the author list from Crossref and tries matching to an author in 
#     authors_json using firstname, lastname, and affiliations, or ORCID if ORCID
#     is present.
    
#     Args:
#         authors_json (dict): keys are authors and values are author attributes. Matches authors JSON schema.
#         author_list (list): list of dicts where each dict is attributes of an author.
        
#     Returns:
#         author_list (list): either the author list with matched authors containing an additional author_id attribute, or an empty list if no authors were matched.
#     """
    
#     publication_has_affiliated_author = False
#     for author_items in author_list:
#         ## If the author has no affiliation or ORCID id then go to the next.
#         if not author_items["affiliation"] and not "ORCID" in author_items:
#             continue
        
#         can_name_match = True
#         if author_items.get("given") is None:
#             can_name_match = False
#         else:
#             author_items_first_name = author_items["given"].replace(".","").lower()
        
#         if author_items.get("family") is None:
#             can_name_match = False
#         else:
#             author_items_last_name = author_items["family"].replace(".","").lower()
        
#         if author_items["affiliation"] and "name" in author_items["affiliation"][0]:
#             author_items_affiliation = author_items["affiliation"][0]["name"].lower()
#         else:
#             author_items_affiliation = []
                
#         if "ORCID" in author_items:
#             ORCID_id = regex_search_return(r"(\d{4}-\d{4}-\d{4}-\d{3}[0,1,2,3,4,5,6,7,8,9,X])", author_items["ORCID"])[0]
#         else:
#             ORCID_id = ""
        
#         for author, author_attributes in authors_json.items():
#             author_json_first_name = author_attributes["first_name"].replace(".","").lower()
#             author_json_last_name = author_attributes["last_name"].replace(".","").lower()
        
#             ## Match the author's first and last name and then match affiliations.
#             ## The first name is matched with an additional .* to try and allow for the addition of initials, but this could cause bad matches. 
#             ## For example the name Hu will match Hubert. Counting on the last name to reduce errors.
#             ## Note that the PubMed query will return publications where the author is just a collaborater, so not finding a match in the authors isn't uncommon.
#             if can_name_match and re.match(_generate_first_name_match_regex(author_json_first_name), author_items_first_name) and \
#                author_json_last_name == author_items_last_name:
#                 ## affiliations are sets of strings so the intersection should have at least 1 string for a match.
#                 if any([affiliation.lower() in author_items_affiliation for affiliation in author_attributes["affiliations"]]):
#                     publication_has_affiliated_author = True
#                     author_items["author_id"] = author
#                     break
                
#             elif ORCID_id and "ORCID" in author_attributes and ORCID_id == author_attributes["ORCID"]:
#                 publication_has_affiliated_author = True
#                 author_items["author_id"] = author
#                 break
                
#     if publication_has_affiliated_author:
#         return author_list
#     else:
#         return []



def match_pub_authors_to_citation_authors(citation_authors, author_list):
    """Try to match authors in pub data to authors in citation data.
    
    Goes through the author_list from a publication and tries matching to an author in 
    citation_authors using last name or ORCID if ORCID is present.
    
    Args:
        citation_authors (list): list of dicts where each dict can have last name and ORCID or collective_name and ORCID.
        author_list (list): list of dicts where each dict is the attributes of an author.
        
    Returns:
        (bool): True if an author was matched, False otherwise.
    """
    for author_items in author_list:
        is_collective_author = False
        has_collective_name = False
        if "collectivename" in author_items:
            is_collective_author = True
            if author_items["collectivename"] is not None:
                has_collective_name = True
                author_items_collective_name = author_items["collectivename"]
        
        else:
            can_name_match = True
            if author_items["lastname"] is None:
                can_name_match = False
            else:
                author_items_last_name = author_items["lastname"].replace(".","").lower()
                                    
        for author_attributes in citation_authors:
            ## Try to match on ORCID.
            if author_items["ORCID"] and "ORCID" in author_attributes and author_items["ORCID"] == author_attributes["ORCID"]:
                return True
            
            citation_is_collective_author = False
            citation_has_collective_name = False
            if "collective_name" in author_attributes:
                citation_is_collective_author = True
                if author_attributes["collective_name"] is not None:
                    citation_has_collective_name = True
                    citation_author_collective_name = author_attributes["collective_name"]
            
            ## If it is a collective author then match on collectivename, else match on first and last.
            if is_collective_author:
                if not has_collective_name or \
                   not citation_is_collective_author or \
                   not citation_has_collective_name:
                    continue
                
                if do_strings_fuzzy_match(citation_author_collective_name, author_items_collective_name):
                       return True
            
            elif not citation_is_collective_author:
                citation_author_last_name = author_attributes["last"].replace(".","").lower()
            
                if can_name_match and citation_author_last_name == author_items_last_name:
                    return True
                
    return False



def match_pub_authors_to_config_authors(authors_json, author_list):
    """Try to match authors in pub data to authors in config data.
    
    Goes through the author_list from a publication and tries matching to an author in 
    authors_json using firstname, lastname, and affiliations, or ORCID if ORCID
    is present.
    
    Args:
        authors_json (dict): keys are authors and values are author attributes. Matches authors JSON schema.
        author_list (list): list of dicts where each dict is the attributes of an author.
        
    Returns:
        author_list (list): either the author list with matched authors containing an additional author_id and/or ORCID attribute, or an empty list if no authors were matched.
    """
    publication_has_affiliated_author = False
    for author_items in author_list:
        is_collective_author = False
        has_collective_name = False
        if "collectivename" in author_items:
            is_collective_author = True
            if author_items["collectivename"] is not None:
                has_collective_name = True
                author_items_collective_name = author_items["collectivename"]
        
        else:
            can_name_match = True
            if author_items["firstname"] is None:
                can_name_match = False
            else:
                author_items_first_name = author_items["firstname"].replace(".","").lower()
            
            if author_items["lastname"] is None:
                can_name_match = False
            else:
                author_items_last_name = author_items["lastname"].replace(".","").lower()
            
            if author_items["affiliation"] is None:
                can_name_match = False
            else:
                author_items_affiliation = author_items["affiliation"].lower()
                        
        for author, author_attributes in authors_json.items():
            ## Try to match on ORCID.
            if author_items["ORCID"] and "ORCID" in author_attributes and author_items["ORCID"] == author_attributes["ORCID"]:
                publication_has_affiliated_author = True
                author_items["author_id"] = author
                break
            
            author_json_is_collective_author = False
            author_json_has_collective_name = False
            if "collective_name" in author_attributes:
                author_json_is_collective_author = True
                if author_attributes["collective_name"] is not None:
                    author_json_has_collective_name = True
                    author_json_collective_name = author_attributes["collective_name"]
            
            ## If it is a collective author then match on collective_name, else match on first and last.
            if is_collective_author:
                if not has_collective_name or \
                   not author_json_is_collective_author or \
                   not author_json_has_collective_name:
                    continue
                                
                if do_strings_fuzzy_match(author_json_collective_name, author_items_collective_name):
                       publication_has_affiliated_author = True
                       author_items["author_id"] = author
                       author_items["ORCID"] = author_attributes["ORCID"] if "ORCID" in author_attributes and author_items["ORCID"] is None else author_items["ORCID"]
                       break
            
            elif not author_json_is_collective_author:
                author_json_first_name = author_attributes["first_name"].replace(".","").lower()
                author_json_last_name = author_attributes["last_name"].replace(".","").lower()
            
                ## Match the author's first and last name and then match affiliations.
                ## The first name is matched with an additional .* to try and allow for the addition of initials, but this could cause bad matches. 
                ## For example the name Hu will match Hubert. Counting on the last name to reduce errors.
                ## Note that the PubMed query will return publications where the author is just a collaborater, so not finding a match in the authors isn't uncommon.
                if can_name_match and re.match(_generate_first_name_match_regex(author_json_first_name), author_items_first_name) and \
                   author_json_last_name == author_items_last_name:
                    ## affiliations in author_attributes are sets of strings so see if any are in the author_items string.
                    if any([affiliation.lower() in author_items_affiliation for affiliation in author_attributes["affiliations"]]):
                        publication_has_affiliated_author = True
                        author_items["author_id"] = author
                        author_items["ORCID"] = author_attributes["ORCID"] if "ORCID" in author_attributes and author_items["ORCID"] is None else author_items["ORCID"]
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
     "author_id" : author's ID,
     "ORCID": ORCID ID}
    
    {"collectivename": collective name,
     "author_id": author's ID,
     "ORCID": ORCID ID}
    
    If author_id is missing or None in the prev_author_list, it will be updated 
    in the combined_author_list if the matched author in new_author_list has it. 
    The same can be said for the ORCID attribute.
    
    Args:
        prev_author_list (list): list of dicts where each dict is the attributes of an author.
        new_author_list (list): list of dicts where each dict is the attributes of an author.
        
    Returns:
        combined_author_list (list): the prev_author_list updated with "author_id" for dictionaries in the list that matched the given author.
    """
    combined_author_list = copy.deepcopy(prev_author_list)
    for new_author_attributes in new_author_list:
        is_collective_author = False
        has_collective_name = False
        if "collectivename" in new_author_attributes:
            is_collective_author = True
            if new_author_attributes["collectivename"] is not None:
                has_collective_name = True
                new_collective_name = new_author_attributes["collectivename"]
        
        else:
            can_name_match = True
            if new_author_attributes["firstname"] is None:
                can_name_match = False
            else:
                new_firstname_adjusted = new_author_attributes["firstname"].replace(".","").lower()
            
            if new_author_attributes["lastname"] is None:
                can_name_match = False
            else:
                new_lastname_adjusted = new_author_attributes["lastname"].replace(".","").lower()
        
        new_author_matched = False
        for i, prev_author_attributes in enumerate(prev_author_list):
            ## Try to match with author_id.
            if new_author_attributes.get("author_id", 0) == prev_author_attributes.get("author_id", 1):
                new_author_matched = True
                if prev_author_attributes["ORCID"] is None:
                    combined_author_list[i]["ORCID"] = new_author_attributes["ORCID"]
                break
            
            ## Try to match with ORCID.
            if new_author_attributes["ORCID"] and new_author_attributes["ORCID"] == prev_author_attributes["ORCID"]:
                new_author_matched = True
                if (author_id := new_author_attributes.get("author_id")) and not prev_author_attributes.get("author_id"):
                    combined_author_list[i]["author_id"] = author_id
                break
            
            prev_is_collective_author = False
            prev_has_collective_name = False
            if "collectivename" in prev_author_attributes:
                prev_is_collective_author = True
                if prev_author_attributes["collectivename"] is not None:
                    prev_has_collective_name = True
                    prev_collective_name = prev_author_attributes["collectivename"]
            
            ## If it is a collective author then match on collectivename, else match on first and last.
            if is_collective_author:
                if not has_collective_name or \
                   not prev_is_collective_author or \
                   not prev_has_collective_name:
                    continue
                
                if do_strings_fuzzy_match(prev_collective_name, new_collective_name):
                        new_author_matched = True
                        if (author_id := new_author_attributes.get("author_id")) and not prev_author_attributes.get("author_id"):
                            combined_author_list[i]["author_id"] = author_id
                        if prev_author_attributes["ORCID"] is None:
                            combined_author_list[i]["ORCID"] = new_author_attributes["ORCID"]
                        break
            
            elif not prev_is_collective_author:
                ## If the first and last names are missing for either author then they can't be matched.
                if prev_author_attributes["firstname"] is None or \
                   prev_author_attributes["lastname"] is None or \
                   not can_name_match:
                    continue
                    
                prev_firstname_adjusted = prev_author_attributes["firstname"].replace(".","").lower()
                prev_lastname_adjusted = prev_author_attributes["lastname"].replace(".","").lower()
                
                if re.match(_generate_first_name_match_regex(new_firstname_adjusted), prev_firstname_adjusted) and \
                   new_lastname_adjusted == prev_lastname_adjusted:
                        new_author_matched = True
                        if (author_id := new_author_attributes.get("author_id")) and not prev_author_attributes.get("author_id"):
                            combined_author_list[i]["author_id"] = author_id
                        if prev_author_attributes["ORCID"] is None:
                            combined_author_list[i]["ORCID"] = new_author_attributes["ORCID"]
                        break
        
        if not new_author_matched:
            combined_author_list.append(new_author_attributes)
                
    return combined_author_list



def _match_references_in_prev_pub(prev_reference_list, new_reference_list):
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
        
    Returns:
        combined_reference_list (list): the prev_reference_list updated with keys for dictionaries in the list that matched the given reference.
    """
    characters_to_remove = ['.', ',', ';', '(', ')', '[', ']', '{', '}']
    combined_reference_list = copy.deepcopy(prev_reference_list)
    matched_indexes = []
    for new_reference_attributes in new_reference_list:
        new_reference_matched = False
        for i, prev_reference_attributes in enumerate(prev_reference_list):
            ## There is a rare case where 2 different publications have the same title and 
            ## are referenced in the same paper. Need to disallow matching to the same reference 
            ## twice to avoid duplicates. Example paper: https://pubmed.ncbi.nlm.nih.gov/24404440/ 
            ## reference 1 and 3 have the same title, but are not the same reference.
            if i in matched_indexes:
                continue
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
               (do_strings_fuzzy_match(new_title, prev_title))) or\
               (new_title and prev_citation and new_title.lower() in prev_citation.lower()) or\
               (new_citation and prev_title and prev_title.lower() in new_citation.lower()) or\
               ((percentages := _compute_common_phrase_percent(prev_citation, new_citation, characters_to_remove, 4)) and\
                (percentages[0] >= 85 or percentages[1] >= 85)):
                _update(combined_reference_list[i], new_reference_attributes)
                new_reference_matched = True
                matched_indexes.append(i)
                break
            
        if not new_reference_matched:
            combined_reference_list.append(new_reference_attributes)
                
    return combined_reference_list



def _compute_common_phrase_percent(prev_citation, new_citation, characters_to_remove, min_len=2):
    """Find common phrases between prev_citation and new_citation and return percentage.
    
    Determine the common subphrases between the citations and then divide the length of the 
    common subphrases with the length of the common subphrases plus the uncommon subphrases 
    left for each citation and multiply by 100 to get the percentage of characters that are 
    common between the common+uncommon and common subphrases. If either citation is None, then 
    return None.
    
    Example:
        prev_citation = 'open js foundation 2019  accessed on 1 january 2023  available online:  https://openjsforg/'
        new_citation = '2023 january 01 open js foundation available online: https://openjsforg/'
        
        common_base_string = ' https://openjsforg/open js foundation available online:  january 2023 '
        
        prev_common_plus_uncommon = ' https://openjsforg/open js foundation available online:  january 2023 2019  accessed on 1'
        new_common_plus_uncommon = ' https://openjsforg/open js foundation available online:  january 2023 01'
        
        prev_percent = 78.88888888888889
        new_percent = 97.26027397260275
    
    Args:
        prev_citation (str|None): a string to find common subphrases with another string.
        new_citation (str|None): a string to find common subphrases with another string.
        characters_to_remove (list): a list of characters or strings to remove from each citation before finding common subphrases.
        min_len (int): the minimum length of a subphrase.
    
    Returns:
        ((int, int)|None): if either citation is None or empty after character removal and stripping, then return None, else the percentage of common to uncommon phrase length for each citation.
    """
    if prev_citation and new_citation:
        citation_strip_regex = "|".join([f"\\{char}" for char in characters_to_remove])
        # citation_strip_regex = r"\.|,|;|\(|\)|\[|\]|\{|\}"
        stripped_prev_citation = re.sub(citation_strip_regex, "", prev_citation.lower())
        stripped_new_citation = re.sub(citation_strip_regex, "", new_citation.lower())
        
        common_subphrases = find_common_subphrases(stripped_prev_citation, stripped_new_citation, min_len)
        
        prev_citation_common_phrases_removed = stripped_prev_citation
        new_citation_common_phrases_removed = stripped_new_citation
        for phrase in common_subphrases:
            prev_citation_common_phrases_removed = prev_citation_common_phrases_removed.replace(phrase.strip(), "")
            new_citation_common_phrases_removed = new_citation_common_phrases_removed.replace(phrase.strip(), "")
        common_base_string = "".join(common_subphrases)
        prev_common_denom = len(common_base_string + prev_citation_common_phrases_removed.strip())
        new_common_denom = len(common_base_string + new_citation_common_phrases_removed.strip())
        if prev_common_denom == 0 or new_common_denom == 0: 
            return None
        prev_common_percentage = len(common_base_string) / prev_common_denom * 100
        new_common_percentage = len(common_base_string) / new_common_denom * 100
        
        return prev_common_percentage, new_common_percentage
    else:
        return None



def create_pub_dict_for_saving_PubMed(pub, include_xml=False):
    """Convert pymed.PubMedArticle to a dictionary and modify it for saving.
    
    Converts a pymed.PubMedArticle to a dictionary, deletes the "xml" key if include_xml is False, and 
    converts the "publication_date" key to a string.
    
    Args:
        pub (pymed.PubMedArticle): publication to convert to a dictionary.
        include_xml (bool): if True, include the raw XML query in the key "xml".
        
    Returns:
        pub_id (str): the ID of the publication (DOI or PMID).
        pub_dict (dict): pub converted to a dictionary. Keys are "pubmed_id", "title", "abstract", 
        "keywords", "journal", "publication_date", "authors", "methods", "conclusions", "results", "copyrights", and "doi"
    """
    
    pub_dict = pub.toDict()
        
    if (pmid := pub_dict["xml"].find("PubmedData/ArticleIdList/ArticleId[@IdType='pubmed']")) is not None:
        pub_dict["pubmed_id"] = pmid.text
    else:
        pub_dict["pubmed_id"] = None
    
    if (doi := pub_dict["xml"].find("PubmedData/ArticleIdList/ArticleId[@IdType='doi']")) is not None:
        pub_dict["doi"] = doi.text.lower()
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
        
        if (text := reference.find("ArticleIdList/ArticleId[@IdType='pmc']")) is not None:
            ref_pmc = text.text
        else:
            ref_pmc = None
        
        if (text := reference.find("ArticleIdList/ArticleId[@IdType='pubmed']")) is not None:
            ref_pmid = text.text
        else:
            ref_pmid = None
        
        if (text := reference.find("ArticleIdList/ArticleId[@IdType='doi']")) is not None:
            ref_doi = text.text.lower()
        else:
            ref_doi = None
        
        temp_dict = {"citation":citation,
                     "title": None,
                     "PMCID":ref_pmc,
                     "pubmed_id":ref_pmid,
                     "doi":ref_doi}
        
        ## Only add references that have at least 1 non-null value.
        if not all([value is None for value in temp_dict.values()]):
            references.append(temp_dict)
    pub_dict["references"] = references
    
    authors = []
    for author in pub_dict["xml"].findall(".//Author"):
        last_name = None
        if (text := author.find("LastName")) is not None:
            last_name = text.text
        
        collective_name = None
        if (text := author.find("CollectiveName")) is not None:
            collective_name = text.text
        
        first_name = None
        if (text := author.find("ForeName")) is not None:
            first_name = text.text
        
        initials = None
        if (text := author.find("Initials")) is not None:
            initials = text.text
        
        affiliation = None
        if (affiliations := author.findall("AffiliationInfo/Affiliation")) is not None:
            affiliation = '\n'.join([text.text for text in affiliations]) if affiliations else None
        
        orcid = None
        if (text := author.find("Identifier[@Source='ORCID']")) is not None:
            orcid = extract_ORCID_from_string(text.text)
        
        if collective_name:
            temp_dict = {"collectivename":collective_name,
                         "ORCID":orcid,
                         "author_id":None}
        else:
            temp_dict = {"lastname":last_name if last_name else collective_name,
                         "firstname": first_name,
                         "initials":initials,
                         "affiliation":affiliation,
                         "ORCID":orcid,
                         "author_id":None}
        
        ## Only add authors that have at least 1 non-null value.
        if not all([value is None for value in temp_dict.values()]):
            authors.append(temp_dict)
    pub_dict["authors"] = authors
        
    if not include_xml:
        del pub_dict["xml"]
    else:
        pub_dict["xml"] = str(ET.tostring(pub_dict["xml"]), encoding="utf-8")
    
    if pub_dict["publication_date"]:
        pub_dict["publication_date"] = {"year":pub_dict["publication_date"].year, "month":pub_dict["publication_date"].month, "day":pub_dict["publication_date"].day}
    else:
        pub_dict["publication_date"] = {"year":None, "month":None, "day":None}
    
    pub_id = DOI_URL + pub_dict["doi"] if pub_dict["doi"] else pub_dict["pubmed_id"]
    
    return pub_id, pub_dict



def create_pub_dict_for_saving_Crossref(work, prev_query):
    """Create the standard pub_dict from a Crossref query work dict.
    
    Args:
        work (dict): the dictionary for a publication returned in a Crossref query.
        prev_query (dict|None): a dictionary containing publications from a previous query, used for message printing.
    
    Returns:
        pub_id (str|None): the ID of the publication (DOI, PMID, or URL). If None, an ID couldn't be determined.
        pub_dict (dict|None): the standard pub_dict with values filled in from the Crossref publication. If None, an ID couldn't be determined.
    """
    if "title" in work:
        title = work["title"][0]
    else:
        return None, None
    
    ## Look for DOI
    doi = work["DOI"].lower() if "DOI" in work else None
    
    ## Look for external URL
    if "URL" in work:
        external_url = work["URL"]
    elif "link" in work:
        external_url = [link["URL"] for link in work["link"] if "URL" in link and link["URL"]][0]
        if not external_url:
            external_url = None
    else:
        external_url = None
                    
    
    if doi:
        pub_id = DOI_URL + doi
    elif external_url:
        pub_id = external_url
    elif not prev_query:
        vprint("Warning: Could not find a DOI or external URL for a publication when searching Crossref. It will not be in the publications.", verbosity=1)
        vprint("Title: " + title, verbosity=1)
        return None, None
    else:
        return None, None
    
    ## Determine authors and put them in unified form.
    new_author_list = []
    if "author" in work:
        for cr_author_dict in work["author"]:
            temp_dict = {}
            
            orcid = None
            if "ORCID" in cr_author_dict:
                orcid = extract_ORCID_from_string(cr_author_dict["ORCID"])
            temp_dict["ORCID"] = orcid
            
            temp_dict["author_id"] = None
            
            ## If "name" is in dict then it is a collective author and not an individual.
            if "name" in cr_author_dict:
                temp_dict["collectivename"] = cr_author_dict["name"]
            
            else:
                temp_dict["lastname"] = cr_author_dict.get("family")
                temp_dict["firstname"] = cr_author_dict.get("given")
                temp_dict["initials"] = None
                
                affiliations = []
                if cr_author_dict["affiliation"]:
                    for affiliation in cr_author_dict["affiliation"]:
                        if aff_text := affiliation.get("name"):
                            affiliations.append(aff_text)
                temp_dict["affiliation"] = '\n'.join(affiliations) if affiliations else None
            
            ## Only add authors that have at least 1 non-null value.
            if not all([value is None for value in temp_dict.values()]):
                new_author_list.append(temp_dict)
    
    
    ## Find published date
    date_found = False
    if "published" in work:
        date_key = "published"
        date_found = True
    elif "published-online" in work:
        date_key = "published-online"
        date_found = True
    elif "published-print" in work:
        date_key = "published-print"
        date_found = True
    
    if date_found:
        date_length = len(work[date_key]["date-parts"][0])
        
        if date_length > 2:
            publication_year = work[date_key]["date-parts"][0][0]
            publication_month = work[date_key]["date-parts"][0][1]
            publication_day = work[date_key]["date-parts"][0][2]
        elif date_length > 1:
            publication_year = work[date_key]["date-parts"][0][0]
            publication_month = work[date_key]["date-parts"][0][1]
            publication_day = None
        elif date_length > 0:
            publication_year = work[date_key]["date-parts"][0][0]
            publication_month = None
            publication_day = None
        else:
            publication_year = None
            publication_month = None
            publication_day = None
    else:
        publication_year = None
        publication_month = None
        publication_day = None
    
    
    ## look for grants in results
    found_grants = []
    if "funder" in work:
        for funder in work["funder"]:
            if awards := funder.get("award"):
                found_grants += awards
        
    ## Look for journal
    journal = work["publisher"] if "publisher" in work else None
    
    ## Look for references and put them in unified form.
    references = []
    if "reference" in work:
        for reference in work["reference"]:
            if "DOI" in reference:
                ref_doi = reference["DOI"]
            else:
                ref_doi = None
            
            if ref_title := reference.get("article-title"):
                pass
            else:
                ref_title = reference.get("series-title")
            
            reference_dict = {"citation":reference.get("unstructured"),
                              "title":ref_title,
                              "PMCID":None,
                              "pubmed_id":None,
                              "doi":ref_doi}
            if all([value is None for value in reference_dict.values()]):
                continue
            else:
                references.append(reference_dict)
        

    ## Build the pub_dict from what we were able to collect.
    pub_dict = copy.deepcopy(PUBLICATION_TEMPLATE)
    
    pub_dict["doi"] = doi
    pub_dict["publication_date"]["year"] = publication_year
    pub_dict["publication_date"]["month"] = publication_month
    pub_dict["publication_date"]["day"] = publication_day
    pub_dict["journal"] = journal
    pub_dict["grants"] = found_grants
    pub_dict["authors"] = new_author_list
    pub_dict["title"] = title
    pub_dict["references"] = references
    
    return pub_id, pub_dict



ORCID_regex = r"(\d{4}-\d{4}-\d{4}-\d{3}[0,1,2,3,4,5,6,7,8,9,X])"
alt_ORCID_regex = r"(\d{4}\d{4}\d{4}\d{3}[0,1,2,3,4,5,6,7,8,9,X])"
def extract_ORCID_from_string(string):
    """Extract an ORCID ID from a string.
    
    Args:
        string (str): the string to extract the ID from.
        
    Returns:
        (str|None): either the extracted ID as a string or None.
    """
    
    if re_match := re.search(ORCID_regex, string):
        return re_match.groups()[0]
    elif re_match := re.search(alt_ORCID_regex, string):
        captured_string = re_match.groups()[0]
        new_string = captured_string[0:4] + '-' + captured_string[4:8] + '-' + captured_string[8:12] + '-' + captured_string[12:]
        return new_string
    else:
        return None



def is_fuzzy_match_to_list(str_to_match, list_to_match):
    """True if string is a 90 or higher ratio match to any string in list, False otherwise.
    
    Args:
        str_to_match (str): string to compare with list
        list_to_match (list): list of strings to compare with str_to_match
        
    Returns:
        (bool): True if str_to_match is a match to any string in list_tp_match, False otherwise.
    """
    # str_to_match = str_to_match.lower()
    # list_to_match = [list_string.lower() for list_string in list_to_match]
    
    return any([do_strings_fuzzy_match(str_to_match, list_string) for list_string in list_to_match])



def fuzzy_matches_to_list(str_to_match, list_to_match):
    """Return strings and indexes for strings with match ratio that is 90 or higher.
    
    Args:
        str_to_match (str): string to compare with list
        list_to_match (list): list of strings to compare with str_to_match
        
    Returns:
        (list): list of matches (tuples) with each element being the string and its index in list_to_match. [(9, "title 1"), ...]
    """
    # str_to_match = str_to_match.lower()
    # list_to_match = [list_string.lower() for list_string in list_to_match]
    
    return [(index, list_string) for index, list_string in enumerate(list_to_match) if do_strings_fuzzy_match(str_to_match, list_string)]



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
        if do_strings_fuzzy_match(title, value["title"]):
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
        
    unique_duplicate_sets = {tuple(sorted(duplicate_set)) for duplicate_set in duplicates_dict.values()}
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
    pub_dois = [doi.lower() for pub in pub_dict.values() if (doi := normalize_DOI(pub["doi"]))]
    pub_pmids = [pub["pubmed_id"] for pub in pub_dict.values() if pub["pubmed_id"]]
    
    return [True if citation["PMID"] in pub_pmids or ((doi := normalize_DOI(citation["DOI"])) and doi.lower()) in pub_dois or is_fuzzy_match_to_list(citation["title"], pub_titles) else False for citation in tokenized_citations]


def normalize_DOI(doi_string):
    """
    """
    if doi_string:
        if doi_match := regex_match_return(r'https?://doi.org/(.*)', doi_string):
            return doi_match[0]
        return doi_string
    return None



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



def _merge_pub_dicts(prev_dict, new_dict):
    """Merge information from 2 unified pub_dicts.
    
    Args:
        prev_dict (dict): the dictionary whose values will be updated.
        new_dict (dict): the dictionary whose values will be used to update prev_dict.
    
    Returns:
        prev_dict (dict): prev_dict with updated values
    """
    _update(prev_dict, new_dict)
    prev_dict["authors"] = match_authors_in_prev_pub(prev_dict["authors"], new_dict["authors"])
    prev_dict["references"] = _match_references_in_prev_pub(prev_dict["references"], new_dict["references"])
    new_grants = [grant for grant in new_dict["grants"] if grant not in prev_dict["grants"]]
    prev_dict["grants"] += new_grants
    
    return prev_dict



def find_common_subphrases(str1, str2, min_len=2):
    """Find all common subphrases between str1 and str2 longer than min_len.
    
    Modified from https://stackoverflow.com/a/63337541/19957088.
    Find all common subphrases between the 2 strings, but filer out common subphrases 
    between subphrases. For example, if "sand" is common between the 2 strings the 
    function will not return "and" unless there is another instance of "and" between 
    the 2 strings. A phrase is a string that must end in a space or be at the end 
    of the string. So "sand asdf" and "sand awer" will only match "sand " and not 
    "sand a". Spaces are expected to be meaningful. It is recommended to remove 
    punctuation from the strings.
    
    Args:
        str1 (str): one of the 2 strings to look for common substrings in.
        str2 (str): one of the 2 strings to look for common substrings in.
        min_len (int): if the length of a substring is less than this, then ignore it.
        
    Returns:
        cs_array (list): a list of the common substrings.
    """
    len1, len2 = len(str1), len(str2)

    if len1 > len2:
        str1, str2 = str2, str1 
        len1, len2 = len2, len1
    
    cs_array=[]
    cs_array_index = []
    for i in range(len1, min_len-1, -1):
        for k in range(len1-i+1):
            end_index = i + k
            sub_string = str1[k:end_index]
            if sub_string[-1] != " " and end_index < len1 and sub_string[0] != " " and k > 0:
                continue
            if sub_string in str2:
                flag = 1
                for m in range(len(cs_array)):
                    if (sub_string in cs_array[m] and\
                       ## Have to make sure the sub_string is in the same index range as what it matched.
                       ## Otherwise, "and" won't get matched between 'sand asdf and' and 'sand and'.
                       k >= cs_array_index[m][0] and end_index <= cs_array_index[m][1]) or (\
                       ## We don't want to return overlapping substrings, without the below check 'sand asdf and'
                       ## and 'sand and' will return 'sand a' and 'and' instead of 'sand a' and 'nd'.
                       ## This is undesirable for us because we plan to remove the found substrings 
                       ## after this function, and overlapping substrings make that harder.
                       (k >= cs_array_index[m][0] and k < cs_array_index[m][1])):
                        flag=0
                        break
                if flag == 1:
                    cs_array.append(sub_string)
                    cs_array_index.append([k, end_index])
    return cs_array

## Good test phrases to understand how the function works.
# find_common_subphrases('sandc cand','sandb asdf and', 2)
# find_common_subphrases('sand and','sand asdf and', 2)
# find_common_subphrases('sand and','sand qsdf and', 2)

