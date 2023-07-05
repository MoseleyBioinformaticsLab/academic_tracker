# -*- coding: utf-8 -*-

import os
import requests
import copy
import re

import pytest
import shutil

from academic_tracker.ref_srch_modularized import input_reading_and_checking, build_publication_dict, save_and_send_reports_and_emails
from academic_tracker.fileio import load_json, read_text_from_txt


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())



@pytest.fixture
def config_dict():
    return load_json(os.path.join("testing_files", "config_truncated.json"))


def test_input_reading_and_checking_no_prev_pub(config_dict):
    config_json_filepath = os.path.join("testing_files", "config_truncated.json")
    ref_path_or_URL = os.path.join("testing_files", "tokenized_citations_duplicates_removed.json")
    
    expected_config_dict = config_dict
    
    actual_config_dict, tokenized_citations, has_previous_pubs, prev_pubs = input_reading_and_checking(config_json_filepath, ref_path_or_URL, False, False, False, "ignore")
    
    assert expected_config_dict == actual_config_dict
    assert tokenized_citations == load_json(os.path.join("testing_files", "tokenized_citations_duplicates_removed.json"))
    assert has_previous_pubs == False
    assert prev_pubs == {}



def test_input_reading_and_checking_has_prev_pub(config_dict):
    config_json_filepath = os.path.join("testing_files", "config_truncated.json")
    ref_path_or_URL = os.path.join("testing_files", "tokenized_citations_duplicates_removed.json")
    prev_pub_filepath = os.path.join("testing_files", "publication_dict_truncated.json")
    
    expected_config_dict = config_dict
    
    actual_config_dict, tokenized_citations, has_previous_pubs, prev_pubs = input_reading_and_checking(config_json_filepath, ref_path_or_URL, False, False, False, prev_pub_filepath)
    
    assert expected_config_dict == actual_config_dict
    assert tokenized_citations == load_json(os.path.join("testing_files", "tokenized_citations_duplicates_removed.json"))
    assert has_previous_pubs == True
<<<<<<< Updated upstream
    assert prev_pubs == load_json(os.path.join("testing_files", "publication_dict_truncated.json"))
=======
    assert prev_pubs == load_json(os.path.join("tests", "testing_files", "publication_dict_truncated.json"))
    
    
def test_input_reading_and_checking_noCrossref(config_dict):
    config_json_filepath = os.path.join("tests", "testing_files", "config_truncated_noCrossref.json")
    ref_path_or_URL = os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json")
    
    expected_config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated_noCrossref.json"))
    
    actual_config_dict, tokenized_citations, has_previous_pubs, prev_pubs = input_reading_and_checking(config_json_filepath, ref_path_or_URL, False, False, False, "ignore")
    
    assert expected_config_dict == actual_config_dict
    assert tokenized_citations == load_json(os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json"))
    assert has_previous_pubs == False
    assert prev_pubs == {}
    

def test_input_reading_and_checking_noPubMed(config_dict):
    config_json_filepath = os.path.join("tests", "testing_files", "config_truncated_noPubMed.json")
    ref_path_or_URL = os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json")
    
    expected_config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated_noPubMed.json"))
    
    actual_config_dict, tokenized_citations, has_previous_pubs, prev_pubs = input_reading_and_checking(config_json_filepath, ref_path_or_URL, False, False, False, "ignore")
    
    assert expected_config_dict == actual_config_dict
    assert tokenized_citations == load_json(os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json"))
    assert has_previous_pubs == False
    assert prev_pubs == {}
>>>>>>> Stashed changes




def test_build_publication_dict_with_Crossref(config_dict, mocker):
    
    expected_tokenized_citations = load_json(os.path.join("testing_files", "tokenized_citations_for_report_test.json"))
    
    input_tokenized_citations = copy.deepcopy(expected_tokenized_citations)
    for citation in input_tokenized_citations:
        citation["pub_dict_key"] = ""
    
    expected_pub_dict = load_json(os.path.join("testing_files", "ref_srch_Crossref_pub_dict.json"))
    
    def mock_query(*args, **kwargs):
        return {"https://doi.org/10.3390/metabo10090368":expected_pub_dict["https://doi.org/10.3390/metabo10090368"]}, [None, "https://doi.org/10.3390/metabo10090368"]
    mocker.patch("academic_tracker.ref_srch_modularized.ref_srch_webio.search_references_on_PubMed", mock_query)
    
    def mock_query2(*args, **kwargs):
        return {"https://doi.org/10.3390/metabo11030163":expected_pub_dict["https://doi.org/10.3390/metabo11030163"]}, ["https://doi.org/10.3390/metabo11030163", None]
    mocker.patch("academic_tracker.ref_srch_modularized.ref_srch_webio.search_references_on_Crossref", mock_query2)
    
    actual_publication_dict, actual_tokenized_citations = build_publication_dict(config_dict, input_tokenized_citations, False, False)
    
    assert expected_pub_dict == actual_publication_dict
    assert expected_tokenized_citations == actual_tokenized_citations
    


def test_build_publication_dict_no_Crossref(config_dict, mocker):
    
    expected_tokenized_citations = load_json(os.path.join("testing_files", "tokenized_citations_for_report_test.json"))
    expected_tokenized_citations[0]["pub_dict_key"] = ""
    
    input_tokenized_citations = copy.deepcopy(expected_tokenized_citations)
    for citation in input_tokenized_citations:
        citation["pub_dict_key"] = ""
        
    expected_pub_dict = load_json(os.path.join("testing_files", "ref_srch_Crossref_pub_dict.json"))
    del expected_pub_dict["https://doi.org/10.3390/metabo11030163"]
    
    def mock_query(*args, **kwargs):
        return {"https://doi.org/10.3390/metabo10090368":expected_pub_dict["https://doi.org/10.3390/metabo10090368"]}, [None, "https://doi.org/10.3390/metabo10090368"]
    mocker.patch("academic_tracker.ref_srch_modularized.ref_srch_webio.search_references_on_PubMed", mock_query)
    
    def mock_query2(*args, **kwargs):
        return {"https://doi.org/10.3390/metabo11030163":expected_pub_dict["https://doi.org/10.3390/metabo11030163"]}, ["https://doi.org/10.3390/metabo11030163", None]
    mocker.patch("academic_tracker.ref_srch_modularized.ref_srch_webio.search_references_on_Crossref", mock_query2)
        
    actual_publication_dict, actual_tokenized_citations = build_publication_dict(config_dict, input_tokenized_citations, True, False)
    
    assert expected_pub_dict == actual_publication_dict
    assert expected_tokenized_citations == actual_tokenized_citations
    


def test_build_publication_dict_no_PubMed(config_dict, mocker):
    
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_citations_for_report_test.json"))
    expected_tokenized_citations[1]["pub_dict_key"] = ""
    
    input_tokenized_citations = copy.deepcopy(expected_tokenized_citations)
    for citation in input_tokenized_citations:
        citation["pub_dict_key"] = ""
        
    expected_pub_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_Crossref_pub_dict.json"))
    del expected_pub_dict["https://doi.org/10.3390/metabo10090368"]
    
    def mock_query(*args, **kwargs):
        return {"https://doi.org/10.3390/metabo10090368":expected_pub_dict["https://doi.org/10.3390/metabo10090368"]}, [None, "https://doi.org/10.3390/metabo10090368"]
    mocker.patch("academic_tracker.ref_srch_modularized.ref_srch_webio.search_references_on_PubMed", mock_query)
    
    def mock_query2(*args, **kwargs):
        return {"https://doi.org/10.3390/metabo11030163":expected_pub_dict["https://doi.org/10.3390/metabo11030163"]}, ["https://doi.org/10.3390/metabo11030163", None]
    mocker.patch("academic_tracker.ref_srch_modularized.ref_srch_webio.search_references_on_Crossref", mock_query2)
        
    actual_publication_dict, actual_tokenized_citations = build_publication_dict(config_dict, input_tokenized_citations, False, True)
    
    assert expected_pub_dict == actual_publication_dict
    assert expected_tokenized_citations == actual_tokenized_citations




def test_save_and_send_reports_and_emails_no_email(config_dict):
    
    tokenized_citations = load_json(os.path.join("testing_files", "tokenized_citations_for_report_test.json"))
    pub_dict = load_json(os.path.join("testing_files", "ref_srch_Crossref_pub_dict.json"))
    
    config_dict["summary_report"] = {}
    config_dict["summary_report"]["template"] = read_text_from_txt(os.path.join("testing_files", "ref_srch_report_template_string.txt"))
    
    save_dir = save_and_send_reports_and_emails(config_dict, tokenized_citations, pub_dict, {}, False, False)
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert read_text_from_txt(os.path.join("testing_files", "ref_srch_report_test1.txt")) == read_text_from_txt(os.path.join(save_dir, "summary_report.txt"))
    assert not os.path.exists(os.path.join(save_dir, "emails.json"))



def test_save_and_send_reports_and_emails_with_email(config_dict):
    
    tokenized_citations = load_json(os.path.join("testing_files", "tokenized_citations_for_report_test.json"))
    pub_dict = load_json(os.path.join("testing_files", "ref_srch_Crossref_pub_dict.json"))
    
    config_dict["summary_report"] = {}
    config_dict["summary_report"]["template"] = read_text_from_txt(os.path.join("testing_files", "ref_srch_report_template_string.txt"))
    config_dict["summary_report"]["from_email"] = "ptth222@uky.edu"
    config_dict["summary_report"]["to_email"] = ["ptth222@uky.edu"]
    config_dict["summary_report"]["cc_email"] = ["ptth222@uky.edu"]
    config_dict["summary_report"]["email_body"] = "Body"
    config_dict["summary_report"]["email_subject"] = "Subject"
    
    save_dir = save_and_send_reports_and_emails(config_dict, tokenized_citations, pub_dict, {}, False, True)
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert read_text_from_txt(os.path.join("testing_files", "ref_srch_report_test1.txt")) == read_text_from_txt(os.path.join(save_dir, "summary_report.txt"))
    assert os.path.exists(os.path.join(save_dir, "emails.json"))



def test_save_and_send_reports_and_emails_default_template(config_dict):
    
    tokenized_citations = load_json(os.path.join("testing_files", "tokenized_citations_for_report_test.json"))
    pub_dict = load_json(os.path.join("testing_files", "ref_srch_Crossref_pub_dict.json"))
    
    config_dict["summary_report"] = {}
    
    save_dir = save_and_send_reports_and_emails(config_dict, tokenized_citations, pub_dict, {}, False, False)
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert read_text_from_txt(os.path.join("testing_files", "ref_srch_report_default.txt")) == read_text_from_txt(os.path.join(save_dir, "summary_report.txt"))
    assert not os.path.exists(os.path.join(save_dir, "emails.json"))
    
    
def test_save_and_send_reports_and_emails_tabular(config_dict):
    
    tokenized_citations = load_json(os.path.join("testing_files", "tokenized_citations_for_report_test.json"))
    pub_dict = load_json(os.path.join("testing_files", "ref_srch_Crossref_pub_dict.json"))
    
    config_dict["summary_report"] = {}
    config_dict["summary_report"]["columns"] = {"Col1":"<author_first>"}
    
    save_dir = save_and_send_reports_and_emails(config_dict, tokenized_citations, pub_dict, {}, False, False)
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.csv"))
    assert not os.path.exists(os.path.join(save_dir, "emails.json"))
    
    
def test_save_and_send_reports_and_emails_manual_name(config_dict):
    
    tokenized_citations = load_json(os.path.join("testing_files", "tokenized_citations_for_report_test.json"))
    pub_dict = load_json(os.path.join("testing_files", "ref_srch_Crossref_pub_dict.json"))
    
    config_dict["summary_report"] = {}
    config_dict["summary_report"]["template"] = read_text_from_txt(os.path.join("testing_files", "ref_srch_report_template_string.txt"))
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





