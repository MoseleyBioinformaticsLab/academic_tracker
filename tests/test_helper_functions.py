# -*- coding: utf-8 -*-

import pytest
from academic_tracker.helper_functions import create_citation, replace_body_magic_words, replace_subject_magic_words, create_emails_dict, create_email_dict_for_no_PMCID_pubs
from fixtures import pub_with_no_matching_author, pub_with_grants, authors_dict, publication_dict, pubs_by_author_dict, pub_with_matching_author, email_messages


def test_create_citation():
    
    pub = {
            'abstract': "Following the publication of this article the authors noted that Torfi Sigurdsson's name was misspelled. Instead of Sigrudsson it should be Sigurdsson. The PDF and HTML versions of the paper have been modified accordingly.\xa0The authors would like to apologise for this error and the inconvenience this may have caused.",
             'authors': [
                     { 'affiliation': 'Department of Neurology, University Medical Center, Johannes Gutenberg-University, Mainz, Germany.',
                       'firstname': 'Carine',
                       'initials': 'C',
                       'lastname': 'Thalman'},],
             'conclusions': None,
             'copyrights': None,
             'doi': '10.1038/s41380-018-0320-1',
             'journal': 'Molecular psychiatry',
             'keywords': [],
             'methods': None,
             'publication_date': '2019-01-04',
             'pubmed_id': '30602735',
             'results': None,
             'title': 'Correction: Synaptic phospholipids as a new target for cortical hyperexcitability and E/I balance in psychiatric disorders.'}
             
             
    assert create_citation(pub) == 'Thalman C. 2019. Correction: Synaptic phospholipids as a new target for cortical hyperexcitability and E/I balance in psychiatric disorders.. Molecular psychiatry. 10.1038/s41380-018-0320-1 PMID:30602735'


                 
                 
def test_create_emails_dict_creates_successfully(pubs_by_author_dict, authors_dict, publication_dict, email_messages):
    function_messages = create_emails_dict(pubs_by_author_dict, authors_dict, publication_dict)
    
    del function_messages["creation_date"]
    del email_messages["creation_date"]
    
    assert email_messages == function_messages
    
    
@pytest.fixture
def publications_with_no_PMCID_list():
    return [{'DOI': '10.1016/j.chroma.2021.462426',
  'PMID': '34352431',
  'line': 'Mottaleb MA, Ding QX, Pennell KG, Haynes E, Morris AJ. 2021. Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry. Journal of Chromatography. A. 1653:5. doi:10.1016/j.chroma.2021.462426 PMID:34352431 ',
  'Grants': ['P30 ES026529']},
 {'DOI': '10.13023/jah.0201.06',
  'PMID': '',
  'line': 'Hoover AG, Koempel A, Christian WJ, Tumlin KI, Pennell KG. 2020. Appalachian environmental health literacy: Building knowledge and skills to protect health. Journal of Appalachian Health. 2:doi:10.13023/jah.0201.06 ',
  'Grants': []}]
    
@pytest.fixture
def passing_config():
    return {
              "affiliations": [
                "kentucky"
              ],
              "cc_email": [],
              "cutoff_year": 2019,
              "email_subject": "New PubMed Publications",
              "email_template": "These are the publications I was able to find on PubMed. Are any missing?\n\n<total_pubs>\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu",
              "from_email": "ptth222@uky.edu",
              "grants": [
                "P42ES007380",
                "P42 ES007380"
              ]
            }
    
@pytest.fixture
def no_PMCID_email_message():
    return {'creation_date': '2021-11-06 02:32',
 'emails': [{'body': 'These are the publications I was able to find on PubMed. Are any missing?\n\nMottaleb MA, Ding QX, Pennell KG, Haynes E, Morris AJ. 2021. Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry. Journal of Chromatography. A. 1653:5. doi:10.1016/j.chroma.2021.462426 PMID:34352431 \n\nPMID: 34352431\n\nCited Grants:\nP30 ES026529\n\n\nHoover AG, Koempel A, Christian WJ, Tumlin KI, Pennell KG. 2020. Appalachian environmental health literacy: Building knowledge and skills to protect health. Journal of Appalachian Health. 2:doi:10.13023/jah.0201.06 \n\nPMID: None\n\nCited Grants:\nNone\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
   'subject': 'New PubMed Publications',
   'from': 'ptth222@uky.edu',
   'to': 'ptth222@uky.edu',
   'cc': ''}]}
        

def test_create_email_dict_for_no_PMCID_pubs(publications_with_no_PMCID_list, passing_config, no_PMCID_email_message):
    email_message = create_email_dict_for_no_PMCID_pubs(publications_with_no_PMCID_list, passing_config, "ptth222@uky.edu")
    
    del email_message["creation_date"]
    del no_PMCID_email_message["creation_date"]
    
    assert email_message == no_PMCID_email_message
    
    

def test_replace_body_magic_words(pubs_by_author_dict, authors_dict, publication_dict):
    
    assert replace_body_magic_words(pubs_by_author_dict["Andrew Morris"], authors_dict["Andrew Morris"], publication_dict) == 'Hey Andrew,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\nMottaleb MA, Ding QX, Pennell KG, Haynes EN, Morris AJ. 2021. Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry.. Journal of chromatography. A. 10.1016/j.chroma.2021.462426 PMID:34352431\n\nCited Grants:\nNone\n\n\nDeng P, Valentino T, Flythe MD, Moseley HNB, Leachman JR, Morris AJ, Hennig B. 2021. Untargeted Stable Isotope Probing of the Gut Microbiota Metabolome Using . Journal of proteome research. 10.1021/acs.jproteome.1c00124 PMID:33830777\n\nCited Grants:\nP42 ES007380\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu'


def test_replace_subject_magic_words(authors_dict):
    
    author_attributes = authors_dict["Andrew Morris"]
    author_attributes["email_subject"] = "Test replacement <author_first_name> <author_last_name>"
    
    assert replace_subject_magic_words(author_attributes) == "Test replacement Andrew Morris"




