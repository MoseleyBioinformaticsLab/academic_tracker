# -*- coding: utf-8 -*-
"""
This module contains the functions that interface with the internet.
"""

import urllib.request
import urllib.error
import os.path
import time
import pymed
import email.message
import subprocess
import io
from . import helper_functions
import orcid
import scholarly
import re
import habanero
import copy

TOOL = "Academic Tracker"
DOI_URL = "https://doi.org/"

## Some helpful code to get the xml back as text. import xml.etree.ElementTree as ET    ET.tostring(Element)

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


## TODO get with pymed and add grants and pmcid to PubMedArticle class.
def search_DOIs_on_pubmed(DOI_list, from_email):
    """Query PubMed for each DOI and return the ones with no PMCID.
    
    For each dictionary in DOI_list query PubMed and get more information about 
    the publication if found. Returns a list of dictionaries like DOI_list, but 
    adds a key for "Grants" and does not return publications that have a PMCID.
    
    Args:
        DOI_list (list): A list of dictionaries. 
        [{"DOI":"publication DOI", "PMID": "publication PMID", "line":"short description of the publication"}]
        from_email (str): An email to use when querying PubMed.
        
    Returns:
        publications_with_no_PMCID_list (list): A list of dictionaries.
        [{"DOI":"publication DOI", "PMID": "publication PMID", "line":"short description of the publication", "Grants":"grants funding the publication"}]
        
    """
    
    publications_with_no_PMCID_list = []
    
    pubmed = pymed.PubMed(tool=TOOL, email=from_email)
    
    for dictionary in DOI_list:
        if dictionary["PMID"]:
            query_string = dictionary["PMID"]
        else:
            query_string = dictionary["DOI"]
        
        publications = pubmed.query(query_string, max_results=10)
        
        match_found_in_query = False
        at_least_one_result_found = False
        for pub in publications:
            at_least_one_result_found = True
            if dictionary["DOI"] == pub.doi:
                match_found_in_query = True
                PMC_id_elements = pub.xml.findall(".//ArticleId[@IdType='pmc']")
                if PMC_id_elements:
                    continue
#                    PMC_id = PMC_id_elements[0].text
                
                dictionary["Grants"] = [grant.text for grant in pub.xml.findall(".//GrantID")]
                dictionary["PMID"] = pub.pubmed_id.split("\n")[0]
                publications_with_no_PMCID_list.append(dictionary)
                break
                
            
            else:
                continue
        
        if not match_found_in_query or not at_least_one_result_found:
            dictionary["Grants"] = []
            dictionary["PMID"] = ""
            publications_with_no_PMCID_list.append(dictionary)
        
    return publications_with_no_PMCID_list


                



def search_PubMed_for_pubs(prev_pubs, authors_json_file, from_email, verbose):
    """Searhes PubMed for publications by each author.
    
    For each author in authors_json_file PubMed is queried for the publications. The list of publications is then filtered 
    by prev_pubs, affiliations, and cutoff_year. If the publication is in the list of prev_pubs then it is skipped. 
    If the author doesn't have at least one matching affiliation then the publication is skipped. If the publication 
    was published before the cutoff_year then it is skipped. Each publication is then determined to have citations 
    for any of the grants in the author's grants.
    
    Args:
        prev_pubs (list): List of publications ids as strings to filter publications found on PubMed
        authors_json_file (dict): keys are authors and values are author attributes. Matches authors JSON schema.
        from_email (str): used in the query to PubMed
        verbose (bool): Determines whether errors are silenced or not.
        
    Returns:
        publication_dict (dict): keys are pulication ids and values are a dictionary with publication attributes
    """
       
    # initiate PubMed API
    pubmed = pymed.PubMed(tool=TOOL, email=from_email)
    
    publication_dict = dict()
    prev_pubs_titles = [pub_attr["title"] for pub_attr in prev_pubs.values()]
    titles = []
    
    ########################
    # loop through list of authors and request a list of their publications
    ########################
    for author, author_attributes in authors_json_file.items():
        
        publications = pubmed.query(author_attributes["pubmed_name_search"], max_results=500)
        
        ## Unpacking pub from publications appears to be the slowest part of the code.
        ## publications is an iterator that is broken up into batches and there are noticeable slow downs each time a new batch is fetched.
        for pub in publications:
            
            pub_id = DOI_URL + pub.doi if pub.doi else pub.pubmed_id.split("\n")[0]
            publication_date = int(str(pub.publication_date)[:4])
            
            ## if the publication id is in prev_pubs or publication_dict or the publication date is before the curoff year then skip.
            if publication_date < author_attributes["cutoff_year"] or \
               helper_functions.is_pub_in_publication_dict(pub_id, pub.title, prev_pubs, prev_pubs_titles) or \
               helper_functions.is_pub_in_publication_dict(pub_id, pub.title, publication_dict, titles):
                continue
            
            author_list = helper_functions.match_authors_in_pub_PubMed(authors_json_file, pub.authors)
    
            ## If no authors were matched then go to the next publication. Note that this is not uncommon because PubMed returns publications for authors who were just colloborators.
            if not author_list:
                continue
                
            pub.authors = author_list
            pub_dict = helper_functions.modify_pub_dict_for_saving(pub)
            
            publication_dict[pub_id] = pub_dict
            titles.append(pub_dict["title"])
                    
                ## Look for each grant_id and if found add it to dict.
                ## TODO look for grants in DOI if not on PubMed, and in pdf. Full text link might work as well. clicking that goes to full text. There is not a direct pdf link on pubmed page.
                ## Simply do the union of the sets to add grants to the pubs_by_author_dict. Do a difference of sets to see if they were all found.
                ## Should we keep looking after finding at least one grant? Will there be multiple grants cited?
                ## For now not going to check the DOI for grants.
#                if author_attributes["grants"] - pubs_by_author_dict[author][pub_id]:
#                    pubs_by_author_dict[author][pub_id] | check_doi_for_grants(pub_dict["doi"], author_attributes["grants"], verbose)
                    
            
        # don't piss off NCBI
        time.sleep(1)
        
    return publication_dict







def check_pubmed_for_grants(pub_id, grants):
    """Searches PubMed webpage for grants.
    
    Concatenates "https://pubmed.ncbi.nlm.nih.gov/" with the pub_id, visits the 
    page and looks for the given grants on that page.
    
    Args:
        pub_id (str): PubMed ID for the publication.
        grants (list): list of str for each grant to look for.
        
    Returns:
        found_grants (list): list of str with each grant that was found on the page.
    """
    
    pub_med_url = "https://pubmed.ncbi.nlm.nih.gov/"
    
    response = urllib.request.urlopen(os.path.join(pub_med_url, pub_id))
    url_str = response.read().decode("utf-8")
    response.close()
    
    return { grant for grant in grants if grant in url_str }





def check_doi_for_grants(doi, grants, verbose):
    """Searches DOI webpage for grants.
    
    Concatenates "https://doi.org/" with the doi, visits the 
    page and looks for the given grants on that page.
    
    Args:
        doi (str): DOI for the publication.
        grants (list): list of str for each grant to look for.
        verbose (bool): if True print HTTP errors.
        
    Returns:
        found_grants (list): list of str with each grant that was found on the page.
    """
    
    doi_url = "https://doi.org/"
    
    try:
        req = urllib.request.Request(os.path.join(doi_url, doi), headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=5)
        url_str = response.read().decode("utf-8")
        response.close()
                
    except urllib.error.HTTPError as e:
        if verbose:
            print(e)
            print(os.path.join(doi_url, doi))
            
        return set()
    
    return { grant for grant in grants if grant in url_str }




def download_pdf(pdf_url, verbose):
    """
    """
    ## test url https://realpython.com/python-tricks-sample-pdf
    try:
        req = urllib.request.Request(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req)
        pdf_bytes = io.BytesIO(response.read())
        response.close()
                
    except urllib.error.HTTPError as e:
        if verbose:
            print(e)
            print(pdf_url)
        
        return None
            
    return pdf_bytes





def send_emails(email_messages):
    """Uses sendmail to send email_messages to authors.
    
    Only works on systems with sendmail installed. 
    
    Args:
        email_messages (dict): keys are author names and values are the message
    """
    sendmail_location = "/usr/sbin/sendmail"
    
    # build and send each message by looping over the email_messages dict
    for email_parts in email_messages["emails"]:
        msg = email.message.EmailMessage()
        msg["Subject"] = email_parts["subject"]
        msg["From"] = email_parts["from"]
        msg["To"] = email_parts["to"]
        msg["Cc"] = email_parts["cc"]
        msg.set_content(email_parts["body"])
        
        subprocess.run([sendmail_location, "-t", "-oi"], input=msg.as_bytes())
        



PUBLICATION_TEMPLATE = {
        "abstract": None,
        "authors": None,
        "conclusions": None,
        "copyrights": None,
        "doi": None,
        "journal": None,
        "keywords": None,
        "methods": None,
        "publication_date": {"year":None, "month":None, "day":None},
        "pubmed_id": None,
        "results": None,
        "title": None,
        "grants": None,
        "PMCID": None
   }
        
        
        
        
def search_ORCID_for_pubs(prev_pubs, ORCID_key, ORCID_secret, authors_json_file, verbose):
    """Searhes ORCID for publications by each author.
    
    For each author in authors_json_file ORCID is queried for the publications. The list of publications is then filtered 
    by prev_pubs, affiliations, and cutoff_year. If the publication is in the list of prev_pubs then it is skipped. 
    If the author doesn't have at least one matching affiliation then the publication is skipped. If the publication 
    was published before the cutoff_year then it is skipped. Each publication is then determined to have citations 
    for any of the grants in the author's grants.
    
    Args:
        prev_pubs (list): List of publications ids as strings to filter publications found on ORCID
        ORCID_key (str): string of the app key ORCID gives when you register the app with them
        ORCID_secret (str): string of the secret ORCID gives when you register the app with them
        authors_json_file (dict): keys are authors and values are author attributes. Matches authors JSON schema.
        verbose (bool): Determines whether errors are silenced or not.
        
    Returns:
        publication_dict (dict): keys are publication ids and values are a dictionary with publication attributes
    """
    
    api = orcid.PublicAPI(ORCID_key, ORCID_secret)
    search_token = api.get_search_token_from_orcid()
    
    publication_dict = {}
    prev_pubs_titles = [pub_attr["title"] for pub_attr in prev_pubs.values()]
    titles = []

    for author, authors_attributes in authors_json_file.items():
        
        if not "ORCID" in authors_attributes:
            continue
        
        summary = api.read_record_public(authors_attributes["ORCID"], 'works',
                                     search_token)
        
        for work in summary["group"]:
            title = None
            doi = None
            external_url = None
            publication_year = None
            publication_month = None
            publication_day = None
            pmid = None
            ## If the work is not a journal article then skip it.
            work_is_a_journal_article = True
            for work_summary in work["work-summary"]:
                
                if work_summary["type"] != "JOURNAL_ARTICLE":
                    work_is_a_journal_article = False
                    break
                
                work_before_relevant_year = False
                if work_summary["publication-date"]:
                    if not publication_year and work_summary["publication-date"]["year"]:
                        publication_year = int(work_summary["publication-date"]["year"]["value"])
                        
                    if not publication_month and work_summary["publication-date"]["month"]:
                        publication_month = int(work_summary["publication-date"]["month"]["value"])
                        
                    if not publication_day and work_summary["publication-date"]["day"]:
                        publication_day = int(work_summary["publication-date"]["day"]["value"])

                    if publication_year < authors_attributes["cutoff_year"]:
                        work_before_relevant_year = True
                        break
                
                
                if work_summary["title"] and not title:
                    title = work_summary["title"]["title"]["value"]
                
                if not doi:
                    for external_id in work_summary["external-ids"]["external-id"]:
                        if external_id["external-id-type"] == "doi":
                            doi = external_id["external-id-value"]
                            break
                        elif external_id["external-id-url"]:
                            external_url = external_id["external-id-url"]["value"]
                        elif external_id["external-id-type"] == "pmid":
                            pmid = external_id["external-id-value"]
                
                if title and doi and publication_year and publication_month and publication_day:
                    break
            
            if work_before_relevant_year or not work_is_a_journal_article:
                continue
                       
            if (not title and not doi) or (not doi and not external_url) or not publication_year:
                continue
            else:
                if doi:
                    pub_id = DOI_URL + doi
                elif external_url:
                    pub_id = external_url
                elif pmid:
                    pub_id = pmid
                else:
                    print("Warning: Could not find a DOI, URL, or PMID for a publication when searching ORCID. It will not be in the publications")
                    print("Title: " + title)
                    continue
                    
                if helper_functions.is_pub_in_publication_dict(pub_id, title, prev_pubs, prev_pubs_titles):
                    continue
                    
                
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
                    
                
                if not helper_functions.is_pub_in_publication_dict(pub_id, title, publication_dict, titles):
                    pub_dict["authors"] = [{"affiliation": authors_attributes["affiliations"],
                                            "firstname": authors_attributes["first_name"],
                                            "initials": None,
                                            "lastname": authors_attributes["last_name"],
                                            "author_id" : author}]
                    publication_dict[pub_id] = pub_dict
                    titles.append(title)
                elif pub_id in publication_dict:
                    author_ids = [pub_author["author_id"] for pub_author in publication_dict[pub_id]["authors"]]
                    if not author in author_ids:
                        publication_dict[pub_id]["authors"].append({"affiliation": authors_attributes["affiliations"],
                                                                     "firstname": authors_attributes["first_name"],
                                                                     "initials": None,
                                                                     "lastname": authors_attributes["last_name"],
                                                                     "author_id" : author})
                
        time.sleep(1)
        
    return publication_dict


            

def search_Google_Scholar_for_pubs(prev_pubs, authors_json_file, mailto_email, verbose):
    """Searhes Google Scholar for publications by each author.
    
    For each author in authors_json_file Google Scholar is queried for the publications. The list of publications is then filtered 
    by prev_pubs, affiliations, and cutoff_year. If the publication is in the list of prev_pubs then it is skipped. 
    If the author doesn't have at least one matching affiliation then the publication is skipped. If the publication 
    was published before the cutoff_year then it is skipped. Each publication is then determined to have citations 
    for any of the grants in the author's grants.
    
    Args:
        prev_pubs (list): List of publications ids as strings to filter publications found on Google Scholar
        authors_json_file (dict): keys are authors and values are author attributes. Matches authors JSON schema.
        mailto_email (str): used in the query to Crossref when trying to find DOIs for the articles
        verbose (bool): Determines whether errors are silenced or not.
        
    Returns:
        publication_dict (dict): keys are pulication ids and values are a dictionary with publication attributes
    """
    
    publication_dict = {}
    prev_pubs_titles = [pub_attr["title"] for pub_attr in prev_pubs.values()]
    titles = []
    for author, authors_attributes in authors_json_file.items():
        
        if not "scholar_id" in authors_attributes:
            continue
        
        try:
            queried_author = scholarly.scholarly.search_author_id(authors_attributes["scholar_id"])
        except:
            print("Error: The \"scholar_id\" for author " + author + " is probably incorrect, an error occured when trying to query Google Scholar.")    
            continue
        
        if not queried_author["scholar_id"] == authors_attributes["scholar_id"]:
            continue
        
        ## Note that fill modifies the passed dictionary directly, but this is easier to mock in unit tests.
        queried_author = scholarly.scholarly.fill(queried_author, sections=["publications"])
        
        for pub in queried_author["publications"]:
            
            ## Find the publication year and check that it is in range.
            if "pub_year" in pub["bib"]:
                publication_year = int(pub["bib"]["pub_year"])
            else:
                publication_year = None
        
            if not publication_year or publication_year < authors_attributes["cutoff_year"]:
                continue
            
            title = pub["bib"]["title"]
            
            ## Determine the pub_id
            doi = get_DOI_from_Crossref(title, mailto_email)
            if doi:
                pub_id = DOI_URL + doi
            else:
                pub = scholarly.scholarly.fill(pub)
                if "pub_url" in pub:
                    pub_id = pub["pub_url"]
                else:
                    print("Warning: Could not find a DOI, URL, or PMID for a publication when searching Google Scholar. It will not be in the publications.")
                    print("Title: " + title)
                    continue
            
            if helper_functions.is_pub_in_publication_dict(pub_id, title, prev_pubs, prev_pubs_titles):
                continue
        
            
            pub_dict = copy.deepcopy(PUBLICATION_TEMPLATE)
            if doi:
                pub_dict["doi"] = doi
            if title:
                pub_dict["title"] = title
            if publication_year:
                pub_dict["publication_date"]["year"] = publication_year
                
            
            if not helper_functions.is_pub_in_publication_dict(pub_id, title, publication_dict, titles):
                pub_dict["authors"] = [{"affiliation": authors_attributes["affiliations"],
                                        "firstname": authors_attributes["first_name"],
                                        "initials": None,
                                        "lastname": authors_attributes["last_name"],
                                        "author_id" : author}]
                publication_dict[pub_id] = pub_dict
                titles.append(title)
            elif pub_id in publication_dict:
                author_ids = [pub_author["author_id"] for pub_author in publication_dict[pub_id]["authors"]]
                if not author in author_ids:
                    publication_dict[pub_id]["authors"].append({"affiliation": authors_attributes["affiliations"],
                                             "firstname": authors_attributes["first_name"],
                                             "initials": None,
                                             "lastname": authors_attributes["last_name"],
                                             "author_id" : author})
                
        time.sleep(1)
            
    return publication_dict



## Leaving this function here because it might be useful someday, but the problem is that verifying DOI addresses is hard to do.
## Currently trying to visit DOIs programmatically usually results in an HTTP Forbidden error.
def scrape_url_for_DOI(url, verbose):
    """Searches url for DOI.
    
    Uses the regex "(?i).*doi:\s*([^\s]+\w).*" to look for a DOI on 
    the provided url. The DOI is visited to confirm it is a proper DOI.
    
    Args:
        url (str): url to search.
        verbose (bool): if True print HTTP errors.
        
    Returns:
        DOI (str): string of the DOI found on the webpage. Is empty string if DOI is not found.
    """
        
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=5)
        url_str = response.read().decode("utf-8")
        response.close()
                
    except urllib.error.HTTPError as e:
        if verbose:
            print(e)
            print(url)
            
    DOI = helper_functions.regex_group_return(helper_functions.regex_search_return(r"(?i)doi:\s*(<[^>]*>)?([^\s<]+)", url_str), 1)
    
    if DOI:
        ## TODO figure out how to visit DOI addresses without getting Forbidden HTTPError.
        if re.match(r".*http.*", DOI):
            try:
                req = urllib.request.Request(DOI, headers={"User-Agent": "Mozilla/5.0"})
                response = urllib.request.urlopen(req, timeout=5)
                response.close()
                        
            except urllib.error.HTTPError:
                return ""
            
            ## try to pull out the DOI from the url. If it doesn't work then empty string is returned.
            return helper_functions.regex_group_return(helper_functions.regex_match_return(r"https://doi.org/(.*)", DOI), 0)
        
        else:
            try:
                req = urllib.request.Request(DOI_URL + DOI, headers={"User-Agent": "Mozilla/5.0"})
                response = urllib.request.urlopen(req, timeout=5)
                response.close()
                        
            except urllib.error.HTTPError:
                return ""
            
            return DOI
        
    else:
        return ""
    
            

def get_DOI_from_Crossref(title, mailto_email):
    """Search title on Crossref and try to find a DOI for it.
    
    Args:
        title (str): string of the title of the journal article to search for.
        mailto_email (str): an email address needed to search Crossref more effectively.
        
    Returns:
        doi (str): Either None or the DOI of the article title. The DOI will not be a URL.
    """
    
    doi = None
    
    cr = habanero.Crossref(ua_string = "Academic Tracker (mailto:" + mailto_email + ")")
    
    results = cr.works(query_bibliographic = title, filter = {"type":"journal-article"})
    
    for work in results["message"]["items"]:
        
        if not "title" in work or not helper_functions.is_fuzzy_match_to_list(title, work["title"]):
            continue
            
        ## Look for DOI
        if "DOI" in work:
            doi = work["DOI"]
        
        ## Crossref should only have one result that matches the title, so if it got past the check at the top break.
        break
    
    return doi



def get_grants_from_Crossref(title, mailto_email, grants):
    """Search title on Crossref and try to find the grants associated with it.
    
    Only the grants in the grants parameter are searched for because trying to find 
    all grants associated with the article is too difficult.
    
    Args:
        title (str): string of the title of the journal article to search for.
        mailto_email (str): an email address needed to search Crossref more effectively.
        grants (list): a list of the grants to try and find for the article.
        
    Returns:
        found_grants (str): Either None or a list of grants found for the article.
    """
    
    found_grants = None
    
    cr = habanero.Crossref(ua_string = "Academic Tracker (mailto:" + mailto_email + ")")
    
    results = cr.works(query_bibliographic = title, filter = {"type":"journal-article"})
    
    for work in results["message"]["items"]:
        
        if not "title" in work or not helper_functions.is_fuzzy_match_to_list(title, work["title"]):
            continue
            
        if "funder" in work:
            ## the grant string could be in any value of the funder dict so look for it in each one.
            found_grants = {grant for funder in work["funder"] for value in funder.values() for grant in grants if grant in value}
            if found_grants:
                found_grants = list(found_grants)
            
        ## Crossref should only have one result that matches the title, so if it got past the check at the top break.
        break
    
    return found_grants



def search_Crossref_for_pubs(prev_pubs, authors_json_file, mailto_email, verbose):
    """Searhes Crossref for publications by each author.
    
    For each author in authors_json_file Crossref is queried for the publications. The list of publications is then filtered 
    by prev_pubs, affiliations, and cutoff_year. If the publication is in the list of prev_pubs then it is skipped. 
    If the author doesn't have at least one matching affiliation then the publication is skipped. If the publication 
    was published before the cutoff_year then it is skipped. Each publication is then determined to have citations 
    for any of the grants in the author's grants.
    
    Args:
        prev_pubs (list): List of publications ids as strings to filter publications found on Crossref
        authors_json_file (dict): keys are authors and values are author attributes. Matches authors JSON schema.
        mailto_email (str): used in the query to Crossref
        verbose (bool): Determines whether errors are silenced or not.
        
    Returns:
        publication_dict (dict): keys are pulication ids and values are a dictionary with publication attributes
    """
    
    cr = habanero.Crossref(ua_string = "Academic Tracker (mailto:" + mailto_email + ")")
    
    publication_dict = {}
    prev_pubs_titles = [pub_attr["title"] for pub_attr in prev_pubs.values()]
    titles = []
    for author, authors_attributes in authors_json_file.items():
        
        results = cr.works(query_author = authors_attributes["pubmed_name_search"], filter = {"type":"journal-article", "from-pub-date":str(authors_attributes["cutoff_year"])}, limit = 300)
        
        for work in results["message"]["items"]:
            
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
            
            
                
            if publication_year < authors_attributes["cutoff_year"]:
                continue
            
            if "title" in work:
                title = work["title"][0]
            else:
                continue
            
            author_list = helper_functions.match_authors_in_pub_Crossref(authors_json_file, work["author"])
            ## If the author_list is empty then there were no matching authors, continue.
            if not author_list:
                continue
            
            ## Change the author list to a form like PubMed's
            new_author_list = []
            for cr_author_dict in author_list:
                
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
            
            ## Look for DOI
            if "DOI" in work:
                doi = work["DOI"]
            else:
                doi = None
            
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
            
            
            
            if helper_functions.is_pub_in_publication_dict(pub_id, title, prev_pubs, prev_pubs_titles) or \
               helper_functions.is_pub_in_publication_dict(pub_id, title, publication_dict, titles):
                continue
            
            
            
            ## look for grants in results
            if "funder" in work:
                ## the grant string could be in any value of the funder dict so look for it in each one.
                found_grants = {grant for funder in work["funder"] for value in funder.values() for grant in authors_attributes["grants"] if grant in value}
                if found_grants:
                    found_grants = list(found_grants)
                else:
                    found_grants = None
            else:
                found_grants = None
                
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
            if found_grants:
                pub_dict["grants"] = found_grants
                
            pub_dict["authors"] = new_author_list
            pub_dict["title"] = title
            
            
            publication_dict[pub_id] = pub_dict
            titles.append(title)
            
        time.sleep(1)
            
            
    return publication_dict
        
                

##TODO look into adding expanded search to orcid, would need to upgrade to 3.0.
def search_ORCID_for_ids(ORCID_key, ORCID_secret, authors_json_file):
    """"""
    
    import requests
    SEARCH_VERSION = "/v3.0"
    def search_replace(self, query, method, start, rows, headers,
                endpoint):
        url = endpoint + SEARCH_VERSION + \
                "/expanded-search/?defType=" + method + "&q=" + query
        if start:
            url += "&start=%s" % start
        if rows:
            url += "&rows=%s" % rows

        response = requests.get(url, headers=headers,
                                timeout=self._timeout)
        response.raise_for_status()
        if self.do_store_raw_response:
            self.raw_response = response
        return response.json()
    
    orcid.PublicAPI._search = search_replace
    
    api = orcid.PublicAPI(ORCID_key, ORCID_secret)
    
    search_token = api.get_search_token_from_orcid()
    
    for author, author_attributes in authors_json_file.items():
        
        if "ORCID" in author_attributes:
            continue
        
        search_results = api.search(author_attributes["pubmed_name_search"], access_token=search_token)
        
        for result in search_results["expanded-result"]:
            if re.match(author_attributes["first_name"].lower() + ".*", result["given-names"]) and author_attributes["last_name"].lower() == result["family-names"]:
                
                if any([affiliation.lower() in institution.lower() for institution in result["institution-name"] for affiliation in author_attributes["affiliations"]]):
                    author_attributes["ORCID"] = result["orcid-id"]
                    break


    return authors_json_file



def search_Google_Scholar_for_ids(authors_json_file):
    """"""
    
    for author, author_attributes in authors_json_file.items():
        
        if "scholar_id" in author_attributes:
            continue
    
        search_query = scholarly.scholarly.search_author(author)
        
        for queried_author in search_query:
        
            if any([affiliation.lower() in queried_author["affiliation"].lower() for affiliation in author_attributes["affiliations"]]):
                author_attributes["scholar_id"] = queried_author["scholar_id"]
                break
            
    return authors_json_file





















        

## How to import from a full file path
#import importlib
#path_to_helper = 'C:/Users/Sparda/Desktop/Moseley Lab/Code/academic_tracker/academic_tracker/helper_functions.py'
#spec = importlib.util.spec_from_file_location("module.name", path_to_helper)
#foo = importlib.util.module_from_spec(spec)
#helper_functions = importlib.util.module_from_spec(spec)
#spec.loader.exec_module(helper_functions)
    

        
