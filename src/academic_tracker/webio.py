# -*- coding: utf-8 -*-
"""
Webio
~~~~~

General functions that interface with the internet.
"""

import urllib.request
import urllib.error
import email.message
import subprocess
import io
import re
import os
import shutil

import orcid
import scholarly
import habanero
import bs4
import json
import requests

from . import helper_functions


TOOL = "Academic Tracker"
DOI_URL = "https://doi.org/"

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
        "grants": [],
        "PMCID": None,
        "queried_sources": [],
        "references": []
   }



##TODO look into adding expanded search to orcid, would need to upgrade to 3.0.
def search_ORCID_for_ids(ORCID_key, ORCID_secret, authors_json):
    """Query ORCID with author names and get ORCID IDs.
    
    If an author already has an ORCID, or doesn't have affiliations they are skipped.
    
    Args:
        ORCID_key (str): key assigned to your registered application from ORCID.
        ORCID_secret (str): secret given to you by ORCID.
        authors_json (dict): JSON matching the Authors section of the Configuration file.
        
    Returns:
        authors_json (dict): the authors_json modified with any ORCID IDs found.
    """
    
    ## This is a workaround to get the expanded search functionality that the orcid package doesn't currently have.
    SEARCH_VERSION = "/v3.0"
    def search_replace(self, query, method, start, rows, headers, endpoint):
        url = endpoint + SEARCH_VERSION + "/expanded-search/?defType=" + method + "&q=" + query
        if start:
            url += "&start=%s" % start
        if rows:
            url += "&rows=%s" % rows

        response = requests.get(url, headers=headers, timeout=self._timeout)
        response.raise_for_status()
        
        if self.do_store_raw_response:
            self.raw_response = response
        return response.json()
    
    orcid.PublicAPI._search = search_replace
    
    api = orcid.PublicAPI(ORCID_key, ORCID_secret)
    
    search_token = api.get_search_token_from_orcid()
    
    for author, author_attributes in authors_json.items():
        
        if ("ORCID" in author_attributes and author_attributes["ORCID"]) or not "affiliations" in author_attributes:
            continue
        search_results = api.search(author_attributes["pubmed_name_search"], access_token=search_token)
        
        for result in search_results["expanded-result"]:
            if re.match(author_attributes["first_name"].lower() + ".*", result["given-names"].lower()) and author_attributes["last_name"].lower() == result["family-names"].lower():
                
                if any([affiliation.lower() in institution.lower() for institution in result["institution-name"] for affiliation in author_attributes["affiliations"]]):
                    authors_json[author]["ORCID"] = result["orcid-id"]
                    break


    return authors_json



def search_Google_Scholar_for_ids(authors_json):
    """Query Google Scholar with author names and get Scholar IDs.
    
    If an author already has a scholar_id, or doesn't have affiliations they are skipped.
    
    Args:
        authors_json (dict): JSON matching the Authors section of the Configuration file.
        
    Returns:
        authors_json (dict): the authors_json modified with any ORCID IDs found.
    """
    
    for author, author_attributes in authors_json.items():
        
        if ("scholar_id" in author_attributes and author_attributes["scholar_id"]) or not "affiliations" in author_attributes:
            continue
    
        search_query = scholarly.scholarly.search_author(author_attributes["pubmed_name_search"])
        
        for queried_author in search_query:
            name = queried_author["name"].split(" ")
            first_name = name[0].lower()
            last_name = name[-1].lower()
            if author_attributes["first_name"].lower() == first_name and author_attributes["last_name"].lower() == last_name:
        
                if any([affiliation.lower() in queried_author["affiliation"].lower() for affiliation in author_attributes["affiliations"]]):
                    authors_json[author]["scholar_id"] = queried_author["scholar_id"]
                    break
            
    return authors_json


            

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
    
    try:
        results = cr.works(query_bibliographic = title, filter = {"type":"journal-article"})
    except:
        helper_functions.vprint("Warning: There was an error querying Crossref to get the DOI for the publication titled: " + title)
        return None
    
    for work in results["message"]["items"]:
        
        if not "title" in work or not helper_functions.is_fuzzy_match_to_list(title, work["title"]):
            continue
            
        ## Look for DOI
        if "DOI" in work:
            doi = work["DOI"].lower()
        
        ## Crossref should only have one result that matches the title, so if it got past the check at the top break.
        break
    
    return doi




def get_url_contents_as_str(url):
    """Query the url and return it's contents as a string.
    
    Args:
        url (str): the URL to query.
        
    Returns:
        (str): Either the website as a string or None if an error occurred.
    """
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=5)
        url_str = response.read().decode("utf-8")
        response.close()
        return url_str
                
    except urllib.error.HTTPError as e:
        helper_functions.vprint(e, verbosity=1)
        helper_functions.vprint(url, verbosity=1)
        
        return None
    
    

def clean_tags_from_url(url):
    """Remove tags from webpage.
    
    Remove tags from a webpage so it looks more like what a user would see in a 
    browser.
    
    Args:
        url (str): the URL to query.
        
    Returns:
        clean_url (str): webpage contents cleaned of tags.    
    """
    
    url_str = get_url_contents_as_str(url)
    if not url_str:
        return None
    
    ## All of the python libraries return the html with newlines in seemingly 
    ## arbitrary locations, so remove them and add in some for tags that make sense.
    clean_url = url_str.replace("\n", "")
    clean_url = clean_url.replace("<br>", "\n")
    clean_url = clean_url.replace("</div>", "</div>\n")
    clean_url = clean_url.replace("</p>", "</p>\n")
    clean_url = bs4.BeautifulSoup(clean_url, "lxml").text
#    clean_url = lxml.html.fromstring(url_str).text_content()
    
    return clean_url



def send_emails(email_messages):
    """Uses sendmail to send email_messages to authors.
    
    Only works on systems with sendmail installed. 
    
    Args:
        email_messages (dict): keys are author names and values are the message
    """
    if not shutil.which("sendmail"):
        helper_functions.vprint("Warning: sendmail was not found in PATH, so no emails were sent.")
        return
    
    # build and send each message by looping over the email_messages dict
    for email_parts in email_messages["emails"]:
        msg = email.message.EmailMessage()
        msg["Subject"] = email_parts["subject"]
        msg["From"] = email_parts["from"]
        msg["To"] = email_parts["to"]
        msg["Cc"] = email_parts["cc"]
        msg.set_content(email_parts["body"])
        
        if os.path.exists(email_parts["attachment"]):
            with open(email_parts["attachment"], 'rb') as content_file:
                content = content_file.read()
                
            msg.add_attachment(content, maintype="application", subtype="vnd.ms-excel", filename=email_parts["attachment_filename"])
        else:
            msg.add_attachment(email_parts["attachment"], filename=email_parts["attachment_filename"])
        
        subprocess.run(["sendmail", "-t", "-oi"], input=msg.as_bytes())




###############
## Unused Functions
###############
        
# def get_grants_from_Crossref(title, mailto_email, grants):
#     """Search title on Crossref and try to find the grants associated with it.
    
#     Only the grants in the grants parameter are searched for because trying to find 
#     all grants associated with the article is too difficult.
    
#     Args:
#         title (str): string of the title of the journal article to search for.
#         mailto_email (str): an email address needed to search Crossref more effectively.
#         grants (list): a list of the grants to try and find for the article.
        
#     Returns:
#         found_grants (str): Either None or a list of grants found for the article.
#     """
    
#     found_grants = None
    
#     cr = habanero.Crossref(ua_string = "Academic Tracker (mailto:" + mailto_email + ")")
    
#     results = cr.works(query_bibliographic = title, filter = {"type":"journal-article"})
    
#     for work in results["message"]["items"]:
        
#         if not "title" in work or not helper_functions.is_fuzzy_match_to_list(title, work["title"]):
#             continue
            
#         if "funder" in work:
#             ## the grant string could be in any value of the funder dict so look for it in each one.
#             found_grants = {grant for funder in work["funder"] for value in funder.values() for grant in grants if grant in value}
#             if found_grants:
#                 found_grants = list(found_grants)
            
#         ## Crossref should only have one result that matches the title, so if it got past the check at the top break.
#         break
    
#     return found_grants



# def get_redirect_url_from_doi(doi):
#     """"""
    
#     doi = doi.lower()
    
#     if re.match(r".*http.*", doi):
#         match = helper_functions.regex_match_return(r".*doi.org/(.*)", doi)
#         if match:
#             url = DOI_URL + "api/handles/" + match[0]
#         else:
#             return ""
#     else:
#         url = DOI_URL + "api/handles/" + doi
        
#     try:
#         req = urllib.request.Request(url)
#         response = urllib.request.urlopen(req)
#         json_response = json.loads(response.read())
#         response.close()
                
#     except urllib.error.HTTPError:
#         helper_functions.vprint("Error trying to resolve DOI: " + doi, verbosity=1)
#         return ""
        
#     for value in json_response["values"]:
#         if value["type"] == "URL":
#             return value["data"]["value"]
        
#     return ""



# def scrape_url_for_DOI(url):
#     """Searches url for DOI.
    
#     Uses the regex "(?i).*doi:\s*([^\s]+\w).*" to look for a DOI on 
#     the provided url. The DOI is visited to confirm it is a proper DOI.
    
#     Args:
#         url (str): url to search.
        
#     Returns:
#         DOI (str): string of the DOI found on the webpage. Is empty string if DOI is not found.
#     """
        
#     url_str = get_url_contents_as_str(url)
#     if not url_str:
#         return ""
            
#     doi = helper_functions.regex_group_return(helper_functions.regex_search_return(r"(?i)doi:\s*(<[^>]*>)?([^\s<]+)", url_str), 1)
    
#     if doi:
        
#         url = get_redirect_url_from_doi(doi)
#         return doi if url else ""
        
#     else:
#         return ""
    


# def check_doi_for_grants(doi, grants):
#     """Searches DOI webpage for grants.
    
#     Concatenates "https://doi.org/" with the doi, visits the 
#     page and looks for the given grants on that page.
    
#     Args:
#         doi (str): DOI for the publication.
#         grants (list): list of str for each grant to look for.
        
#     Returns:
#         found_grants (list): list of str with each grant that was found on the page.
#     """
    
#     url = get_redirect_url_from_doi(doi)
#     if not url:
#         return set()
    
#     url_str = get_url_contents_as_str(url)
#     if not url_str:
#         return set()
        
#     return { grant for grant in grants if grant in url_str }
    



# def download_pdf(pdf_url):
#     """
#     """
#     ## test url https://realpython.com/python-tricks-sample-pdf
#     try:
#         req = urllib.request.Request(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
#         response = urllib.request.urlopen(req)
#         pdf_bytes = io.BytesIO(response.read())
#         response.close()
                
#     except urllib.error.HTTPError as e:
#         helper_functions.vprint(e, verbosity=1)
#         helper_functions.vprint(pdf_url, verbosity=1)
        
#         return None
            
#     return pdf_bytes


    