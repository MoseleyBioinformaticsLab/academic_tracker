# -*- coding: utf-8 -*-

import pytest
import xml.etree.ElementTree as ET
import os
import pymed
from academic_tracker.helper_functions import create_pub_dict_for_saving_PubMed
from academic_tracker.fileio import load_json
from academic_tracker import webio

DOI_URL = webio.DOI_URL


@pytest.fixture
def authors_json_file():
    return load_json(os.path.join("tests", "testing_files", "authors.json"))

@pytest.fixture
def pub_with_no_matching_author():
    xml_path = os.path.join("tests", "testing_files", "no_author.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())


@pytest.fixture
def pub_with_matching_author():
    xml_path = os.path.join("tests", "testing_files", "has_author.xml")
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
    xml_path = os.path.join("tests", "testing_files", "has_pubmed_grants.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())

@pytest.fixture
def publication_dict(pub_with_grants, pub_with_matching_author):
    publication_dict = {}
    
    _, pub_dict = create_pub_dict_for_saving_PubMed(pub_with_grants)
    publication_dict[DOI_URL + pub_dict["doi"]] = pub_dict
    
    _, pub_dict = create_pub_dict_for_saving_PubMed(pub_with_matching_author)
    publication_dict[DOI_URL + pub_dict["doi"]] = pub_dict
    
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
                                  'cutoff_year': 2019,
                                  'grants': ['P42ES007380', 'P42 ES007380']}}

@pytest.fixture
def email_messages():
    return {'creation_date': '2021-10-20 21:50',
             'emails': [{'body': 'Hey Andrew,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\nMottaleb MA, Ding QX, Pennell KG, Haynes EN, Morris AJ. 2021. Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry.. Journal of chromatography. A. 10.1016/j.chroma.2021.462426 PMID:34352431\n\nCited Grants:\nNone\n\n\nDeng P, Valentino T, Flythe MD, Moseley HNB, Leachman JR, Morris AJ, Hennig B. 2021. Untargeted Stable Isotope Probing of the Gut Microbiota Metabolome Using . Journal of proteome research. 10.1021/acs.jproteome.1c00124 PMID:33830777\n\nCited Grants:\nP42 ES007380\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
               'subject': 'New PubMed Publications',
               'from': 'ptth222@uky.edu',
               'to': 'a.j.morris@uky.edu',
               'cc': 'ptth222@uky.edu,ptth222@gmail.com',
               "attachment": "attachment content",
               "attachment_filename": "attachment_name.txt",
               'author': 'Andrew Morris'}]}
        

@pytest.fixture
def passing_config():
    return {"project_descriptions": {
                "project 1":{
                  "affiliations": [
                    "kentucky"
                  ],
                  "cutoff_year": 2019,
                  "project_report":{
                          "email_subject": "New PubMed Publications",
                          "email_body": "Attached is the report for publications found.\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu",
                          "template": "Hey <author_first>,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\n<author_loop><pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>",
                          "from_email": "ptth222@uky.edu",
                          "cc_email": [],},
                  "collaborator_report":{},
                  "authors": ["Andrew Morris", "Hunter Moseley", "Isabel Escobar"],
                  "grants": [
                    "P42ES007380",
                    "P42 ES007380"
                  ]
                },
                "project 2":{
                  "affiliations": [
                    "kentucky"
                  ],
                  "cutoff_year": 2019,
                  "project_report":{
                          "email_subject": "New PubMed Publications",
                          "email_body": "Attached is the report for publications found.\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu",
                          "template": "<author_loop><pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>",
                          "from_email": "ptth222@uky.edu",
                          "cc_email": [],
                          "to_email": ["ptth222@uky.edu"],},
                  "grants": [
                    "P42ES007380",
                    "P42 ES007380"
                  ]
                },
                "project 3":{
                  "affiliations": [
                    "kentucky"
                  ],
                  "cutoff_year": 2018,
                  "project_report":{
                          "email_subject": "New PubMed Publications",
                          "email_body": "Attached is the report for publications found.\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu",
                          "template": "<author_loop><pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>",
                          "from_email": "ptth222@uky.edu",
                          "cc_email": [],
                          "to_email": ["ptth222@uky.edu"],},
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
                    "mailto_email":"ptth222@uky.edu"},
            "summary_report":{
                    "email_subject": "New PubMed Publications",
                    "email_body": "Attached is the report for publications found.\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu",
                    "template": "<author_loop><pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>",
                    "from_email": "ptth222@uky.edu",
                    "cc_email": [],
                    "to_email": ["ptth222@uky.edu"],},
            "Authors": {
                    "Andrew Morris": {
                          "ORCID": "0000-0003-1910-4865",
                          "affiliations": [
                            "kentucky"
                          ],
                          "cutoff_year": 2020,
                          "email": "a.j.morris@uky.edu",
                          "first_name": "Andrew",
                          "last_name": "Morris",
                          "pubmed_name_search": "Andrew Morris",
                          "scholar_id": "-j7fxnEAAAAJ"},
                    "Hunter Moseley": {
                          "ORCID": "0000-0003-3995-5368",
                          "affiliations": [
                            "kentucky"
                          ],
                          "cutoff_year": 2020,
                          "email": "hunter.moseley@gmail.com",
                          "first_name": "Hunter",
                          "last_name": "Moseley",
                          "pubmed_name_search": "Hunter Moseley",
                          "scholar_id": "ctE_FZMAAAAJ"},},
            }
            

@pytest.fixture
def authors_by_project_dict():
    return {'project 1': {
              'Andrew Morris': {'ORCID': '0000-0003-1910-4865',
                   'affiliations': ['kentucky'],
                   'cutoff_year': 2020,
                   'email': 'a.j.morris@uky.edu',
                   'first_name': 'Andrew',
                   'last_name': 'Morris',
                   'pubmed_name_search': 'Andrew Morris',
                   'scholar_id': '-j7fxnEAAAAJ',
                   'project_report': {'email_subject': 'New PubMed Publications',
                    'email_body': 'Attached is the report for publications found.\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
                    'template': 'Hey <author_first>,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\n<author_loop><pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>',
                    'from_email': 'ptth222@uky.edu',
                    'cc_email': []},
                   'collaborator_report': {},
                   'authors': ['Andrew Morris', 'Hunter Moseley', 'Isabel Escobar'],
                   'grants': ['P42ES007380', 'P42 ES007380']},
              'Hunter Moseley': {'ORCID': '0000-0003-3995-5368',
                   'affiliations': ['kentucky'],
                   'cutoff_year': 2020,
                   'email': 'hunter.moseley@gmail.com',
                   'first_name': 'Hunter',
                   'last_name': 'Moseley',
                   'pubmed_name_search': 'Hunter Moseley',
                   'scholar_id': 'ctE_FZMAAAAJ',
                   'project_report': {'email_subject': 'New PubMed Publications',
                    'email_body': 'Attached is the report for publications found.\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
                    'template': 'Hey <author_first>,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\n<author_loop><pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>',
                    'from_email': 'ptth222@uky.edu',
                    'cc_email': []},
                   'collaborator_report': {},
                   'authors': ['Andrew Morris', 'Hunter Moseley', 'Isabel Escobar'],
                   'grants': ['P42ES007380', 'P42 ES007380']}},
            'project 2': {
              'Andrew Morris': {'ORCID': '0000-0003-1910-4865',
                   'affiliations': ['kentucky'],
                   'cutoff_year': 2020,
                   'email': 'a.j.morris@uky.edu',
                   'first_name': 'Andrew',
                   'last_name': 'Morris',
                   'pubmed_name_search': 'Andrew Morris',
                   'scholar_id': '-j7fxnEAAAAJ',
                   'project_report': {'email_subject': 'New PubMed Publications',
                    'email_body': 'Attached is the report for publications found.\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
                    'template': '<author_loop><pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>',
                    'from_email': 'ptth222@uky.edu',
                    'cc_email': [],
                    'to_email': ['ptth222@uky.edu']},
                   'grants': ['P42ES007380', 'P42 ES007380']},
              'Hunter Moseley': {'ORCID': '0000-0003-3995-5368',
                   'affiliations': ['kentucky'],
                   'cutoff_year': 2020,
                   'email': 'hunter.moseley@gmail.com',
                   'first_name': 'Hunter',
                   'last_name': 'Moseley',
                   'pubmed_name_search': 'Hunter Moseley',
                   'scholar_id': 'ctE_FZMAAAAJ',
                   'project_report': {'email_subject': 'New PubMed Publications',
                    'email_body': 'Attached is the report for publications found.\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
                    'template': '<author_loop><pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>',
                    'from_email': 'ptth222@uky.edu',
                    'cc_email': [],
                    'to_email': ['ptth222@uky.edu']},
                   'grants': ['P42ES007380', 'P42 ES007380']}},
            'project 3': {
              'Andrew Morris': {'ORCID': '0000-0003-1910-4865',
                   'affiliations': ['kentucky'],
                   'cutoff_year': 2020,
                   'email': 'a.j.morris@uky.edu',
                   'first_name': 'Andrew',
                   'last_name': 'Morris',
                   'pubmed_name_search': 'Andrew Morris',
                   'scholar_id': '-j7fxnEAAAAJ',
                   'project_report': {'email_subject': 'New PubMed Publications',
                    'email_body': 'Attached is the report for publications found.\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
                    'template': '<author_loop><pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>',
                    'from_email': 'ptth222@uky.edu',
                    'cc_email': [],
                    'to_email': ['ptth222@uky.edu']},
                   'grants': ['P42ES007380', 'P42 ES007380']},
              'Hunter Moseley': {'ORCID': '0000-0003-3995-5368',
                   'affiliations': ['kentucky'],
                   'cutoff_year': 2020,
                   'email': 'hunter.moseley@gmail.com',
                   'first_name': 'Hunter',
                   'last_name': 'Moseley',
                   'pubmed_name_search': 'Hunter Moseley',
                   'scholar_id': 'ctE_FZMAAAAJ',
                   'project_report': {'email_subject': 'New PubMed Publications',
                    'email_body': 'Attached is the report for publications found.\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
                    'template': '<author_loop><pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>',
                    'from_email': 'ptth222@uky.edu',
                    'cc_email': [],
                    'to_email': ['ptth222@uky.edu']},
                   'grants': ['P42ES007380', 'P42 ES007380']}}}
        
        