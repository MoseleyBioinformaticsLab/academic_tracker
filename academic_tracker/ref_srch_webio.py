# -*- coding: utf-8 -*-
"""
Internet interfacing for reference_search
"""

import time
import copy
import sys

import pymed
import scholarly
import habanero
import bs4
import fuzzywuzzy.fuzz

from . import helper_functions
from . import citation_parsing
from . import webio


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
    
    for PMID in PMID_list:
        
        publications = pubmed.query(PMID, max_results=10)
        
        for pub in publications:
            
            pub_id = pub.pubmed_id.split("\n")[0]
            if pub_id == PMID:
                publication_dict[pub_id] = helper_functions.modify_pub_dict_for_saving(pub)
                break
                
        time.sleep(1)

    return publication_dict



def search_references_on_PubMed(tokenized_citations, from_email, verbose):
    """Searhes PubMed for publications matching the citations.
    
    For each citation in tokenized_citations PubMed is queried for the publication. 
    
    Args:
        tokenized_citations (list): list of citations parsed from a source. Each citation is a dict {"authors", "title", "DOI", "PMID"}.
        from_email (str): used in the query to PubMed
        verbose (bool): Determines whether errors are silenced or not.
        
    Returns:
        publication_dict (dict): keys are pulication ids and values are a dictionary with publication attributes
    """
       
    # initiate PubMed API
    pubmed = pymed.PubMed(tool=TOOL, email=from_email)
    
    publication_dict = dict()
    titles = []
    matching_key_for_citation = []
    
    for citation in tokenized_citations:
        
        if citation["PMID"]:
            query_string = citation["PMID"]
        elif citation["DOI"]:
            query_string = citation["DOI"]
        elif citation["title"]:
            query_string = citation["title"]
        else:
            matching_key_for_citation.append(None)
            continue
        
        publications = pubmed.query(query_string, max_results=10)
        
        citation_matched = False
        for pub in publications:
            
            pmid = pub.pubmed_id.split("\n")[0]
            pub_id = DOI_URL + pub.doi.lower() if pub.doi else pmid
            
            if helper_functions.is_pub_in_publication_dict(pub_id, pub.title, publication_dict, titles):
                continue
            
            ## Match publication to the citation.
            pub_matched = False
            if citation["PMID"] == pmid:
                pub_matched = True
            elif pub.doi and citation["DOI"] == pub.doi.lower():
                pub_matched = True
            else:
                has_matching_author = any([author_items.get("lastname").lower() == author_attributes["last"].lower() for author_items in pub.authors for author_attributes in citation["authors"] if author_items.get("lastname") and author_attributes["last"]])
                if has_matching_author and fuzzywuzzy.fuzz.ratio(citation["title"], pub.title) >= 90:
                    pub_matched = True
                               
            if not pub_matched:
                continue
                        
            
            pub_dict = helper_functions.modify_pub_dict_for_saving(pub)
            
            publication_dict[pub_id] = pub_dict
            titles.append(pub_dict["title"])
            matching_key_for_citation.append(pub_id)
            citation_matched = True
            break
                    
        if not citation_matched:
            matching_key_for_citation.append(None)
        time.sleep(1)
        
    return publication_dict, matching_key_for_citation


       

def search_references_on_Google_Scholar(tokenized_citations, mailto_email, verbose):
    """Searhes Google Scholar for publications that match the citations.
        
    Args:
        tokenized_citations (list): list of citations parsed from a source. Each citation is a dict {"authors", "title", "DOI", "PMID"}.
        mailto_email (str): used in the query to Crossref when trying to find DOIs for the articles
        verbose (bool): Determines whether errors are silenced or not.
        
    Returns:
        publication_dict (dict): keys are pulication ids and values are a dictionary with publication attributes
    """
    
    publication_dict = {}
    titles = []
    matching_key_for_citation = []
    for citation in tokenized_citations:
        
        if citation["title"]:
            query = scholarly.scholarly.search_pubs(citation["title"])
        else:
            matching_key_for_citation.append(None)
            continue
        
        citation_matched = False
        for count, pub in enumerate(query):
            
            if count > 50:
                break
            
            time.sleep(1)
            
            title = pub["bib"]["title"]
            
            ## authors from Google Scholar are last names and initials in a single string, each string in one list. ['SA Cholewiak', 'RW Fleming', 'M Singh']
            pub_matched = False
            has_matching_author = any([author_attributes["last"].lower() in author.lower() for author in pub["bib"]["author"] for author_attributes in citation["authors"]])
            if has_matching_author and fuzzywuzzy.fuzz.ratio(citation["title"], title) >= 90:
                pub_matched = True
                               
            if not pub_matched:
                continue
            
            ## Find the publication year and check that it is in range.
            if "pub_year" in pub["bib"]:
                publication_year = int(pub["bib"]["pub_year"])
            else:
                publication_year = None
        
            
            ## Determine the pub_id
            doi = webio.get_DOI_from_Crossref(title, mailto_email)
            if doi:
                pub_id = DOI_URL + doi
            else:
                if "pub_url" in pub:
                    pub_id = pub["pub_url"]
                else:
                    print("Warning: Could not find a DOI, URL, or PMID for a publication when searching Google Scholar. It will not be in the publications.")
                    print("Title: " + title)
                    break
            
            
            pub_dict = copy.deepcopy(PUBLICATION_TEMPLATE)
            if doi:
                pub_dict["doi"] = doi
            if title:
                pub_dict["title"] = title
            if publication_year:
                pub_dict["publication_date"]["year"] = publication_year
                
            
            if not helper_functions.is_pub_in_publication_dict(pub_id, title, publication_dict, titles):
                pub_dict["authors"] = [{"affiliation": None,
                                        "firstname": None,
                                        "initials": None,
                                        "lastname": author["last"]} for author in citation["authors"]]
                publication_dict[pub_id] = pub_dict
                titles.append(title)
                matching_key_for_citation.append(pub_id)
                citation_matched = True
            
            break
        
        if not citation_matched:
            matching_key_for_citation.append(None)
        
    return publication_dict, matching_key_for_citation




def search_references_on_Crossref(tokenized_citations, mailto_email, verbose):
    """Searhes Crossref for publications matching the citations.
    
    Args:
        tokenized_citations (list): list of citations parsed from a source. Each citation is a dict {"authors", "title", "DOI", "PMID"}.
        mailto_email (str): used in the query to Crossref
        verbose (bool): Determines whether errors are silenced or not.
        
    Returns:
        publication_dict (dict): keys are pulication ids and values are a dictionary with publication attributes
    """
    
    cr = habanero.Crossref(ua_string = "Academic Tracker (mailto:" + mailto_email + ")")
    
    publication_dict = {}
    titles = []
    matching_key_for_citation = []
    for citation in tokenized_citations:
        
        if citation["DOI"]:
            results = cr.works(ids = citation["DOI"])
            works = [results["message"]]
        elif citation["title"]:
            results = cr.works(query_bibliographic = citation["title"], filter = {"type":"journal-article"}, limit = 10)
            works = results["message"]["items"]
        else:
            matching_key_for_citation.append(None)
            continue
        
        citation_matched = False
        for work in works:
            
            ## Look for DOI
            if "DOI" in work:
                doi = work["DOI"].lower()
            else:
                doi = None
             
            ## Look for title    
            if "title" in work and work["title"]:
                title = work["title"][0]
            else:
                continue
            
            pub_matched = False
            if citation["DOI"] == doi:
                pub_matched = True
            else:
                if "author" in work:
                    has_matching_author = any([author_items.get("family").lower() == author_attributes["last"].lower() for author_items in work["author"] for author_attributes in citation["authors"] if "family" in author_items and author_items.get("family")])
                    if has_matching_author and fuzzywuzzy.fuzz.ratio(citation["title"], title) >= 90:
                        pub_matched = True
                               
            if not pub_matched:
                matching_key_for_citation.append(None)
                continue
            
            
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
                date_length = len(work[date_key]["date-parts"])
                
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
            
            
            ## Change the author list to a form like PubMed's
            new_author_list = []
            for cr_author_dict in work["author"]:
                
                temp_dict = {"lastname":cr_author_dict["family"], "initials":None,}
                
                if "given" in cr_author_dict:
                    temp_dict["firstname"] = cr_author_dict["given"]
                else:
                    temp_dict["firstname"] = None
                
                if cr_author_dict["affiliation"] and "name" in cr_author_dict["affiliation"][0]:
                    temp_dict["affiliation"] = cr_author_dict["affiliation"][0]["name"]
                else:
                    temp_dict["affiliation"] = None
                    
                if "author_id" in cr_author_dict:
                    temp_dict["author_id"] = cr_author_dict["author_id"]
                
                new_author_list.append(temp_dict)
            
            
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
            else:
                print("Could not find a DOI or external URL for a publication when searching Crossref. It will not be in the publications.")
                print("Title: " + title)
                continue
            
            
            
            if helper_functions.is_pub_in_publication_dict(pub_id, title, publication_dict, titles):
                continue
            
            
            ## Look for journal
            if "publisher" in work:
                journal = work["publisher"]
            else:
                journal = None
                
        
            ## Build the pub_dict from what we were able to collect.
            pub_dict = copy.deepcopy(PUBLICATION_TEMPLATE)
            if doi:
                pub_dict["doi"] = doi
            if publication_year:
                pub_dict["publication_date"]["year"] = publication_year
            if publication_month:
                pub_dict["publication_date"]["month"] = publication_month
            if publication_day:
                pub_dict["publication_date"]["day"] = publication_day
            if journal:
                pub_dict["journal"] = journal
                
            pub_dict["authors"] = new_author_list
            pub_dict["title"] = title
            
            
            publication_dict[pub_id] = pub_dict
            titles.append(title)
            matching_key_for_citation.append(pub_id)
            citation_matched = True
            break
        
        if not citation_matched:
            matching_key_for_citation.append(None)
        time.sleep(1)
            
            
    return publication_dict, matching_key_for_citation
        
                



def parse_myncbi_citations(url, verbose):
    """
    Note that authors and title can be missing or empty from the webpage.
    """
    
    ## Get the first page, find out the total pages, and parse it.
    url_str = webio.get_url_contents_as_str(url, verbose)
    if not url_str:
        print("Error: Could not access the MYNCBI webpage. Make sure the address is correct.")
        sys.exit()
    
    soup = bs4.BeautifulSoup(url_str, "html.parser")
    number_of_pages = int(soup.find("span", class_ = "totalPages").text)
    
    parsed_pubs, reference_lines = citation_parsing.tokenize_myncbi_citations(url_str)
    
    ## Parse the rest of the pages.    
    if url[-1] == "/":
        new_url = url
    else:
        new_url = url + "/"
    
    for i in range(2,number_of_pages+1):
        
        url_str = webio.get_url_contents_as_str(new_url + "?page=" + str(i), verbose)
        if not url_str:
            print("Error: Could not access page " + str(i) + " of the MYNCBI webpage. Aborting run.")
            sys.exit()
        
        temp_pubs, temp_lines = citation_parsing.tokenize_myncbi_citations(url_str)
        parsed_pubs += temp_pubs
        reference_lines += temp_lines
        
    return parsed_pubs, reference_lines





