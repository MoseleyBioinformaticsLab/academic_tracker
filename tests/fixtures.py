# -*- coding: utf-8 -*-

import pytest
import xml.etree.ElementTree as ET
import os
import pymed
from academic_tracker.helper_functions import modify_pub_dict_for_saving
from academic_tracker.fileio import load_json


@pytest.fixture
def authors_json_file():
    return load_json(os.path.join("testing_files", "authors.json"))

@pytest.fixture
def pub_with_no_matching_author():
    xml_path = os.path.join("testing_files", "no_author.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())


@pytest.fixture
def pub_with_matching_author():
    xml_path = os.path.join("testing_files", "has_author.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())


@pytest.fixture
def author_info():
    cutoff_year = 2019
    author_first_name = "Andrew"
    author_last_name = "Morris"
    author_affiliations = ["kentucky"]
    author_id = "Andrew Morris"
    
    return cutoff_year, author_first_name, author_last_name, author_affiliations, author_id

@pytest.fixture
def pub_with_grants():
    xml_path = os.path.join("testing_files", "has_pubmed_grants.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())

@pytest.fixture
def publication_dict(pub_with_grants, pub_with_matching_author):
    publication_dict = {}
    
    pub_dict = modify_pub_dict_for_saving(pub_with_grants)
    publication_dict["https://doi.org/" + pub_dict["doi"]] = pub_dict
    
    pub_dict = modify_pub_dict_for_saving(pub_with_matching_author)
    publication_dict["https://doi.org/" + pub_dict["doi"]] = pub_dict
    
    return publication_dict


@pytest.fixture
def pubs_by_author_dict():
    return {"Andrew Morris":{"34352431":set(), "33830777":set(["P42 ES007380"])}}

@pytest.fixture
def authors_dict():
    return {'Andrew Morris': {'email': 'a.j.morris@uky.edu',
                                  'first_name': 'Andrew',
                                  'last_name': 'Morris',
                                  'ORCID':'0000-0003-1910-4865',
                                  'scholar_id': '-j7fxnEAAAAJ',
                                  'pubmed_name_search': 'Andrew Morris',
                                  'affiliations': ['kentucky'],
                                  'cc_email': ["ptth222@uky.edu", "ptth222@gmail.com"],
                                  'cutoff_year': 2019,
                                  'email_subject': 'New PubMed Publications',
                                  'email_template': 'Hey <author_first_name>,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\n<total_pubs>\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
                                  'from_email': 'ptth222@uky.edu',
                                  'grants': ['P42ES007380', 'P42 ES007380']}}

@pytest.fixture
def email_messages():
    return {'creation_date': '2021-10-20 21:50',
             'emails': [{'body': 'Hey Andrew,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\nMottaleb MA, Ding QX, Pennell KG, Haynes EN, Morris AJ. 2021. Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry.. Journal of chromatography. A. 10.1016/j.chroma.2021.462426 PMID:34352431\n\nCited Grants:\nNone\n\n\nDeng P, Valentino T, Flythe MD, Moseley HNB, Leachman JR, Morris AJ, Hennig B. 2021. Untargeted Stable Isotope Probing of the Gut Microbiota Metabolome Using . Journal of proteome research. 10.1021/acs.jproteome.1c00124 PMID:33830777\n\nCited Grants:\nP42 ES007380\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
               'subject': 'New PubMed Publications',
               'from': 'ptth222@uky.edu',
               'to': 'a.j.morris@uky.edu',
               'cc': 'ptth222@uky.edu,ptth222@gmail.com',
               'author': 'Andrew Morris'}]}
        

@pytest.fixture
def passing_config():
    return {"project_descriptions": {
                "project 1":{
                  "affiliations": [
                    "kentucky"
                  ],
                  "cc_email": [],
                  "cutoff_year": 2019,
                  "email_subject": "New PubMed Publications",
                  "email_template": "Hey <author_first_name>,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\n<total_pubs>\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu",
                  "from_email": "ptth222@uky.edu",
                  "authors": ["Andrew Morris", "Hunter Moseley"],
                  "grants": [
                    "P42ES007380",
                    "P42 ES007380"
                  ]
                },
                "project 2":{
                  "affiliations": [
                    "kentucky"
                  ],
                  "cc_email": [],
                  "cutoff_year": 2019,
                  "email_subject": "New PubMed Publications",
                  "email_template": "These are the publications I was able to find on PubMed. Are any missing?\n\n<total_pubs>\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu",
                  "from_email": "ptth222@uky.edu",
                  "to_email": ["ptth222@uky.edu"],
                  "grants": [
                    "P42ES007380",
                    "P42 ES007380"
                  ]
                },
                "project 3":{
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
                },
            "ORCID_search":{
                    "ORCID_key":"asdf",
                    "ORCID_secret":"qwer"},
            "PubMed_search":{
                    "PubMed_email":"ptth222@uky.edu"},
            "Crossref_search":{
                    "mailto_email":"ptth222@uky.edu"}}
            

@pytest.fixture
def authors_by_project_dict():
    return {'project 1': {'Hunter Moseley': {'ORCID': '0000-0003-3995-5368',
           'affiliations': ['kentucky'],
           'cutoff_year': 2020,
           'email': 'hunter.moseley@gmail.com',
           'first_name': 'Hunter',
           'last_name': 'Moseley',
           'pubmed_name_search': 'Hunter Moseley',
           'scholar_id': 'ctE_FZMAAAAJ',
           'cc_email': [],
           'email_subject': 'New PubMed Publications',
           'email_template': 'Hey <author_first_name>,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\n<total_pubs>\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
           'from_email': 'ptth222@uky.edu',
           'authors': ['Andrew Morris', 'Hunter Moseley'],
           'grants': ['P42ES007380', 'P42 ES007380']}},
         'project 2': {'Hunter Moseley': {'ORCID': '0000-0003-3995-5368',
           'affiliations': ['kentucky'],
           'cutoff_year': 2020,
           'email': 'hunter.moseley@gmail.com',
           'first_name': 'Hunter',
           'last_name': 'Moseley',
           'pubmed_name_search': 'Hunter Moseley',
           'scholar_id': 'ctE_FZMAAAAJ',
           'cc_email': [],
           'email_subject': 'New PubMed Publications',
           'email_template': 'These are the publications I was able to find on PubMed. Are any missing?\n\n<total_pubs>\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
           'from_email': 'ptth222@uky.edu',
           'to_email': 'ptth222@uky.edu',
           'grants': ['P42ES007380', 'P42 ES007380']},
          'Isabel Escobar': {'ORCID': '0000-0001-9269-5927',
           'affiliations': ['kentucky'],
           'cutoff_year': 2020,
           'email': 'isabel.escobar@uky.edu',
           'first_name': 'Isabel',
           'last_name': 'Escobar',
           'pubmed_name_search': 'Isabel Escobar',
           'scholar_id': 'RfB5L8kAAAAJ',
           'cc_email': [],
           'email_subject': 'New PubMed Publications',
           'email_template': 'These are the publications I was able to find on PubMed. Are any missing?\n\n<total_pubs>\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
           'from_email': 'ptth222@uky.edu',
           'to_email': 'ptth222@uky.edu',
           'grants': ['P42ES007380', 'P42 ES007380']}},
         'project 3': {'Hunter Moseley': {'ORCID': '0000-0003-3995-5368',
           'affiliations': ['kentucky'],
           'cutoff_year': 2020,
           'email': 'hunter.moseley@gmail.com',
           'first_name': 'Hunter',
           'last_name': 'Moseley',
           'pubmed_name_search': 'Hunter Moseley',
           'scholar_id': 'ctE_FZMAAAAJ',
           'cc_email': [],
           'email_subject': 'New PubMed Publications',
           'email_template': 'These are the publications I was able to find on PubMed. Are any missing?\n\n<total_pubs>\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
           'from_email': 'ptth222@uky.edu',
           'grants': ['P42ES007380', 'P42 ES007380']},
          'Isabel Escobar': {'ORCID': '0000-0001-9269-5927',
           'affiliations': ['kentucky'],
           'cutoff_year': 2020,
           'email': 'isabel.escobar@uky.edu',
           'first_name': 'Isabel',
           'last_name': 'Escobar',
           'pubmed_name_search': 'Isabel Escobar',
           'scholar_id': 'RfB5L8kAAAAJ',
           'cc_email': [],
           'email_subject': 'New PubMed Publications',
           'email_template': 'These are the publications I was able to find on PubMed. Are any missing?\n\n<total_pubs>\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
           'from_email': 'ptth222@uky.edu',
           'grants': ['P42ES007380', 'P42 ES007380']}}}
        
        