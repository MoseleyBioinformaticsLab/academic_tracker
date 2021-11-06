# -*- coding: utf-8 -*-
"""
This module contains the functions that interface with the internet.
"""

import collections
import urllib.request
import urllib.error
import os.path
import time
import pymed
import email.message
import re
import subprocess
import io
from . import helper_functions

## Some helpful code to get the xml back as text. import xml.etree.ElementTree as ET    ET.tostring(Element)

def build_pub_dict_from_PMID(PMID_list, from_email):
    """Query PubMed for each PMID and build a dictionary of the returned data.
    
    Args:
        PMID_list (list): A list of PMIDs as strings.
        from_email (str): An email address to use when querying PubMed.
        
    Returns:
        publication_dict (dict): keys are pulication ids and values are a dictionary with publication attributes.
    """
    
    pubmed = pymed.PubMed(tool="Publication_Tracker", email=from_email)
    
    publication_dict = dict()
    
    for PMID in PMID_list:
        
        publications = pubmed.query(PMID, max_results=10)
        
        for pub in publications:
            
            pub_id = pub.pubmed_id.split("\n")[0]
            if pub_id == PMID:
                publication_dict[pub_id] = helper_functions.modify_pub_dict_for_saving(pub)
                break
                
        time.sleep(1)
        

    publication_dict = collections.OrderedDict(sorted(publication_dict.items(), key=lambda x: x[1]["publication_date"], reverse=True))
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
    
    pubmed = pymed.PubMed(tool="Publication_Tracker", email=from_email)
    
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


                



def request_pubs_from_pubmed(prev_pubs, authors_dict, from_email, verbose):
    """Searhes PubMed for publications by each author.
    
    For each author in authors_dict PubMed is queried for the publications. The list of publications is then filtered 
    by prev_pubs, affiliations, and cutoff_year. If the publication is in the list of prev_pubs then it is skipped. 
    If the author doesn't have at least one matching affiliation then the publication is skipped. If the publication 
    was published before the cutoff_year then it is skipped. Each publication is then determined to have citations 
    for any of the grants in the author's grants.
    
    Args:
        prev_pubs (list): List of publications ids as strings to filter publications found on PubMed
        authors_dict (dict): keys are author names and values should be a dict with attributes, but only the keys are used
        from_email (str): used in the query to PubMed
        verbose (bool): Determines whether errors are silenced or not.
        
    Returns:
        publication_dict (dict): keys are pulication ids and values are a dictionary with publication attributes
        pubs_by_author_dict (dict): keys are author and values are a dict of publication ids with a set of grants cited for them
    """
       
    # initiate PubMed API
    pubmed = pymed.PubMed(tool="Publication_Tracker", email=from_email)
    
    publication_dict = dict()
    
    # key is author and value is a dict of publication ids with a set of grants cited for them. {"author":{"pub_id":("grant")}}
    pubs_by_author_dict = {}
    

    ########################
    # loop through list of authors and request a list of their publications
    ########################
    for author, author_attributes in authors_dict.items():
        
        ## TODO add options to query other sources such as ORCID using ORCID.
        
        publications = pubmed.query(author_attributes["pubmed_name_search"], max_results=500)
        
        ## Unpacking pub from publications appears to be the slowest part of the code.
        ## publications is an iterator that is broken up into batches and there are noticeable slow downs each time a new batch is fetched.
        for pub in publications:
            
            
            pub_dict = is_relevant_publication(pub, 
                                               author_attributes["cutoff_year"], 
                                               author_attributes["first_name"], 
                                               author_attributes["last_name"], 
                                               author_attributes["affiliations"], 
                                               author, prev_pubs)
            
            if pub_dict:
                pub_id = pub_dict["pubmed_id"].split("\n")[0]
            
                # add publications to the publication_dict if not there, else update the authors attribute so the other author has thier id added.
                if not pub_id in publication_dict.keys():
                    publication_dict[pub_id] = pub_dict
                else:
                    publication_dict[pub_id]["authors"][0].update(pub_dict["authors"][0])
                    
                
                
                ## Add publication to dict under the author.
                if author not in pubs_by_author_dict:
                    pubs_by_author_dict[author] = {pub_id:set()}
                else:
                    pubs_by_author_dict[author][pub_id] = set()
                
                
                ## Look for each grant_id and if found add it to dict.
                ## TODO look for grants in DOI if not on PubMed, and in pdf. Full text link might work as well. clicking that goes to full text. There is not a direct pdf link on pubmed page.
                ## Simply do the union of the sets to add grants to the pubs_by_author_dict. Do a difference of sets to see if they were all found.
                ## Should we keep looking after finding at least one grant? Will there be multiple grants cited?
#                [grant.text for grant in pub.xml.findall(".//GrantID")]
                pubs_by_author_dict[author][pub_id] | check_pubmed_for_grants(pub_id, author_attributes["grants"])
                ## For now not going to check the DOI for grants.
#                if author_attributes["grants"] - pubs_by_author_dict[author][pub_id]:
#                    pubs_by_author_dict[author][pub_id] | check_doi_for_grants(pub_dict["doi"], author_attributes["grants"], verbose)
                    
            
        # don't piss off NCBI
        time.sleep(1)
        

    publication_dict = collections.OrderedDict(sorted(publication_dict.items(), key=lambda x: x[1]["publication_date"], reverse=True))
    
    return publication_dict, pubs_by_author_dict







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





def is_relevant_publication(pub, cutoff_year, author_first_name, author_last_name, author_affiliations, author_id, prev_pubs):
    """Determine if a publication is what we are looking for.
    
    Determines if the pub is what we are looking for. If the pub is before the cutoff_year, 
    is in prev_pubs, or can't match an author to the author we are looking for then 
    return an empty dict. Otherwise return a dictionary with the publication attributes.
    
    Args:
        pub (object): publication queried from PubMed.
        cutoff_year (int): year before which to ignore publications.
        author_first_name (str): author's first name to match in the dict of authors for the pub
        author_last_name (str): author's last name to match in the dict of authors for the pub
        author_affiliations (list): author's affiliations to match in the dict of authors for the pub
        author_id (str): unique_id for the author to add to the dict of authors for the pub
        prev_pubs (dict): dict of previous pubs to match the PubMed ID to in order to skip the pub
        
    Returns:
        pub_dict (dict): dict matching a single entry in the publications JSON file
    """
    
    ## Setup for all the checks to see if we skip the publication.
    pub_id = pub.pubmed_id.split("\n")[0]
    publication_date = int(str(pub.publication_date)[:4])
    
    ## if the publication id is in the list of previously found ones or the publication date is before the curoff year then skip.
    ## TODO check and see if prev_pub now has grant citation if it didn't before. Add key to publication_dict to keep track.
    if pub_id in prev_pubs or publication_date < cutoff_year:
        return {}
    
    
    ## pub.authors are dictionaries with lastname, firstname, initials, and affiliation. firstname can have initials at the end ex "Andrew P"
    publication_has_affiliated_author = False
    for author_items in pub.authors:
        
        ## Match the author's first and last name and then match affiliations.
        ## The first name is matched with an additional .* to try and allow for the addition of initials, but this could cause bad matches. 
        ## For example the name Hu will match Hubert. Counting on the last name to reduce errors.
        ## Note that the PubMed query will return publications where the author is just a collaborater, so not finding a match in the authors isn't uncommon.
        if re.match(author_first_name + ".*", str(author_items.get("firstname"))) and author_last_name == str(author_items.get("lastname")):
            ## affiliations are sets of strings so the intersection should have at least 1 string for a match.
            if len(set(author_affiliations).intersection(set(re.findall(r"[\w]+", str(author_items.get("affiliation")).lower())))) > 0:
                publication_has_affiliated_author = True
                author_items["author_id"] = author_id
                break
    
    
    ## If publication has the author we are looking for then add it to the publication_dict and look for grants.
    if publication_has_affiliated_author:
        return helper_functions.modify_pub_dict_for_saving(pub)
    
    else:
        return {}
    






def send_emails(email_messages):
    """Uses sendmail to send email_messages to authors.
    
    Only works on systems with sendmail installed. Pulls the authors' email 
    from the authors_dict and sends the corresponding email in email_messages
    to the author. Every email will have the cc_emails cc'd.
    
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
