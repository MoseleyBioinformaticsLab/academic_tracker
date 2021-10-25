# -*- coding: utf-8 -*-
"""
This module contains the functions that interface with the internet.
"""

from collections import OrderedDict
from urllib.request import urlopen
from urllib.error import HTTPError
from os.path import join
from time import sleep
from pymed import PubMed
from email.message import EmailMessage
import re
from datetime import datetime
import subprocess
from .helper_functions import create_citation



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
    pubmed = PubMed(tool="Publication_Tracker", email=from_email)
    
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
                pubs_by_author_dict[author][pub_id] | check_pubmed_for_grants(pub_id, author_attributes["grants"])
                ## For now not going to check the DOI for grants.
#                if author_attributes["grants"] - pubs_by_author_dict[author][pub_id]:
#                    pubs_by_author_dict[author][pub_id] | check_doi_for_grants(pub_dict["doi"], author_attributes["grants"], verbose)
                    
                    
            
        # don't piss off NCBI
        sleep(1)
        

    publication_dict = OrderedDict(sorted(publication_dict.items(), key=lambda x: x[1]["publication_date"], reverse=True))
    
    return publication_dict, pubs_by_author_dict







def create_emails_dict(pubs_by_author_dict, authors_dict, publication_dict):
    """Create emails for each author.
    
    For each author in pubs_by_author create an email with publication citations. 
    Information in authors_dict is used to get information about the author, and 
    publication_dict is used to get information about publications. 
    
    Args:
        pubs_by_author (dict): keys are author_ids that match keys in authors_dict, values are a set of pubmed_ids that match keys in publication_dict.
        authors_dict (dict): keys and values match the authors JSON file.
        publication_dict (dict): keys and values match the publications JSON file.
        
    Returns:
        email_messages (dict): keys and values match the email JSON file.
    
    """
    
    # dict for email messages.
    email_messages = {"creation_date" : str(datetime.now())[0:16], "emails" : []}
    
    for author in pubs_by_author_dict:
        pubs_string = ""
        for pub_id in pubs_by_author_dict[author]:
            pubs_string += create_citation(publication_dict[pub_id]) + "\n\n" + "Cited Grants:\n"
            
            for grant_id in pubs_by_author_dict[author][pub_id]:
                pubs_string += grant_id
                    
            else:
                pubs_string += "None"
                
            pubs_string += "\n\n\n"
            
       
        body = authors_dict[author]["email_template"]
        body = body.replace("<total_pubs>", pubs_string)
        body = body.replace("<author_first_name>", authors_dict[author]["first_name"])
        body = body.replace("<author_last_name>", authors_dict[author]["last_name"])
        
        subject = authors_dict[author]["email_subject"]
        subject = subject.replace("<author_first_name>", authors_dict[author]["first_name"])
        subject = subject.replace("<author_last_name>", authors_dict[author]["last_name"])
        
        
        
        cc_string = ""
        for email in authors_dict[author]["cc_email"]:
            cc_string += email + ","
        email_messages["emails"].append({"body": body, "subject": subject, "from": authors_dict[author]["from_email"], "to": authors_dict[author]["email"], "cc":cc_string, "author":author})
        
    
    return email_messages







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
    
    response = urlopen(join(pub_med_url, pub_id))
    url_str = response.read().decode("utf-8")
    response.close()
    
    found_grants = set()
    for grant in grants:
        if grant in url_str:
            found_grants.add(grant)
            
    return found_grants





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
        response = urlopen(join(doi_url, doi), timeout=5)
        url_str = response.read().decode("utf-8")
        response.close()
                
    except HTTPError as e:
        if verbose:
            print(e)
            print(join(doi_url, doi))
            
        return set()
    
    
    found_grants = set()
    for grant in grants:
        if grant in url_str:
            found_grants.add(grant)
                
    return found_grants






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
        pub_dict = pub.toDict()
            
        
        del pub_dict["xml"]
        pub_dict["publication_date"] = str(pub_dict["publication_date"])
        
        
        return pub_dict
    
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
    
    # build and send each message by looping over the email_messages dict
    for email_parts in email_messages["emails"]:
        msg = EmailMessage()
        msg["Subject"] = email_parts["subject"]
        msg["From"] = email_parts["from"]
        msg["To"] = email_parts["to"]
        msg["Cc"] = email_parts["cc"]
        msg.set_content(email_parts["body"])
        
        sendmail_location = "/usr/sbin/sendmail"
        subprocess.run([sendmail_location, "-t", "-oi"], input=msg.as_bytes())
