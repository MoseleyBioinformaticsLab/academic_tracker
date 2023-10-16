# -*- coding: utf-8 -*-
"""
Regenerate intermediate testing files, must be ran from academic_tracker diretory, must use pytest to run.
"""

import json
import copy
import os

import pymed
import xml.etree.ElementTree as ET
import pytest

from academic_tracker.fileio import load_json
from academic_tracker.ref_srch_webio import search_references_on_source
from academic_tracker.ref_srch_modularized import build_publication_dict




@pytest.fixture
def config_dict_Hunter_only():
    return load_json(os.path.join("tests", "testing_files", "config_Hunter_only.json"))

@pytest.fixture
def tokenized_citations():
    return load_json(os.path.join("tests", "testing_files", "tokenized_ref_test.json"))

@pytest.fixture
def original_queries():
    query_json = load_json(os.path.join("tests", "testing_files", "all_queries_ref.json"))
    ## Convert PubMed dictionaries back to articles class.
    for i, pub_list in enumerate(query_json["PubMed"]):
        new_list = []
        for pub in pub_list:
            new_list.append(pymed.article.PubMedArticle(ET.fromstring(pub["xml"])))
        query_json["PubMed"][i] = new_list
    return query_json




def test_build_publication_dict_with_Crossref(mocker, config_dict_Hunter_only, original_queries, tokenized_citations):
    running_pubs = {}
    running_pubs1, matching_key_for_citation1, all_pubs = search_references_on_source("PubMed", running_pubs, tokenized_citations, "asdf", original_queries["PubMed"])
    running_pubs2, matching_key_for_citation2, all_pubs = search_references_on_source("Crossref", copy.deepcopy(running_pubs1), tokenized_citations, "asdf", original_queries["Crossref"])
    
    running_pubs3, matching_key_for_citation3, all_pubs = search_references_on_source("PubMed", copy.deepcopy(running_pubs2), tokenized_citations, "asdf", original_queries["PubMed"])
    running_pubs4, matching_key_for_citation4, all_pubs = search_references_on_source("Crossref", copy.deepcopy(running_pubs3), tokenized_citations, "asdf", original_queries["Crossref"])
    
    
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "all", "running_pubs1.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "all", "running_pubs2.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "all", "running_pubs3.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(running_pubs3, indent=2, sort_keys=True))
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "all", "running_pubs4.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(running_pubs4, indent=2, sort_keys=True))
    
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "all", "matching_key_for_citation1.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(matching_key_for_citation1, indent=2, sort_keys=True))
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "all", "matching_key_for_citation2.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(matching_key_for_citation2, indent=2, sort_keys=True))
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "all", "matching_key_for_citation3.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(matching_key_for_citation3, indent=2, sort_keys=True))
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "all", "matching_key_for_citation4.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(matching_key_for_citation4, indent=2, sort_keys=True))
    
    
    mocker.patch("academic_tracker.ref_srch_modularized.ref_srch_webio.search_references_on_source", 
                  side_effect=[(running_pubs1, matching_key_for_citation1, original_queries["PubMed"]), 
                               (running_pubs2, matching_key_for_citation2, original_queries["Crossref"]),
                               (running_pubs3, matching_key_for_citation3, original_queries["PubMed"]),
                               (running_pubs4, matching_key_for_citation4, original_queries["Crossref"])])
    
    actual_publication_dict, actual_tokenized_citations, _ = build_publication_dict(config_dict_Hunter_only, tokenized_citations, False, False)
    
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "all", "tokenized_reference.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(actual_tokenized_citations, indent=2, sort_keys=True))
    
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "all", "publication_dict.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))




def test_build_publication_dict_no_Crossref(mocker, config_dict_Hunter_only, original_queries, tokenized_citations):
    
    running_pubs = {}
    running_pubs1, matching_key_for_citation1, all_pubs = search_references_on_source("PubMed", running_pubs, tokenized_citations, "asdf", original_queries["PubMed"])
    
    running_pubs2, matching_key_for_citation2, all_pubs = search_references_on_source("PubMed", copy.deepcopy(running_pubs1), tokenized_citations, "asdf", original_queries["PubMed"])

    
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "no_Crossref", "running_pubs1.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "no_Crossref", "running_pubs2.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
    
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "no_Crossref", "matching_key_for_citation1.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(matching_key_for_citation1, indent=2, sort_keys=True))
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "no_Crossref", "matching_key_for_citation2.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(matching_key_for_citation2, indent=2, sort_keys=True))
    
    
    mocker.patch("academic_tracker.ref_srch_modularized.ref_srch_webio.search_references_on_source", 
                  side_effect=[(running_pubs1, matching_key_for_citation1, original_queries["PubMed"]), 
                                (running_pubs2, matching_key_for_citation2, original_queries["PubMed"])])
        
    
    actual_publication_dict, actual_tokenized_citations, _ = build_publication_dict(config_dict_Hunter_only, tokenized_citations, True, False)
    
    
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "no_Crossref", "tokenized_reference.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(actual_tokenized_citations, indent=2, sort_keys=True))
    
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "no_Crossref", "publication_dict.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))




def test_build_publication_dict_no_PubMed(mocker, config_dict_Hunter_only, original_queries, tokenized_citations):
    
    running_pubs = {}
    running_pubs1, matching_key_for_citation1, all_pubs = search_references_on_source("Crossref", running_pubs, tokenized_citations, "asdf", original_queries["Crossref"])
    
    running_pubs2, matching_key_for_citation2, all_pubs = search_references_on_source("Crossref", copy.deepcopy(running_pubs1), tokenized_citations, "asdf", original_queries["Crossref"])

    
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "no_PubMed", "running_pubs1.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "no_PubMed", "running_pubs2.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
    
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "no_PubMed", "matching_key_for_citation1.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(matching_key_for_citation1, indent=2, sort_keys=True))
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "no_PubMed", "matching_key_for_citation2.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(matching_key_for_citation2, indent=2, sort_keys=True))
    
        
    mocker.patch("academic_tracker.ref_srch_modularized.ref_srch_webio.search_references_on_source", 
                  side_effect=[(running_pubs1, matching_key_for_citation1, original_queries["Crossref"]), 
                                (running_pubs2, matching_key_for_citation2, original_queries["Crossref"])])
    
    
    actual_publication_dict, actual_tokenized_citations, _ = build_publication_dict(config_dict_Hunter_only, tokenized_citations, False, True)
    
    
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "no_PubMed", "tokenized_reference.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(actual_tokenized_citations, indent=2, sort_keys=True))
    
    with open(os.path.join("tests", "testing_files", "new_intermediate_results", "ref_search", "no_PubMed", "publication_dict.json"),'w') as jsonFile:
        jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))







