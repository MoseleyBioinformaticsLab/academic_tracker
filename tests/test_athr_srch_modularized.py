# -*- coding: utf-8 -*-


import os
import requests
import re
import datetime
import xml.etree.ElementTree as ET
import json
import copy

import pytest
import shutil
import pymed

from academic_tracker.athr_srch_modularized import input_reading_and_checking, generate_internal_data_and_check_authors
from academic_tracker.athr_srch_modularized import build_publication_dict, save_and_send_reports_and_emails
from academic_tracker.fileio import load_json, read_text_from_txt
from academic_tracker.athr_srch_webio import search_PubMed_for_pubs, search_ORCID_for_pubs, search_Google_Scholar_for_pubs, search_Crossref_for_pubs


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
    


@pytest.fixture
def config_dict():
    return load_json(os.path.join("tests", "testing_files", "config_truncated.json"))

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





def test_input_reading_and_checking(config_dict):
    config_json_filepath = os.path.join("tests", "testing_files", "config_truncated.json")
    
    expected_config_dict = config_dict
    
    actual_config_dict = input_reading_and_checking(config_json_filepath, False, False, False, False)
    
    assert expected_config_dict == actual_config_dict
    

def test_input_reading_and_checking_no_ORCID():
    config_json_filepath = os.path.join("tests", "testing_files", "config_truncated_noORCID.json")
    
    expected_config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated_noORCID.json"))
    
    actual_config_dict = input_reading_and_checking(config_json_filepath, False, False, False, False)
    
    assert expected_config_dict == actual_config_dict
    

def test_input_reading_and_checking_no_PubMed():
    config_json_filepath = os.path.join("tests", "testing_files", "config_truncated_noPubMed.json")
    
    expected_config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated_noPubMed.json"))
    
    actual_config_dict = input_reading_and_checking(config_json_filepath, False, False, False, False)
    
    assert expected_config_dict == actual_config_dict
    
    
def test_input_reading_and_checking_no_Crossref():
    config_json_filepath = os.path.join("tests", "testing_files", "config_truncated_noCrossref.json")
        
    with pytest.raises(BaseException):
        actual_config_dict = input_reading_and_checking(config_json_filepath, False, False, False, False)
        

def test_input_reading_and_checking_no_Crossref_noGS():
    config_json_filepath = os.path.join("tests", "testing_files", "config_truncated_noCrossref.json")
        
    expected_config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated_noCrossref.json"))
    
    actual_config_dict = input_reading_and_checking(config_json_filepath, False, True, False, False)
    
    assert expected_config_dict == actual_config_dict
    



def test_generate_internal_data_and_check_authors(config_dict, capsys):
    expected_authors_by_project_dict = load_json(os.path.join("tests", "testing_files", "authors_by_project_dict_truncated.json"))
    expected_config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated_authors_adjusted.json"))
    
    actual_authors_by_project_dict, actual_config_dict = generate_internal_data_and_check_authors(config_dict)
    # with open(os.path.join("tests", "testing_files", "config_truncated_authors_adjusted_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_config_dict, indent=2, sort_keys=True))
    
    captured = capsys.readouterr()
    
    assert len(captured.out) > 0
    assert expected_authors_by_project_dict == actual_authors_by_project_dict
    assert expected_config_dict == actual_config_dict



def test_build_publication_dict_all_sources(mocker, config_dict_Hunter_only, original_queries):
    ## Code to run and save intermediate running_pubs. This is slow, so they are saved once and read in later.
    # running_pubs = {}
    # running_pubs1, _ = search_PubMed_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
    # running_pubs2, _ = search_ORCID_for_pubs(copy.deepcopy(running_pubs1), "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
    # running_pubs3, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs2), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])
    # running_pubs4, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs3), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])
    
    # running_pubs5, _ = search_PubMed_for_pubs(copy.deepcopy(running_pubs4), config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
    # running_pubs6, _ = search_ORCID_for_pubs(copy.deepcopy(running_pubs5), "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
    # running_pubs7, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs6), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])
    # running_pubs8, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs7), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs1.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs2.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs3.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs3, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs4.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs4, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs5.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs5, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs6.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs6, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs7.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs7, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs8.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs8, indent=2, sort_keys=True))
    
    
    running_pubs1 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs1.json"))
    running_pubs2 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs2.json"))
    running_pubs3 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs3.json"))
    running_pubs4 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs4.json"))
    running_pubs5 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs5.json"))
    running_pubs6 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs6.json"))
    running_pubs7 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs7.json"))
    running_pubs8 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs8.json"))
    
            
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_PubMed_for_pubs", 
                  side_effect=[(running_pubs1, original_queries["PubMed"]), (running_pubs5, original_queries["PubMed"])])
    
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_ORCID_for_pubs", 
                  side_effect=[(running_pubs2, original_queries["ORCID"]), (running_pubs6, original_queries["ORCID"])])
    
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Google_Scholar_for_pubs", 
                  side_effect=[(running_pubs3, original_queries["Google Scholar"]), (running_pubs7, original_queries["Google Scholar"])])
    
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Crossref_for_pubs", 
                  side_effect=[(running_pubs4, original_queries["Crossref"]), (running_pubs8, original_queries["Crossref"])])
    
    
    actual_publication_dict, _ = build_publication_dict(config_dict_Hunter_only, {}, False, False, False, False)
    
    ## Have to sort to match how it is saved as JSON.
    actual_publication_dict = {key:{key2:value2 for key2, value2 in sorted(value.items())} for key, value in sorted(actual_publication_dict.items())}
    
    expected_pub_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "publication_dict.json"))
        
    assert expected_pub_dict == actual_publication_dict



def test_build_publication_dict_no_ORCID(mocker, config_dict_Hunter_only, original_queries):
    ## Code to run and save intermediate running_pubs. This is slow, so they are saved once and read in later.
    # running_pubs = {}
    # running_pubs1, _ = search_PubMed_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
    # running_pubs2, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs1), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])
    # running_pubs3, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs2), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])
    
    # running_pubs4, _ = search_PubMed_for_pubs(copy.deepcopy(running_pubs3), config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
    # running_pubs5, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs4), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])
    # running_pubs6, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs5), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_ORCID", "running_pubs1.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_ORCID", "running_pubs2.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_ORCID", "running_pubs3.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs3, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_ORCID", "running_pubs4.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs4, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_ORCID", "running_pubs5.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs5, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_ORCID", "running_pubs6.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs6, indent=2, sort_keys=True))
    
    
    running_pubs1 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_ORCID", "running_pubs1.json"))
    running_pubs2 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_ORCID", "running_pubs2.json"))
    running_pubs3 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_ORCID", "running_pubs3.json"))
    running_pubs4 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_ORCID", "running_pubs4.json"))
    running_pubs5 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_ORCID", "running_pubs5.json"))
    running_pubs6 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_ORCID", "running_pubs6.json"))
    
            
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_PubMed_for_pubs", 
                  side_effect=[(running_pubs1, original_queries["PubMed"]), (running_pubs4, original_queries["PubMed"])])
        
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Google_Scholar_for_pubs", 
                  side_effect=[(running_pubs2, original_queries["Google Scholar"]), (running_pubs5, original_queries["Google Scholar"])])
    
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Crossref_for_pubs", 
                  side_effect=[(running_pubs3, original_queries["Crossref"]), (running_pubs6, original_queries["Crossref"])])
    
    
    actual_publication_dict, _ = build_publication_dict(config_dict_Hunter_only, {}, True, False, False, False)
    
    ## Have to sort to match how it is saved as JSON.
    actual_publication_dict = {key:{key2:value2 for key2, value2 in sorted(value.items())} for key, value in sorted(actual_publication_dict.items())}
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_ORCID", "publication_dict.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))
    
    expected_pub_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_ORCID", "publication_dict.json"))
    
    assert expected_pub_dict == actual_publication_dict
    


def test_build_publication_dict_no_Crossref(mocker, config_dict_Hunter_only, original_queries):
    ## Code to run and save intermediate running_pubs. This is slow, so they are saved once and read in later.
    # running_pubs = {}
    # running_pubs1, _ = search_PubMed_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
    # running_pubs2, _ = search_ORCID_for_pubs(copy.deepcopy(running_pubs1), "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
    # running_pubs3, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs2), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])
    
    # running_pubs4, _ = search_PubMed_for_pubs(copy.deepcopy(running_pubs3), config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
    # running_pubs5, _ = search_ORCID_for_pubs(copy.deepcopy(running_pubs4), "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
    # running_pubs6, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs5), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Crossref", "running_pubs1.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Crossref", "running_pubs2.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Crossref", "running_pubs3.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs3, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Crossref", "running_pubs4.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs4, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Crossref", "running_pubs5.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs5, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Crossref", "running_pubs6.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs6, indent=2, sort_keys=True))
    
    
    running_pubs1 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Crossref", "running_pubs1.json"))
    running_pubs2 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Crossref", "running_pubs2.json"))
    running_pubs3 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Crossref", "running_pubs3.json"))
    running_pubs4 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Crossref", "running_pubs4.json"))
    running_pubs5 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Crossref", "running_pubs5.json"))
    running_pubs6 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Crossref", "running_pubs6.json"))
    
            
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_PubMed_for_pubs", 
                  side_effect=[(running_pubs1, original_queries["PubMed"]), (running_pubs4, original_queries["PubMed"])])
        
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_ORCID_for_pubs", 
                  side_effect=[(running_pubs2, original_queries["ORCID"]), (running_pubs5, original_queries["ORCID"])])
    
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Google_Scholar_for_pubs", 
                  side_effect=[(running_pubs3, original_queries["Google Scholar"]), (running_pubs6, original_queries["Google Scholar"])])
    
    
    actual_publication_dict, _ = build_publication_dict(config_dict_Hunter_only, {}, False, False, True, False)
    
    ## Have to sort to match how it is saved as JSON.
    actual_publication_dict = {key:{key2:value2 for key2, value2 in sorted(value.items())} for key, value in sorted(actual_publication_dict.items())}
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Crossref", "publication_dict.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))
    
    expected_pub_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Crossref", "publication_dict.json"))
    
    assert expected_pub_dict == actual_publication_dict
    


def test_build_publication_dict_no_Google_Scholar(mocker, config_dict_Hunter_only, original_queries):
    ## Code to run and save intermediate running_pubs. This is slow, so they are saved once and read in later.
    # running_pubs = {}
    # running_pubs1, _ = search_PubMed_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
    # running_pubs2, _ = search_ORCID_for_pubs(copy.deepcopy(running_pubs1), "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
    # running_pubs3, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs2), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])
    
    # running_pubs4, _ = search_PubMed_for_pubs(copy.deepcopy(running_pubs3), config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
    # running_pubs5, _ = search_ORCID_for_pubs(copy.deepcopy(running_pubs4), "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
    # running_pubs6, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs5), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Google_Scholar", "running_pubs1.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Google_Scholar", "running_pubs2.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Google_Scholar", "running_pubs3.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs3, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Google_Scholar", "running_pubs4.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs4, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Google_Scholar", "running_pubs5.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs5, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Google_Scholar", "running_pubs6.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs6, indent=2, sort_keys=True))
    
    
    running_pubs1 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Google_Scholar", "running_pubs1.json"))
    running_pubs2 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Google_Scholar", "running_pubs2.json"))
    running_pubs3 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Google_Scholar", "running_pubs3.json"))
    running_pubs4 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Google_Scholar", "running_pubs4.json"))
    running_pubs5 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Google_Scholar", "running_pubs5.json"))
    running_pubs6 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Google_Scholar", "running_pubs6.json"))
    
            
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_PubMed_for_pubs", 
                  side_effect=[(running_pubs1, original_queries["PubMed"]), (running_pubs4, original_queries["PubMed"])])
        
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_ORCID_for_pubs", 
                  side_effect=[(running_pubs2, original_queries["ORCID"]), (running_pubs5, original_queries["ORCID"])])
    
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Crossref_for_pubs", 
                  side_effect=[(running_pubs3, original_queries["Crossref"]), (running_pubs6, original_queries["Crossref"])])
    
    
    actual_publication_dict, _ = build_publication_dict(config_dict_Hunter_only, {}, False, True, False, False)
    
    ## Have to sort to match how it is saved as JSON.
    actual_publication_dict = {key:{key2:value2 for key2, value2 in sorted(value.items())} for key, value in sorted(actual_publication_dict.items())}
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Google_Scholar", "publication_dict.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))
    
    expected_pub_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_Google_Scholar", "publication_dict.json"))
    
    assert expected_pub_dict == actual_publication_dict
    
 
    
def test_build_publication_dict_no_PubMed(mocker, config_dict_Hunter_only, original_queries):
    ## Code to run and save intermediate running_pubs. This is slow, so they are saved once and read in later.
    # running_pubs = {}
    # running_pubs1, _ = search_ORCID_for_pubs(running_pubs, "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
    # running_pubs2, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs1), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])
    # running_pubs3, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs2), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])
    
    # running_pubs4, _ = search_ORCID_for_pubs(copy.deepcopy(running_pubs3), "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
    # running_pubs5, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs4), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])
    # running_pubs6, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs5), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs1.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs2.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs3.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs3, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs4.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs4, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs5.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs5, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs6.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs6, indent=2, sort_keys=True))
    
    
    running_pubs1 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs1.json"))
    running_pubs2 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs2.json"))
    running_pubs3 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs3.json"))
    running_pubs4 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs4.json"))
    running_pubs5 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs5.json"))
    running_pubs6 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs6.json"))
    
            
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_ORCID_for_pubs", 
                  side_effect=[(running_pubs1, original_queries["ORCID"]), (running_pubs4, original_queries["ORCID"])])
    
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Google_Scholar_for_pubs", 
                  side_effect=[(running_pubs2, original_queries["Google Scholar"]), (running_pubs5, original_queries["Google Scholar"])])
    
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Crossref_for_pubs", 
                  side_effect=[(running_pubs3, original_queries["Crossref"]), (running_pubs6, original_queries["Crossref"])])
    
    
    actual_publication_dict, _ = build_publication_dict(config_dict_Hunter_only, {}, False, False, False, True)
    
    ## Have to sort to match how it is saved as JSON.
    actual_publication_dict = {key:{key2:value2 for key2, value2 in sorted(value.items())} for key, value in sorted(actual_publication_dict.items())}
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "publication_dict.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))
    
    expected_pub_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "publication_dict.json"))
    
    assert expected_pub_dict == actual_publication_dict
    

    
def test_build_publication_dict_duplicates(mocker, config_dict_Hunter_only, original_queries):
    expected_pub_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "publication_dict.json"))
    pub_to_duplicate = ""
    for pub_id in expected_pub_dict:
        pub_to_duplicate = pub_id
        break
    prev_pubs = {pub_to_duplicate:expected_pub_dict[pub_to_duplicate]}
    
    
    running_pubs1 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs1.json"))
    running_pubs2 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs2.json"))
    running_pubs3 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs3.json"))
    running_pubs4 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs4.json"))
    running_pubs5 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs5.json"))
    running_pubs6 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs6.json"))
    running_pubs7 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs7.json"))
    running_pubs8 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs8.json"))
    
            
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_PubMed_for_pubs", 
                  side_effect=[(running_pubs1, original_queries["PubMed"]), (running_pubs5, original_queries["PubMed"])])
    
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_ORCID_for_pubs", 
                  side_effect=[(running_pubs2, original_queries["ORCID"]), (running_pubs6, original_queries["ORCID"])])
    
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Google_Scholar_for_pubs", 
                  side_effect=[(running_pubs3, original_queries["Google Scholar"]), (running_pubs7, original_queries["Google Scholar"])])
    
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Crossref_for_pubs", 
                  side_effect=[(running_pubs4, original_queries["Crossref"]), (running_pubs8, original_queries["Crossref"])])
    
    actual_publication_dict, _ = build_publication_dict(config_dict_Hunter_only, prev_pubs, False, False, False, False)
    
    ## Have to sort to match how it is saved as JSON.
    actual_publication_dict = {key:{key2:value2 for key2, value2 in sorted(value.items())} for key, value in sorted(actual_publication_dict.items())}
    
    del expected_pub_dict[pub_to_duplicate]
    
    assert expected_pub_dict == actual_publication_dict



def test_build_publication_dict_no_pubs_found(mocker, config_dict_Hunter_only, capsys):
    # config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated.json"))
           
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_PubMed_for_pubs", 
                  side_effect=[({}, {}), ({}, {})])
    
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_ORCID_for_pubs", 
                  side_effect=[({}, {}), ({}, {})])
    
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Google_Scholar_for_pubs", 
                  side_effect=[({}, {}), ({}, {})])
    
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Crossref_for_pubs", 
                  side_effect=[({}, {}), ({}, {})])
    
    with pytest.raises(SystemExit):
        actual_publication_dict, _ = build_publication_dict(config_dict_Hunter_only, {}, False, False, False, False)
    
    captured = capsys.readouterr()
    expected_message = "No new publications found." + "\n"
    assert expected_message in captured.out
    



def test_save_and_send_reports_and_emails_no_email(config_dict, mocker):
    
    def emails(*args, **kwargs):
        return {"creation_date":"asdf", "emails":[]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_emails_and_reports.create_project_reports_and_emails", emails)
    
    pub_dict = load_json(os.path.join("tests", "testing_files", "publication_dict_truncated.json"))
    authors_by_project_dict = load_json(os.path.join("tests", "testing_files", "authors_by_project_dict_truncated.json"))
    
    config_dict["summary_report"] = {}
    config_dict["summary_report"]["template"] = read_text_from_txt(os.path.join("tests", "testing_files", "athr_srch_build_loop_template_string.txt"))
    
    save_dir = save_and_send_reports_and_emails(authors_by_project_dict, pub_dict, config_dict, True)
    # with open(os.path.join("tests", "testing_files", "athr_srch_summary_report_custom_template_new.txt"), 'wb') as outFile:
    #     outFile.write(read_text_from_txt(os.path.join(save_dir, "summary_report.txt")).encode("utf-8"))
    
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert read_text_from_txt(os.path.join("tests", "testing_files", "athr_srch_summary_report_custom_template.txt")) == read_text_from_txt(os.path.join(save_dir, "summary_report.txt"))
    assert not os.path.exists(os.path.join(save_dir, "emails.json"))



def test_save_and_send_reports_and_emails_with_email(config_dict, mocker):
    
    def emails(*args, **kwargs):
        return {"creation_date":"asdf", "emails":[]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_emails_and_reports.create_project_reports_and_emails", emails)
    
    pub_dict = load_json(os.path.join("tests", "testing_files", "publication_dict_truncated.json"))
    authors_by_project_dict = load_json(os.path.join("tests", "testing_files", "authors_by_project_dict_truncated.json"))
    
    config_dict["summary_report"] = {}
    config_dict["summary_report"]["template"] = read_text_from_txt(os.path.join("tests", "testing_files", "athr_srch_build_loop_template_string.txt"))
    config_dict["summary_report"]["from_email"] = "ptth222@uky.edu"
    config_dict["summary_report"]["to_email"] = ["ptth222@uky.edu"]
    config_dict["summary_report"]["cc_email"] = ["ptth222@uky.edu"]
    config_dict["summary_report"]["email_body"] = "Body"
    config_dict["summary_report"]["email_subject"] = "Subject"
    
    save_dir = save_and_send_reports_and_emails(authors_by_project_dict, pub_dict, config_dict, True)
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert read_text_from_txt(os.path.join("tests", "testing_files", "athr_srch_summary_report_custom_template.txt")) == read_text_from_txt(os.path.join(save_dir, "summary_report.txt"))
    assert os.path.exists(os.path.join(save_dir, "emails.json"))



def test_save_and_send_reports_and_emails_default_template(config_dict, mocker):
    
    def emails(*args, **kwargs):
        return {"creation_date":"asdf", "emails":[]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_emails_and_reports.create_project_reports_and_emails", emails)
    
    pub_dict = load_json(os.path.join("tests", "testing_files", "publication_dict_truncated.json"))
    ## Add Travis to a publication so we can test that multiple authors get reported.
    pub_dict["https://doi.org/10.1038/s41597-023-02277-x"]["authors"][1]["author_id"] = "Travis Thompson"
    authors_by_project_dict = load_json(os.path.join("tests", "testing_files", "authors_by_project_dict_truncated.json"))
    
    config_dict["summary_report"] = {}
    
    save_dir = save_and_send_reports_and_emails(authors_by_project_dict, pub_dict, config_dict, True)
    # with open(os.path.join("tests", "testing_files", "athr_srch_summary_report_new.txt"), 'wb') as outFile:
    #     outFile.write(read_text_from_txt(os.path.join(save_dir, "summary_report.txt")).encode("utf-8"))
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert read_text_from_txt(os.path.join("tests", "testing_files", "athr_srch_summary_report.txt")) == read_text_from_txt(os.path.join(save_dir, "summary_report.txt"))
    assert not os.path.exists(os.path.join(save_dir, "emails.json"))


def test_save_and_send_reports_and_emails_collab_reports(config_dict, mocker):
    
    def emails(*args, **kwargs):
        return {"creation_date":"asdf", "emails":[]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_emails_and_reports.create_project_reports_and_emails", emails)
    
    pub_dict = load_json(os.path.join("tests", "testing_files", "publication_dict_truncated.json"))
    authors_by_project_dict = load_json(os.path.join("tests", "testing_files", "authors_by_project_dict_truncated.json"))
    
    config_dict["Authors"]["Hunter Moseley"]["collaborator_report"] = {"from_email":"ptth222@uky.edu", 
                                                                    "email_body":"asdf",
                                                                    "email_subject":"asdf",
                                                                    }
    
    save_dir = save_and_send_reports_and_emails(authors_by_project_dict, pub_dict, config_dict, True)
    
    assert os.path.exists(os.path.join(save_dir, "Hunter Moseley_collaborators.csv"))
    assert os.path.exists(os.path.join(save_dir, "emails.json"))
    
    
def test_save_and_send_reports_and_emails_tabular_summary(config_dict, mocker):
    
    def emails(*args, **kwargs):
        return {"creation_date":"asdf", "emails":[]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_emails_and_reports.create_project_reports_and_emails", emails)
    
    pub_dict = load_json(os.path.join("tests", "testing_files", "publication_dict_truncated.json"))
    authors_by_project_dict = load_json(os.path.join("tests", "testing_files", "authors_by_project_dict_truncated.json"))
    
    config_dict["summary_report"] = {}
    config_dict["summary_report"]["columns"] = {"Col1":"<project_name>"}
    
    save_dir = save_and_send_reports_and_emails(authors_by_project_dict, pub_dict, config_dict, True)
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.csv"))
    


def test_save_and_send_reports_and_emails_manual_name(config_dict, mocker):
    
    def emails(*args, **kwargs):
        return {"creation_date":"asdf", "emails":[]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_emails_and_reports.create_project_reports_and_emails", emails)
    
    pub_dict = load_json(os.path.join("tests", "testing_files", "publication_dict_truncated.json"))
    authors_by_project_dict = load_json(os.path.join("tests", "testing_files", "authors_by_project_dict_truncated.json"))
    
    config_dict["summary_report"] = {}
    config_dict["summary_report"]["template"] = read_text_from_txt(os.path.join("tests", "testing_files", "athr_srch_build_loop_template_string.txt"))
    config_dict["summary_report"]["filename"] = "test_name.txt"
    
    save_dir = save_and_send_reports_and_emails(authors_by_project_dict, pub_dict, config_dict, True)
    
    assert os.path.exists(os.path.join(save_dir, "test_name.txt"))






@pytest.fixture(autouse=True)
def cleanup(request):
    """Cleanup a testing directory once we are finished."""
    def remove_test_dir():
        dir_contents = os.listdir()
        tracker_dirs = [folder for folder in dir_contents if re.match(r"tracker-(\d{10})", folder) or re.match(r"tracker-test-(\d{10})", folder)]
        for directory in tracker_dirs:
            shutil.rmtree(directory)
    request.addfinalizer(remove_test_dir)