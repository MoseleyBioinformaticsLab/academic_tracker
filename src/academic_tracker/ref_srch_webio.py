# -*- coding: utf-8 -*-
"""
Reference Search Webio
~~~~~~~~~~~~~~~~~~~~~~

Internet interfacing for reference_search.
"""

import time
import copy
import sys
import os
import re

import pymed
import scholarly
import habanero
import bs4

from . import helper_functions
from . import citation_parsing
from . import webio
from . import fileio
from . import user_input_checking


TOOL = webio.TOOL
DOI_URL = webio.DOI_URL

PUBLICATION_TEMPLATE = webio.PUBLICATION_TEMPLATE


def build_pub_dict_from_PMID(PMID_list, from_email):
    """Query PubMed for each PMID and build a dictionary of the returned data.
    
    Args:
        PMID_list (list): A list of PMIDs as strings.
        from_email (str): An email address to use when querying PubMed.
        
    Returns:
        publication_dict (dict): keys are pulication ids and values are a dictionary with publication attributes.
    """
    
    pubmed = pymed.PubMed(tool=TOOL, email=from_email)
    
    publication_dict = dict()
    
    for PMID_to_search in PMID_list:
        
        publications = pubmed.query(PMID_to_search, max_results=10)
        
        for pub in publications:
            pub_id, pub_dict = helper_functions.create_pub_dict_for_saving_PubMed(pub)
            
            if pub_dict["pubmed_id"] == PMID_to_search:
                publication_dict[pub_id] = pub_dict
                break
                
        time.sleep(1)

    return publication_dict



# def search_references_on_PubMed(running_pubs, tokenized_citations, from_email, prev_query=None):
#     """Searhes PubMed for publications matching the citations.
    
#     For each citation in tokenized_citations PubMed is queried for the publication. 
#     If the publication is already in running_pubs then missing information will be 
#     filled in if possible.
    
#     Args:
#         running_pubs (dict): dictionary of publications matching the JSON schema for publications.
#         tokenized_citations (list): list of citations parsed from a source. Each citation is a dict {"authors", "title", "DOI", "PMID", "reference_line", "pub_dict_key"}.
#         from_email (str): used in the query to PubMed.
#         prev_query (list|None): a list of lists containing publications from a previous call to this function. [[pub1, ...], [pub1, ...], ...]
        
#     Returns:
#         running_pubs (dict): keys are pulication ids and values are a dictionary with publication attributes
#         matching_key_for_citation (list): list of keys to the publication matching the citation at the same index
#         all_pubs (list): list of lists, each index is the pubs searched through after querying until the citation was matched
#     """
       
#     # initiate PubMed API
#     pubmed = pymed.PubMed(tool=TOOL, email=from_email)
    
#     all_pubs = []
#     matching_key_for_citation = []
    
#     for i, citation in enumerate(tokenized_citations):
#         all_pubs.append([])
        
#         if citation["PMID"]:
#             query_string = citation["PMID"]
#         elif citation["DOI"]:
#             query_string = citation["DOI"]
#         elif citation["title"]:
#             query_string = citation["title"]
#         else:
#             matching_key_for_citation.append(None)
#             continue
#         publications = pubmed.query(query_string, max_results=10) if not prev_query else prev_query[i]
        
#         citation_matched_to_pub = False
#         for pub in publications:
#             if not isinstance(pub, pymed.article.PubMedArticle):
#                 continue
#             all_pubs[i].append(pub)
            
#             pub_dict = helper_functions.create_pub_dict_for_saving_PubMed(pub)
#             pub_id = pub_dict["doi"] if pub_dict["doi"] else pub_dict["pubmed_id"]
            
#             ## Match publication to the citation.
#             if citation["PMID"] == pub_dict["pubmed_id"]:
#                 citation_matched_to_pub = True
#             elif pub.doi and citation["DOI"] and citation["DOI"].lower() == pub.doi.lower():
#                 citation_matched_to_pub = True
#             else:
#                 has_matching_author = helper_functions.match_pub_authors_to_citation_authors(citation["authors"], pub_dict["authors"])
#                 if has_matching_author and helper_functions.do_strings_fuzzy_match(citation["title"], pub_dict["title"]):
#                     citation_matched_to_pub = True
                               
#             if matching_pub_id := helper_functions.get_pub_id_in_publication_dict(pub_id, pub.title, running_pubs):
#                 if "PubMed" in running_pubs[matching_pub_id]["queried_sources"]:
#                     if not citation_matched_to_pub:
#                         continue
#                     matching_key_for_citation.append(matching_pub_id)
#                     break
                
#                 helper_functions._merge_pub_dicts(running_pubs[matching_pub_id], pub_dict)
#                 running_pubs[matching_pub_id]["queried_sources"].append("PubMed")
#                 if citation_matched_to_pub:
#                     matching_key_for_citation.append(matching_pub_id)
#                     break
            
#             else:
#                 if not citation_matched_to_pub:
#                     continue
#                 pub_dict["queried_sources"] = ["PubMed"]
#                 running_pubs[pub_id] = pub_dict
#                 matching_key_for_citation.append(pub_id)
#                 break
                            
#         if not citation_matched_to_pub:
#             matching_key_for_citation.append(None)
#         time.sleep(1)
        
#     return running_pubs, matching_key_for_citation, all_pubs




# def search_references_on_Crossref(running_pubs, tokenized_citations, mailto_email, prev_query=None):
#     """Searhes Crossref for publications matching the citations.
    
#     For each citation in tokenized_citations Crossref is queried for the publication. 
#     If the publication is already in running_pubs then missing information will be 
#     filled in if possible.
    
#     Args:
#         running_pubs (dict): dictionary of publications matching the JSON schema for publications.
#         tokenized_citations (list): list of citations parsed from a source. Each citation is a dict {"authors", "title", "DOI", "PMID", "reference_line", "pub_dict_key"}.
#         mailto_email (str): used in the query to Crossref.
#         prev_query (list|None): a list of lists containing publications from a previous call to this function. [[pub1, ...], [pub1, ...], ...]
        
#     Returns:
#         running_pubs (dict): keys are pulication ids and values are a dictionary with publication attributes
#         matching_key_for_citation (list): list of keys to the publication matching the citation at the same index
#         all_pubs (list): list of lists, each index is the pubs searched through after querying until the citation was matched
#     """
    
#     cr = habanero.Crossref(ua_string = "Academic Tracker (mailto:" + mailto_email + ")")
    
#     all_pubs = []
#     matching_key_for_citation = []
#     for i, citation in enumerate(tokenized_citations):
#         all_pubs.append([])
        
#         if not prev_query:
#             if citation["DOI"]:
#                 results = cr.works(ids = citation["DOI"])
#                 works = [results["message"]]
#             elif citation["title"]:
#                 results = cr.works(query_bibliographic = citation["title"], filter = {"type":"journal-article"}, limit = 10)
#                 works = results["message"]["items"]
#             else:
#                 matching_key_for_citation.append(None)
#                 continue
#         else:
#             works = prev_query[i]
                        
#         citation_matched_to_pub = False
#         for work in works:
#             all_pubs[i].append(work)
            
#             pub_id, pub_dict = helper_functions.create_pub_dict_for_saving_Crossref(work, prev_query)
            
#             if pub_id is None:
#                 continue
            
#             if citation["DOI"] == pub_dict["doi"]:
#                 citation_matched_to_pub = True
#             else:
#                 if "author" in work:
#                     has_matching_author = helper_functions.match_pub_authors_to_citation_authors(citation["authors"], pub_dict["authors"])
#                     if has_matching_author and helper_functions.do_strings_fuzzy_match(citation["title"], pub_dict["title"]):
#                         citation_matched_to_pub = True
                               
#             ## If the publication is already in running_pubs then try to update missing information.
#             if matching_pub_id := helper_functions.get_pub_id_in_publication_dict(pub_id, pub_dict["title"], running_pubs):
#                 if "Crossref" in running_pubs[matching_pub_id]["queried_sources"]:
#                     if not citation_matched_to_pub:
#                         continue
#                     matching_key_for_citation.append(matching_pub_id)
#                     break
                
#                 helper_functions._merge_pub_dicts(running_pubs[matching_pub_id], pub_dict)
#                 running_pubs[matching_pub_id]["queried_sources"].append("Crossref")
#                 if citation_matched_to_pub:
#                     matching_key_for_citation.append(matching_pub_id)
#                     break
            
#             else:
#                 if not citation_matched_to_pub:
#                     continue
#                 pub_dict["queried_sources"] = ["Crossref"]
#                 running_pubs[pub_id] = pub_dict
#                 matching_key_for_citation.append(pub_id)
#                 break
                    
#         if not citation_matched_to_pub:
#             matching_key_for_citation.append(None)
#         time.sleep(1)
            
#     return running_pubs, matching_key_for_citation, all_pubs
        



def search_references_on_source(source, running_pubs, tokenized_citations, mailto_email, prev_query=None):
    """Searhes source for publications matching the citations.
    
    For each citation in tokenized_citations the source is queried for the publication. 
    If the publication is already in running_pubs then missing information will be 
    filled in if possible.
    
    Possible sources are "Crossref" or "PubMed".
    
    Args:
        source (str): must be one of "Crossref" or "PubMed".
        running_pubs (dict): dictionary of publications matching the JSON schema for publications.
        tokenized_citations (list): list of citations parsed from a source. Each citation is a dict {"authors", "title", "DOI", "PMID", "reference_line", "pub_dict_key"}.
        mailto_email (str): email provided to the source when querying.
        prev_query (list|None): a list of lists containing publications from a previous call to this function. [[pub1, ...], [pub1, ...], ...]
        
    Returns:
        running_pubs (dict): keys are pulication ids and values are a dictionary with publication attributes
        matching_key_for_citation (list): list of keys to the publication matching the citation at the same index
        all_pubs (list): list of lists, each index is the pubs searched through after querying until the citation was matched
    """
       
    # initiate API
    if source == "PubMed":
        api = pymed.PubMed(tool=TOOL, email=mailto_email)
        query_function = _query_PubMed
        skip_pub_function = _pub_needs_skipped_PubMed
        pub_dict_creation_function = helper_functions.create_pub_dict_for_saving_PubMed
        pub_dict_creation_arguments = ["pub"]
    elif source == "Crossref":
        api = habanero.Crossref(ua_string = "Academic Tracker (mailto:" + mailto_email + ")")
        query_function = _query_Crossref
        skip_pub_function = _pub_needs_skipped_Crossref
        pub_dict_creation_function = helper_functions.create_pub_dict_for_saving_Crossref
        pub_dict_creation_arguments = ["pub", "prev_query"]
    else:
        helper_functions.vprint("Error: When searching references there was an attempt to query an unknown source, '" + source + "'.")
        sys.exit()
    
    all_pubs = []
    matching_key_for_citation = []
    
    for i, citation in enumerate(tokenized_citations):
        all_pubs.append([])
        
        if not prev_query:
            if not (publications := query_function(api, citation)):
                matching_key_for_citation.append(None)
                continue
        else:
            publications = prev_query[i]
        
        citation_matched_to_pub = False
        for pub in publications:
            if skip_pub_function(pub):
                continue
            all_pubs[i].append(pub)
            
            locals_ref = locals()
            pub_id, pub_dict = pub_dict_creation_function(*[locals_ref[arg] for arg in pub_dict_creation_arguments])
            
            if pub_id is None:
                continue
            
            ## Match publication to the citation.
            if pub_dict["pubmed_id"] and citation["PMID"] and pub_dict["pubmed_id"] == citation["PMID"]:
                citation_matched_to_pub = True
            elif pub_dict["doi"] and citation["DOI"] and citation["DOI"].lower() == pub_dict["doi"]:
                citation_matched_to_pub = True
            else:
                has_matching_author = helper_functions.match_pub_authors_to_citation_authors(citation["authors"], pub_dict["authors"])
                if has_matching_author and helper_functions.do_strings_fuzzy_match(citation["title"], pub_dict["title"]):
                    citation_matched_to_pub = True
            
                               
            if matching_pub_id := helper_functions.get_pub_id_in_publication_dict(pub_id, pub_dict["title"], running_pubs):
                if source in running_pubs[matching_pub_id]["queried_sources"]:
                    if not citation_matched_to_pub:
                        continue
                    matching_key_for_citation.append(matching_pub_id)
                    break
                
                helper_functions._merge_pub_dicts(running_pubs[matching_pub_id], pub_dict)
                running_pubs[matching_pub_id]["queried_sources"].append(source)
                if citation_matched_to_pub:
                    matching_key_for_citation.append(matching_pub_id)
                    break
            
            else:
                if not citation_matched_to_pub:
                    continue
                pub_dict["queried_sources"] = [source]
                running_pubs[pub_id] = pub_dict
                matching_key_for_citation.append(pub_id)
                break
                            
        if not citation_matched_to_pub:
            matching_key_for_citation.append(None)
        time.sleep(1)
        
    return running_pubs, matching_key_for_citation, all_pubs




def _query_PubMed(pubmed, citation):
    """Query PubMed with either the PMID, DOI, or title from citation.
    
    Args:
        pubmed (pymed.api.PubMed): api object from the pymed library.
        citation (dict): citation to query for.
    """
    
    if citation["PMID"]:
        query_string = citation["PMID"]
    elif citation["DOI"]:
        query_string = citation["DOI"]
    elif citation["title"]:
        query_string = citation["title"]
    else:
        return None
    return pubmed.query(query_string, max_results=10)



def _query_Crossref(cr, citation):
    """Query Crossref with either the PMID, DOI, or title from citation.
    
    Args:
        pubmed (habanero.crossref.crossref.Crossref): api object from the habanero library.
        citation (dict): citation to query for.
    """
    
    if citation["DOI"]:
        results = cr.works(ids = citation["DOI"])
        works = [results["message"]]
    elif citation["title"]:
        results = cr.works(query_bibliographic = citation["title"], filter = {"type":"journal-article"}, limit = 10)
        works = results["message"]["items"]
    else:
        return None
    return works
         

def _pub_needs_skipped_PubMed(pub):
    """Determine whether the queried pub from PubMed should be skipped or not.
    
    Args:
        pub (pymed.article.PubMedArticle|pymed.book.PubMedBookArticle): publication queried from PubMed book articles should be skipped.
    """
    
    return not isinstance(pub, pymed.article.PubMedArticle)


def _pub_needs_skipped_Crossref(pub):
    """Determine whether the queried pub from Crossref should be skipped or not.
    
    This is just here to work with the function, publications from Crossref should never be skipped.
    
    Args:
        pub (dict): publication queried from Crossref.
    """
    
    return False




def parse_myncbi_citations(url):
    """Tokenize the citations on a MyNCBI URL.
    
    Note that authors and title can be missing or empty from the webpage.
    This function assumes the url is the first page of the MyNCBI citations.
    The first page is tokenized and then each subsequent page is visited and 
    tokenized.
    
    Args:
        url (str): the url of the MyNCBI page.
        
    Returns:
        parsed_pubs (dict): the citations tokenized in a dictionary matching the tokenized citations JSON schema.    
    """
    
    ## Get the first page, find out the total pages, and parse it.
    url_str = webio.get_url_contents_as_str(url)
    if not url_str:
        helper_functions.vprint("Error: Could not access the MYNCBI webpage. Make sure the address is correct.")
        sys.exit()
    
    soup = bs4.BeautifulSoup(url_str, "html.parser")
    number_of_pages = int(soup.find("span", class_ = "totalPages").text)
    
    parsed_pubs = citation_parsing.tokenize_myncbi_citations(url_str)
    
    ## Parse the rest of the pages.
    new_url = url if url[-1] == "/" else url + "/"
    
    for i in range(2,number_of_pages+1):
        
        url_str = webio.get_url_contents_as_str(new_url + "?page=" + str(i))
        if not url_str:
            helper_functions.vprint("Error: Could not access page " + str(i) + " of the MYNCBI webpage. Aborting run.")
            sys.exit()
        
        temp_pubs = citation_parsing.tokenize_myncbi_citations(url_str)
        parsed_pubs += temp_pubs
        
    return parsed_pubs



def tokenize_reference_input(reference_input, MEDLINE_reference, remove_duplicates=True):
    """Tokenize the citations in reference_input.
    
    reference_input can be a URL or filepath. MyNCBI URLs are handled special, 
    but all other URLs are read as a text document and parsed line by line as 
    if they were a test document. If the format of the reference is MEDLINE then 
    set MEDLINE_reference to True and it will be parsed as such instead of line 
    by line. Citations are expected to be 1 per line otherwise.
    
    Args:
        reference_input (str): URL or filepath.
        MEDLINE_reference (bool): True if reference_input is in MEDLINE format.
        remove_duplicates (bool): if True, remove duplicate entries in tokenized citations.
        
    Returns:
        tokenized_citations (dict): the citations tokenized in a dictionary matching the tokenized citations JSON schema. 
    """
    
    ## Check the reference_input to see if it is json.
    extension = os.path.splitext(reference_input)[1][1:]
    if extension == "json":
        tokenized_citations = fileio.load_json(reference_input)
        user_input_checking.tok_reference_check(tokenized_citations)
    
    ## Check the reference file input and see if it is a URL
    elif re.match(r"http.*", reference_input):
        if re.match(r".*ncbi.nlm.nih.gov/myncbi.*", reference_input):
            tokenized_citations = parse_myncbi_citations(reference_input)
        else:
            document_string = webio.clean_tags_from_url(reference_input)
            
            if not document_string:
                helper_functions.vprint("Nothing was read from the URL. Make sure the address is correct.")
                sys.exit()
            
            tokenized_citations = citation_parsing.parse_text_for_citations(document_string)
    else:
        # Check the file extension and call the correct read in function.
        if extension == "docx":
            document_string = fileio.read_text_from_docx(reference_input)
        elif extension == "txt":
            document_string = fileio.read_text_from_txt(reference_input)
        else:
            helper_functions.vprint("Unknown file type for reference file.")
            sys.exit()
    
        if not document_string:
            helper_functions.vprint("Nothing was read from the reference file. Make sure the file is not empty or is a supported file type.")
            sys.exit()
        
        if MEDLINE_reference:
            tokenized_citations = citation_parsing.parse_MEDLINE_format(document_string)
        else:
            tokenized_citations = citation_parsing.parse_text_for_citations(document_string)
            
    if not tokenized_citations:
        helper_functions.vprint("Warning: Could not tokenize any citations in provided reference. Check setup and formatting and try again.")
        sys.exit()
    
    ## Look for duplicates in citations.
    if remove_duplicates:
        duplicate_citations = helper_functions.find_duplicate_citations(tokenized_citations)
        if duplicate_citations:
            helper_functions.vprint("Warning: The following citations in the reference file or URL appear to be duplicates based on identical DOI, PMID, or similar titles. They will only appear once in any outputs.", verbosity=1)
            helper_functions.vprint("Duplicates:", verbosity=1)
            for index_list in duplicate_citations:
                for index in index_list:
                    if tokenized_citations[index]["reference_line"]:
                        pretty_print = tokenized_citations[index]["reference_line"].split("\n")
                        pretty_print = " ".join([line.strip() for line in pretty_print])
                        helper_functions.vprint(pretty_print, verbosity=1)
                    else:
                        helper_functions.vprint(tokenized_citations[index]["title"], verbosity=1)
                    helper_functions.vprint("", verbosity=1)
                helper_functions.vprint("\n", verbosity=1)
            
            indexes_to_remove = [index for duplicate_set in duplicate_citations for index in duplicate_set[1:]]
            
            tokenized_citations = [citation for count, citation in enumerate(tokenized_citations) if not count in indexes_to_remove]
        
    return tokenized_citations






