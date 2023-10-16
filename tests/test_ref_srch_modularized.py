# -*- coding: utf-8 -*-

import os
import requests
import copy
import re
import xml.etree.ElementTree as ET
import json

import pytest
import shutil
import pymed

from academic_tracker.ref_srch_modularized import input_reading_and_checking, build_publication_dict, save_and_send_reports_and_emails
from academic_tracker.fileio import load_json, read_text_from_txt
from academic_tracker.ref_srch_webio import search_references_on_source


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


def test_input_reading_and_checking_no_prev_pub(config_dict):
    config_json_filepath = os.path.join("tests", "testing_files", "config_truncated.json")
    ref_path_or_URL = os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json")
    
    expected_config_dict = config_dict
    
    actual_config_dict, tokenized_citations, has_previous_pubs, prev_pubs = \
        input_reading_and_checking(config_json_filepath, ref_path_or_URL, False, False, False, "ignore", True)
        
    assert expected_config_dict == actual_config_dict
    assert tokenized_citations == load_json(os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json"))
    assert has_previous_pubs == False
    assert prev_pubs == {}



def test_input_reading_and_checking_has_prev_pub(config_dict):
    config_json_filepath = os.path.join("tests", "testing_files", "config_truncated.json")
    ref_path_or_URL = os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json")
    prev_pub_filepath = os.path.join("tests", "testing_files", "publication_dict_truncated.json")
    
    expected_config_dict = config_dict
    
    actual_config_dict, tokenized_citations, has_previous_pubs, prev_pubs = \
        input_reading_and_checking(config_json_filepath, ref_path_or_URL, False, False, False, prev_pub_filepath, True)
    
    assert expected_config_dict == actual_config_dict
    assert tokenized_citations == load_json(os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json"))
    assert has_previous_pubs == True
    assert prev_pubs == load_json(os.path.join("tests", "testing_files", "publication_dict_truncated.json"))
    
    
def test_input_reading_and_checking_noCrossref(config_dict):
    config_json_filepath = os.path.join("tests", "testing_files", "config_truncated_noCrossref.json")
    ref_path_or_URL = os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json")
    
    expected_config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated_noCrossref.json"))
    
    actual_config_dict, tokenized_citations, has_previous_pubs, prev_pubs = \
        input_reading_and_checking(config_json_filepath, ref_path_or_URL, False, False, False, "ignore", True)
    
    assert expected_config_dict == actual_config_dict
    assert tokenized_citations == load_json(os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json"))
    assert has_previous_pubs == False
    assert prev_pubs == {}
    

def test_input_reading_and_checking_noPubMed(config_dict):
    config_json_filepath = os.path.join("tests", "testing_files", "config_truncated_noPubMed.json")
    ref_path_or_URL = os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json")
    
    expected_config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated_noPubMed.json"))
    
    actual_config_dict, tokenized_citations, has_previous_pubs, prev_pubs = \
        input_reading_and_checking(config_json_filepath, ref_path_or_URL, False, False, False, "ignore", True)
    
    assert expected_config_dict == actual_config_dict
    assert tokenized_citations == load_json(os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json"))
    assert has_previous_pubs == False
    assert prev_pubs == {}




def test_build_publication_dict_with_Crossref(mocker, config_dict_Hunter_only, original_queries, tokenized_citations):
    
    # running_pubs = {}
    # running_pubs1, matching_key_for_citation1, all_pubs = search_references_on_source("PubMed", running_pubs, tokenized_citations, "asdf", original_queries["PubMed"])
    # running_pubs2, matching_key_for_citation2, all_pubs = search_references_on_source("Crossref", copy.deepcopy(running_pubs1), tokenized_citations, "asdf", original_queries["Crossref"])
    
    # running_pubs3, matching_key_for_citation3, all_pubs = search_references_on_source("PubMed", copy.deepcopy(running_pubs2), tokenized_citations, "asdf", original_queries["PubMed"])
    # running_pubs4, matching_key_for_citation4, all_pubs = search_references_on_source("Crossref", copy.deepcopy(running_pubs3), tokenized_citations, "asdf", original_queries["Crossref"])

    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "running_pubs1.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "running_pubs2.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "running_pubs3.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs3, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "running_pubs4.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs4, indent=2, sort_keys=True))
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "matching_key_for_citation1.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(matching_key_for_citation1, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "matching_key_for_citation2.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(matching_key_for_citation2, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "matching_key_for_citation3.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(matching_key_for_citation3, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "matching_key_for_citation4.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(matching_key_for_citation4, indent=2, sort_keys=True))
    
    running_pubs1 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "running_pubs1.json"))
    running_pubs2 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "running_pubs2.json"))
    running_pubs3 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "running_pubs3.json"))
    running_pubs4 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "running_pubs4.json"))
    
    matching_key_for_citation1 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "matching_key_for_citation1.json"))
    matching_key_for_citation2 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "matching_key_for_citation2.json"))
    matching_key_for_citation3 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "matching_key_for_citation3.json"))
    matching_key_for_citation4 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "matching_key_for_citation4.json"))
    
    mocker.patch("academic_tracker.ref_srch_modularized.ref_srch_webio.search_references_on_source", 
                  side_effect=[(running_pubs1, matching_key_for_citation1, original_queries["PubMed"]), 
                                (running_pubs2, matching_key_for_citation2, original_queries["Crossref"]),
                                (running_pubs3, matching_key_for_citation3, original_queries["PubMed"]),
                                (running_pubs4, matching_key_for_citation4, original_queries["Crossref"])])    
    
    actual_publication_dict, actual_tokenized_citations, _ = build_publication_dict(config_dict_Hunter_only, tokenized_citations, False, False)
    
    ## Have to sort to match how it is saved as JSON.
    actual_publication_dict = {key:{key2:value2 for key2, value2 in sorted(value.items())} for key, value in sorted(actual_publication_dict.items())}
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "test_tok_cits.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_tokenized_citations, indent=2, sort_keys=True))
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "test_pub_dict.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))
    
    expected_pub_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "publication_dict.json"))
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "all", "tokenized_reference.json"))
    
    assert expected_pub_dict == actual_publication_dict
    assert expected_tokenized_citations == actual_tokenized_citations
    


def test_build_publication_dict_no_Crossref(mocker, config_dict_Hunter_only, original_queries, tokenized_citations):
    
    # running_pubs = {}
    # running_pubs1, matching_key_for_citation1, all_pubs = search_references_on_source("PubMed", running_pubs, tokenized_citations, "asdf", original_queries["PubMed"])
    
    # running_pubs2, matching_key_for_citation2, all_pubs = search_references_on_source("PubMed", copy.deepcopy(running_pubs1), tokenized_citations, "asdf", original_queries["PubMed"])

    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "running_pubs1.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "running_pubs2.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "matching_key_for_citation1.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(matching_key_for_citation1, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "matching_key_for_citation2.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(matching_key_for_citation2, indent=2, sort_keys=True))
    
    running_pubs1 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "running_pubs1.json"))
    running_pubs2 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "running_pubs2.json"))
    
    matching_key_for_citation1 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "matching_key_for_citation1.json"))
    matching_key_for_citation2 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "matching_key_for_citation2.json"))
    
    mocker.patch("academic_tracker.ref_srch_modularized.ref_srch_webio.search_references_on_source", 
                  side_effect=[(running_pubs1, matching_key_for_citation1, original_queries["PubMed"]), 
                                (running_pubs2, matching_key_for_citation2, original_queries["PubMed"])])
        
    
    actual_publication_dict, actual_tokenized_citations, _ = build_publication_dict(config_dict_Hunter_only, tokenized_citations, True, False)
    
    ## Have to sort to match how it is saved as JSON.
    actual_publication_dict = {key:{key2:value2 for key2, value2 in sorted(value.items())} for key, value in sorted(actual_publication_dict.items())}
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "test_tok_cits.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_tokenized_citations, indent=2, sort_keys=True))
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "test_pub_dict.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))
    
    expected_pub_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "publication_dict.json"))
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "tokenized_reference.json"))
    
    assert expected_pub_dict == actual_publication_dict
    assert expected_tokenized_citations == actual_tokenized_citations
    
    


def test_build_publication_dict_no_PubMed(mocker, config_dict_Hunter_only, original_queries, tokenized_citations):
    
    # running_pubs = {}
    # running_pubs1, matching_key_for_citation1, all_pubs = search_references_on_source("Crossref", running_pubs, tokenized_citations, "asdf", original_queries["Crossref"])
    
    # running_pubs2, matching_key_for_citation2, all_pubs = search_references_on_source("Crossref", copy.deepcopy(running_pubs1), tokenized_citations, "asdf", original_queries["Crossref"])

    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "running_pubs1.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "running_pubs2.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "matching_key_for_citation1.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(matching_key_for_citation1, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "matching_key_for_citation2.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(matching_key_for_citation2, indent=2, sort_keys=True))
    
    running_pubs1 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "running_pubs1.json"))
    running_pubs2 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "running_pubs2.json"))
    
    matching_key_for_citation1 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "matching_key_for_citation1.json"))
    matching_key_for_citation2 = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "matching_key_for_citation2.json"))
        
    mocker.patch("academic_tracker.ref_srch_modularized.ref_srch_webio.search_references_on_source", 
                  side_effect=[(running_pubs1, matching_key_for_citation1, original_queries["Crossref"]), 
                                (running_pubs2, matching_key_for_citation2, original_queries["Crossref"])])
    
    
    actual_publication_dict, actual_tokenized_citations, _ = build_publication_dict(config_dict_Hunter_only, tokenized_citations, False, True)
    
    ## Have to sort to match how it is saved as JSON.
    actual_publication_dict = {key:{key2:value2 for key2, value2 in sorted(value.items())} for key, value in sorted(actual_publication_dict.items())}
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "test_tok_cits.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_tokenized_citations, indent=2, sort_keys=True))
    
    # with open(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "test_pub_dict.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))
    
    expected_pub_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "publication_dict.json"))
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "tokenized_reference.json"))
    
    assert expected_pub_dict == actual_publication_dict
    assert expected_tokenized_citations == actual_tokenized_citations




def test_save_and_send_reports_and_emails_no_email(config_dict):
    
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_citations_for_report_test.json"))
    pub_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_Crossref_pub_dict.json"))
    
    config_dict["summary_report"] = {}
    config_dict["summary_report"]["template"] = read_text_from_txt(os.path.join("tests", "testing_files", "ref_srch_report_template_string.txt"))
    
    save_dir = save_and_send_reports_and_emails(config_dict, tokenized_citations, pub_dict, {}, False, False)
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert read_text_from_txt(os.path.join("tests", "testing_files", "ref_srch_report_test1.txt")) == read_text_from_txt(os.path.join(save_dir, "summary_report.txt"))
    assert not os.path.exists(os.path.join(save_dir, "emails.json"))



def test_save_and_send_reports_and_emails_with_email(config_dict):
    
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_citations_for_report_test.json"))
    pub_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_Crossref_pub_dict.json"))
    
    config_dict["summary_report"] = {}
    config_dict["summary_report"]["template"] = read_text_from_txt(os.path.join("tests", "testing_files", "ref_srch_report_template_string.txt"))
    config_dict["summary_report"]["from_email"] = "ptth222@uky.edu"
    config_dict["summary_report"]["to_email"] = ["ptth222@uky.edu"]
    config_dict["summary_report"]["cc_email"] = ["ptth222@uky.edu"]
    config_dict["summary_report"]["email_body"] = "Body"
    config_dict["summary_report"]["email_subject"] = "Subject"
    
    save_dir = save_and_send_reports_and_emails(config_dict, tokenized_citations, pub_dict, {}, False, True)
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert read_text_from_txt(os.path.join("tests", "testing_files", "ref_srch_report_test1.txt")) == read_text_from_txt(os.path.join(save_dir, "summary_report.txt"))
    assert os.path.exists(os.path.join(save_dir, "emails.json"))



def test_save_and_send_reports_and_emails_default_template(config_dict):
    
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_citations_for_report_test.json"))
    pub_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_Crossref_pub_dict.json"))
    
    config_dict["summary_report"] = {}
    
    save_dir = save_and_send_reports_and_emails(config_dict, tokenized_citations, pub_dict, {}, False, False)
    # with open(os.path.join("tests", "testing_files", "ref_srch_report_default_new.txt"), 'wb') as outFile:
    #     outFile.write(read_text_from_txt(os.path.join(save_dir, "summary_report.txt")).encode("utf-8"))
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert read_text_from_txt(os.path.join("tests", "testing_files", "ref_srch_report_default.txt")) == read_text_from_txt(os.path.join(save_dir, "summary_report.txt"))
    assert not os.path.exists(os.path.join(save_dir, "emails.json"))
    
    
def test_save_and_send_reports_and_emails_tabular(config_dict):
    
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_citations_for_report_test.json"))
    pub_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_Crossref_pub_dict.json"))
    
    config_dict["summary_report"] = {}
    config_dict["summary_report"]["columns"] = {"Col1":"<author_first>"}
    
    save_dir = save_and_send_reports_and_emails(config_dict, tokenized_citations, pub_dict, {}, False, False)
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.csv"))
    assert not os.path.exists(os.path.join(save_dir, "emails.json"))
    
    
def test_save_and_send_reports_and_emails_manual_name(config_dict):
    
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_citations_for_report_test.json"))
    pub_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_Crossref_pub_dict.json"))
    
    config_dict["summary_report"] = {}
    config_dict["summary_report"]["template"] = read_text_from_txt(os.path.join("tests", "testing_files", "ref_srch_report_template_string.txt"))
    config_dict["summary_report"]["filename"] = "test_name.txt"
    
    save_dir = save_and_send_reports_and_emails(config_dict, tokenized_citations, pub_dict, {}, False, False)
    
    assert os.path.exists(os.path.join(save_dir, "test_name.txt"))
    assert not os.path.exists(os.path.join(save_dir, "emails.json"))









@pytest.fixture(autouse=True)
def cleanup(request):
    """Cleanup a testing directory once we are finished."""
    def remove_test_dir():
        dir_contents = os.listdir()
        tracker_dirs = [folder for folder in dir_contents if re.match(r"tracker-(\d{10})", folder) or re.match(r"tracker-test-(\d{10})", folder)]
        for directory in tracker_dirs:
            shutil.rmtree(directory)
    request.addfinalizer(remove_test_dir)





