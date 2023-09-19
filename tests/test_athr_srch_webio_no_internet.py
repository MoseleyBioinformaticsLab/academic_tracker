# -*- coding: utf-8 -*-

import os

import pytest
import pickle
import requests
import xml.etree.ElementTree as ET
import json

import pymed

from fixtures import authors_dict
from academic_tracker.athr_srch_webio import search_PubMed_for_pubs, search_ORCID_for_pubs, search_Google_Scholar_for_pubs
from academic_tracker.athr_srch_webio import search_Crossref_for_pubs
from academic_tracker.fileio import load_json



@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
    


@pytest.fixture
def config_dict_Hunter_only():
    return load_json(os.path.join("tests", "testing_files", "config_Hunter_only.json"))

@pytest.fixture
def original_queries():
    query_json = load_json(os.path.join("tests", "testing_files", "all_queries.json"))
    ## Convert PubMed dictionaries back to articles class.
    for author, pub_list in query_json["PubMed"].items():
        new_list = []
        for pub in pub_list:
            new_list.append(pymed.article.PubMedArticle(ET.fromstring(pub["xml"])))
        query_json["PubMed"][author] = new_list
    return query_json



## The expected_dicts here are generated in test_athr_srch_modularized.py.

def test_search_PubMed_for_pubs_first_pass(config_dict_Hunter_only, original_queries):
    expected_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs1.json"))
    test_publication_dict, all_queries = search_PubMed_for_pubs({}, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", 65, original_queries["PubMed"])
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["PubMed"]


def test_search_PubMed_for_pubs_second_pass(config_dict_Hunter_only, original_queries):
    running_pubs = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs4.json"))
    expected_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs5.json"))
    test_publication_dict, all_queries = search_PubMed_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", 65, original_queries["PubMed"])
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["PubMed"]


def test_search_ORCID_for_pubs_first_pass(config_dict_Hunter_only, original_queries):
    expected_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs1.json"))
    test_publication_dict, all_queries = search_ORCID_for_pubs({}, "asdf", "asdf", config_dict_Hunter_only["Authors"], 65, original_queries["ORCID"])
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["ORCID"]


def test_search_ORCID_for_pubs_second_pass(config_dict_Hunter_only, original_queries):
    running_pubs = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs3.json"))
    expected_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs4.json"))
    test_publication_dict, all_queries = search_ORCID_for_pubs(running_pubs, "asdf", "asdf", config_dict_Hunter_only["Authors"], 65, original_queries["ORCID"])
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["ORCID"]


def test_search_Google_Scholar_for_pubs_first_pass(config_dict_Hunter_only, original_queries):
    expected_dict = load_json(os.path.join("tests", "testing_files", "solo_Google_Scholar.json"))
    test_publication_dict, all_queries = search_Google_Scholar_for_pubs({}, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", 65, original_queries["Google Scholar"])
    # with open(os.path.join("tests", "testing_files", "solo_Google_Scholar.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(test_publication_dict, indent=2, sort_keys=True))
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["Google Scholar"]


def test_search_Google_Scholar_for_pubs_second_pass(config_dict_Hunter_only, original_queries):
    running_pubs = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs6.json"))
    expected_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs7.json"))
    test_publication_dict, all_queries = search_Google_Scholar_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", 65, original_queries["Google Scholar"])
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["Google Scholar"]
    

def test_search_Crossref_for_pubs_first_pass(config_dict_Hunter_only, original_queries):
    expected_dict = load_json(os.path.join("tests", "testing_files", "solo_Crossref.json"))
    test_publication_dict, all_queries = search_Crossref_for_pubs({}, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", 65, original_queries["Crossref"])
    # with open(os.path.join("tests", "testing_files", "solo_Crossref.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(test_publication_dict, indent=2, sort_keys=True))
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["Crossref"]


def test_search_Crossref_for_pubs_second_pass(config_dict_Hunter_only, original_queries):
    running_pubs = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs7.json"))
    expected_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs8.json"))
    test_publication_dict, all_queries = search_Crossref_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", 65, original_queries["Crossref"])
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["Crossref"]




