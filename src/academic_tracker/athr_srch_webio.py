# -*- coding: utf-8 -*-
"""
Author Search Webio
~~~~~~~~~~~~~~~~~~~

Internet interfacing for author_search.
"""


import time
import copy
import traceback

import pymed
import orcid
import scholarly
import habanero

from . import helper_functions
from . import webio



TOOL = webio.TOOL
DOI_URL = webio.DOI_URL

PUBLICATION_TEMPLATE = webio.PUBLICATION_TEMPLATE


## TODO get with pymed and add grants and pmcid to PubMedArticle class.
def search_PubMed_for_pubs(running_pubs, authors_json, from_email, citation_match_ratio, prev_query=None):
    """Searhes PubMed for publications by each author.
    
    For each author in authors_json PubMed is queried for the publications. The list of publications is then filtered 
    by affiliations and cutoff_year. If the publication is in the of running_pubs then it tries to fill in missing 
    information from this source. If the author doesn't have at least one matching affiliation then the publication 
    is skipped. If the publication was published before the cutoff_year then it is skipped. If prev_query is given, then 
    publications will be taken from it instead of querying PubMed again. 
    
    Args:
        running_pubs (dict): dictionary of publications matching the JSON schema for publications.
        authors_json (dict): keys are authors and values are author attributes. Matches Authors section of configuration JSON schema.
        from_email (str): used in the query to PubMed.
        citation_match_ratio (int): if the fuzzy ratio between 2 citations is greater than or equal to this, then consider them to match.
        prev_query (dict|None): a dictionary containing publications from a previous call to this function. {author1: [pub1, ...], ...}
        
    Returns:
        running_pubs (dict): keys are publication ids and values are a dictionary with publication attributes
        all_pubs (dict): a dictionary where the keys are the authors in authors_json and the values are a list of the publications queried for them.
    """
    
    ## Some helpful code to get the xml back as text. import xml.etree.ElementTree as ET    ET.tostring(Element)    ET.ElementTree(element).write('path')
    # initiate PubMed API
    pubmed = pymed.PubMed(tool=TOOL, email=from_email)
    
    all_pubs = {}
    
    ########################
    # loop through list of authors and request a list of their publications
    ########################
    for author, author_attributes in authors_json.items():
        all_pubs[author] = []
        
        publications = pubmed.query(author_attributes["pubmed_name_search"], max_results=500) if not prev_query else prev_query[author]
        
        ## Unpacking pub from publications appears to be the slowest part of the code.
        ## publications is an iterator that is broken up into batches and there are noticeable slow downs each time a new batch is fetched.
        for pub in publications:
            all_pubs[author].append(pub)
            
            pub_dict = helper_functions.modify_pub_dict_for_saving(pub)
            pub_id = DOI_URL + pub_dict["doi"] if pub_dict["doi"] else pub_dict["pubmed_id"]
            
            if matching_pub_id := helper_functions.get_pub_id_in_publication_dict(pub_id, pub.title, running_pubs):
                if "PubMed" in running_pubs[matching_pub_id]["queried_sources"]:
                    continue
                
                helper_functions._merge_pub_dicts(running_pubs[matching_pub_id], pub_dict, citation_match_ratio)
                running_pubs[matching_pub_id]["queried_sources"].append("PubMed")
            else:
                    
                ## Sometimes the publication_date can be None, so just skip it.
                if not pub.publication_date:
                    continue
                publication_date = int(str(pub.publication_date)[:4])
                
                ## if the publication date is before the cutoff year then skip.
                if publication_date < author_attributes["cutoff_year"]:
                    continue
                
                author_list = helper_functions.match_authors_in_pub_PubMed(authors_json, pub.authors)
        
                ## If no authors were matched then go to the next publication. Note that this is not uncommon because PubMed returns publications for authors who were just colloborators.
                if not author_list:
                    continue
                    
                pub_dict["authors"] = author_list
                pub_dict["queried_sources"] = ["PubMed"]
                running_pubs[pub_id] = pub_dict
                    
            
        # don't piss off NCBI
        time.sleep(1)
        
    return running_pubs, all_pubs


       
        
        
def search_ORCID_for_pubs(running_pubs, ORCID_key, ORCID_secret, authors_json, citation_match_ratio, prev_query=None):
    """Searhes ORCID for publications by each author.
    
    For each author in authors_json ORCID is queried for the publications. The list of publications is then filtered 
    by affiliations and cutoff_year. If the author doesn't have at least one matching affiliation, then the publication 
    is skipped. If the publication was published before the cutoff_year, then it is skipped. If prev_query is given, then publications 
    will be taken from it instead of querying ORCID again. 
    
    Args:
        running_pubs (dict): dictionary of publications matching the JSON schema for publications.
        ORCID_key (str): string of the app key ORCID gives when you register the app with them
        ORCID_secret (str): string of the secret ORCID gives when you register the app with them
        authors_json (dict): keys are authors and values are author attributes. Matches authors JSON schema.
        citation_match_ratio (int): if the fuzzy ratio between 2 citations is greater than or equal to this, then consider them to match.
        prev_query (dict|None): a dictionary containing publications from a previous call to this function. {author1: [pub1, ...], ...}
        
    Returns:
        running_pubs (dict): keys are publication ids and values are a dictionary with publication attributes
        all_pubs (dict): a dictionary where the keys are the authors in authors_json and the values are a list of the publications queried for them.
    """
    
    if prev_query is None:
        api = orcid.PublicAPI(ORCID_key, ORCID_secret)
        search_token = api.get_search_token_from_orcid()
    
    all_pubs = {}

    for author, authors_attributes in authors_json.items():
        all_pubs[author] = []
        
        if not "ORCID" in authors_attributes:
            continue
        
        works = api.read_record_public(authors_attributes["ORCID"], 'works', search_token)["group"] if prev_query is None else prev_query[author]
        
        for work in works:
            all_pubs[author].append(work)
            
            title = None
            doi = None
            external_url = None
            publication_year = None
            publication_month = None
            publication_day = None
            pmid = None
            ## If the work is not a journal article then skip it.
            work_is_a_journal_article = True
            work_before_relevant_year = False
            for work_summary in work["work-summary"]:
                
                if work_summary["type"] != "JOURNAL_ARTICLE":
                    work_is_a_journal_article = False
                    break
                
                
                if work_summary["publication-date"]:
                    if not publication_year and work_summary["publication-date"]["year"]:
                        publication_year = int(work_summary["publication-date"]["year"]["value"])
                        
                    if not publication_month and work_summary["publication-date"]["month"]:
                        publication_month = int(work_summary["publication-date"]["month"]["value"])
                        
                    if not publication_day and work_summary["publication-date"]["day"]:
                        publication_day = int(work_summary["publication-date"]["day"]["value"])

                    if publication_year is not None and publication_year < authors_attributes["cutoff_year"]:
                        work_before_relevant_year = True
                        break
                
                
                if work_summary["title"] and not title:
                    title = work_summary["title"]["title"]["value"]
                
                if not doi:
                    for external_id in work_summary["external-ids"]["external-id"]:
                        if external_id["external-id-type"] == "doi":
                            doi = external_id["external-id-value"].lower()
                            break
                        elif external_id["external-id-url"]:
                            external_url = external_id["external-id-url"]["value"]
                        elif external_id["external-id-type"] == "pmid":
                            pmid = external_id["external-id-value"]
                
                if title and doi and publication_year and publication_month and publication_day:
                    break
            
                        
            ## Try to find a way to give the publication an ID.
            if doi:
                pub_id = DOI_URL + doi
            elif external_url:
                pub_id = external_url
            elif pmid:
                pub_id = pmid
            elif not prev_query and title is not None:
                helper_functions.vprint("Warning: Could not find a DOI, URL, or PMID for a publication when searching ORCID. It will not be in the publications", verbosity=1)
                helper_functions.vprint("Title: " + title, verbosity=1)
                continue
            else:
                continue
            
            ## Pretty sure the title is never None, but if it is then there will be an error, so skip.
            if title is None:
                continue
            
            ## Pull out relevant information from ORCID.
            pub_dict = copy.deepcopy(PUBLICATION_TEMPLATE)
            if doi:
                pub_dict["doi"] = doi
            if title:
                pub_dict["title"] = title
            if publication_year:
                pub_dict["publication_date"]["year"] = publication_year
            if publication_month:
                pub_dict["publication_date"]["month"] = publication_month
            if publication_day:
                pub_dict["publication_date"]["day"] = publication_day
            if pmid:
                pub_dict["pubmed_id"] = pmid
                
            author_dict = {"affiliation": ",".join(authors_attributes["affiliations"]),
                           "firstname": authors_attributes["first_name"],
                           "initials": None,
                           "lastname": authors_attributes["last_name"],
                           "author_id" : author}
            
            pub_dict["authors"] = [author_dict]
            
            
            ## If the publication is already in running_pubs then try to update missing information.
            if matching_pub_id := helper_functions.get_pub_id_in_publication_dict(pub_id, title, running_pubs):
                if "ORCID" in running_pubs[matching_pub_id]["queried_sources"]:
                    continue
                
                helper_functions._merge_pub_dicts(running_pubs[matching_pub_id], pub_dict, citation_match_ratio)
                running_pubs[matching_pub_id]["queried_sources"].append("ORCID")
            
            else:
            
                if work_before_relevant_year or not work_is_a_journal_article or not publication_year:
                    continue
                    
                pub_dict["queried_sources"] = ["ORCID"]
                running_pubs[pub_id] = pub_dict
                
        time.sleep(1)
        
    return running_pubs, all_pubs




def search_Google_Scholar_for_pubs(running_pubs, authors_json, mailto_email, citation_match_ratio, prev_query=None):
    """Searhes Google Scholar for publications by each author.
    
    For each author in authors_json Google Scholar is queried for the publications. The list of publications is then filtered 
    by affiliations and cutoff_year. If the author doesn't have at least one matching affiliation, then the publication is 
    skipped. If the publication was published before the cutoff_year, then it is skipped. If prev_query is given, then publications 
    will be taken from it instead of querying Google Scholar again. 
    
    Args:
        running_pubs (dict): dictionary of publications matching the JSON schema for publications.
        authors_json (dict): keys are authors and values are author attributes. Matches authors JSON schema.
        mailto_email (str): used in the query to Crossref when trying to find DOIs for the articles.
        citation_match_ratio (int): if the fuzzy ratio between 2 citations is greater than or equal to this, then consider them to match.
        prev_query (dict|None): a dictionary containing publications from a previous call to this function. {author1: [pub1, ...], ...}
        
    Returns:
        running_pubs (dict): keys are pulication ids and values are a dictionary with publication attributes
        all_pubs (dict): a dictionary where the keys are the authors in authors_json and the values are a list of the publications queried for them.
    """
    
    all_pubs = {}
    for author, authors_attributes in authors_json.items():
        all_pubs[author] = []
        
        if not "scholar_id" in authors_attributes:
            continue
        
        ## Either query Google Scholar or use the prev_query parameter.
        if not prev_query:
            try:
                queried_author = scholarly.scholarly.search_author_id(authors_attributes["scholar_id"])
            except:
                message = "Warning: The \"scholar_id\" for author " + author + " is probably incorrect, an error occured when trying to query Google Scholar.\n"
                message += traceback.format_exc()
                helper_functions.vprint(message, verbosity=1)    
                continue
            
            if not queried_author["scholar_id"] == authors_attributes["scholar_id"]:
                continue
            
            ## Note that fill modifies the passed dictionary directly, but this is easier to mock in unit tests.
            queried_author = scholarly.scholarly.fill(queried_author, sections=["publications"])
            publications = queried_author["publications"]
        else:
            publications = prev_query[author]
        
        ## Loop over queried publications.
        for i, pub in enumerate(publications):
            all_pubs[author].append(pub)
            
            ## Determine the pub_id
            title = pub["bib"]["title"]
            doi = webio.get_DOI_from_Crossref(title, mailto_email) if prev_query is None else pub["doi"]
            all_pubs[author][i]["doi"] = doi
            if doi:
                pub_id = DOI_URL + doi
            else:
                pub = scholarly.scholarly.fill(pub)
                ## The fill method modifies the original pub I think, so this line isn't necessary.
                # all_pubs[author][-1] = pub
                if "pub_url" in pub:
                    pub_id = pub["pub_url"]
                elif not prev_query:
                    helper_functions.vprint("Warning: Could not find a DOI, URL, or PMID for a publication when searching Google Scholar. It will not be in the publications.", verbosity=1)
                    helper_functions.vprint("Title: " + title, verbosity=1)
                    continue
                else:
                    continue
            
            ## Build pub_dict
            publication_year = int(pub["bib"]["pub_year"]) if "pub_year" in pub["bib"] else None
            
            pub_dict = copy.deepcopy(PUBLICATION_TEMPLATE)
            if doi:
                pub_dict["doi"] = doi
            if title:
                pub_dict["title"] = title
            if publication_year:
                pub_dict["publication_date"]["year"] = publication_year
            
            pub_dict["authors"] = [{"affiliation": ",".join(authors_attributes["affiliations"]),
                                    "firstname": authors_attributes["first_name"],
                                    "initials": None,
                                    "lastname": authors_attributes["last_name"],
                                    "author_id" : author}]
            
            
            ## If the publication is already in running_pubs then try to update missing information.
            if matching_pub_id := helper_functions.get_pub_id_in_publication_dict(pub_id, title, running_pubs):
                if "Google Scholar" in running_pubs[matching_pub_id]["queried_sources"]:
                    continue
                
                helper_functions._merge_pub_dicts(running_pubs[matching_pub_id], pub_dict, citation_match_ratio)
                running_pubs[matching_pub_id]["queried_sources"].append("Google Scholar")
            
            else:
            
                ## Check if the publication year is in range.
                if not publication_year or publication_year < authors_attributes["cutoff_year"]:
                    continue
                
                pub_dict["queried_sources"] = ["Google Scholar"]
                running_pubs[pub_id] = pub_dict
                            
        time.sleep(1)
            
    return running_pubs, all_pubs





def search_Crossref_for_pubs(running_pubs, authors_json, mailto_email, citation_match_ratio, prev_query=None):
    """Searhes Crossref for publications by each author.
    
    For each author in authors_json Crossref is queried for the publications. The list of publications is then filtered 
    by affiliations and cutoff_year. If the author doesn't have at least one matching affiliation, then the publication 
    is skipped. If the publication was published before the cutoff_year, then it is skipped. Each publication is then 
    determined to have citations for any of the grants in the author's grants. If prev_query is given, then publications 
    will be taken from it instead of querying Crossref again. 
    
    Args:
        running_pubs (dict): dictionary of publications matching the JSON schema for publications.
        authors_json (dict): keys are authors and values are author attributes. Matches authors JSON schema.
        mailto_email (str): used in the query to Crossref.
        citation_match_ratio (int): if the fuzzy ratio between 2 citations is greater than or equal to this, then consider them to match.
        prev_query (dict|None): a dictionary containing publications from a previous call to this function. {author1: [pub1, ...], ...}
        
    Returns:
        running_pubs (dict): keys are pulication ids and values are a dictionary with publication attributes
        all_pubs (dict): a dictionary where the keys are the authors in authors_json and the values are a list of the publications queried for them.
    """
    
    cr = habanero.Crossref(ua_string = "Academic Tracker (mailto:" + mailto_email + ")")
    
    all_pubs = {}
    for author, authors_attributes in authors_json.items():
        all_pubs[author] = []
        
        ## Query Crossref or use prev_query.
        if not prev_query:
            results = cr.works(query_author = authors_attributes["pubmed_name_search"], 
                               filter = {"type":"journal-article", "from-pub-date":str(authors_attributes["cutoff_year"])}, 
                               limit = 300)
            publications = results["message"]["items"]
        else:
            publications = prev_query[author]
        
        ## Loop over publications.
        for work in publications:
            all_pubs[author].append(work)
            
            if "title" in work:
                title = work["title"][0]
            else:
                continue
            
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
                helper_functions.vprint("Warning: Could not find a DOI or external URL for a publication when searching Crossref. It will not be in the publications.", verbosity=1)
                helper_functions.vprint("Title: " + title, verbosity=1)
                continue
            else:
                continue
            
            ## Determine authors and put them in unified form.
            author_list = helper_functions.match_authors_in_pub_Crossref(authors_json, work["author"])
            new_author_list = []
            for cr_author_dict in author_list:
                
                temp_dict = {"lastname":cr_author_dict["family"], "initials":None,}
                
                temp_dict["firstname"] = cr_author_dict["given"] if "given" in cr_author_dict else None
                
                if cr_author_dict["affiliation"] and "name" in cr_author_dict["affiliation"][0]:
                    temp_dict["affiliation"] = cr_author_dict["affiliation"][0]["name"]
                else:
                    temp_dict["affiliation"] = None
                    
                if "author_id" in cr_author_dict:
                    temp_dict["author_id"] = cr_author_dict["author_id"]
                
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
            
            
            ## look for grants in results
            if "funder" in work:
                ## the grant string could be in any value of the funder dict so look for it in each one.
                found_grants = {grant for funder in work["funder"] for value in funder.values() for grant in authors_attributes["grants"] if grant in value}
                found_grants = list(found_grants) if found_grants else None
            else:
                found_grants = None
                
            ## Look for journal
            journal = work["publisher"] if "publisher" in work else None
            
            ## Look for references and put them in unified form.
            references = []
            if "reference" in work:
                for reference in work["reference"]:
                    if "DOI" in reference:
                        ref_doi = DOI_URL + reference["DOI"]
                    else:
                        ref_doi = None
                    references.append({"citation":reference.get("unstructured"),
                                       "title":reference.get("article-title"),
                                       "PMCID":None,
                                       "pubmed_id":None,
                                       "doi":ref_doi})
                
        
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
            if found_grants:
                pub_dict["grants"] = found_grants
                
            pub_dict["authors"] = new_author_list
            pub_dict["title"] = title
            pub_dict["references"] = references
            
            
            ## If the publication is already in running_pubs then try to update missing information.
            if matching_pub_id := helper_functions.get_pub_id_in_publication_dict(pub_id, title, running_pubs):
                if "Crossref" in running_pubs[matching_pub_id]["queried_sources"]:
                    continue
                
                helper_functions._merge_pub_dicts(running_pubs[matching_pub_id], pub_dict, citation_match_ratio)
                running_pubs[matching_pub_id]["queried_sources"].append("Crossref")
            
            else:
            
                if publication_year < authors_attributes["cutoff_year"]:
                    continue
                ## If the author_list is empty then there were no matching authors, continue.
                if not author_list:
                    continue
            
                pub_dict["queried_sources"] = ["Crossref"]
                running_pubs[pub_id] = pub_dict
            
        time.sleep(1)
            
            
    return running_pubs, all_pubs
