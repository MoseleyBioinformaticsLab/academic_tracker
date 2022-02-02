# -*- coding: utf-8 -*-


import os
import requests
import copy
import re

import pytest
import shutil

from academic_tracker.athr_srch_modularized import input_reading_and_checking, generate_internal_data_and_check_authors
from academic_tracker.athr_srch_modularized import build_publication_dict, save_and_send_reports_and_emails
from academic_tracker.fileio import load_json, read_text_from_txt


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())



@pytest.fixture
def config_dict():
    return load_json(os.path.join("testing_files", "config_truncated.json"))




def test_input_reading_and_checking(config_dict):
    args = {"<config_json_file>":os.path.join("testing_files", "config_truncated.json"), 
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False}
    
    expected_config_dict = config_dict
    
    actual_config_dict = input_reading_and_checking(args)
    
    assert expected_config_dict == actual_config_dict



def test_generate_internal_data_and_check_authors(config_dict, capsys):
    args = {"--verbose":True}
    
    expected_authors_by_project_dict = load_json(os.path.join("testing_files", "authors_by_project_dict_truncated.json"))
    expected_config_dict = load_json(os.path.join("testing_files", "config_truncated_authors_adjusted.json"))
    
    actual_authors_by_project_dict, actual_config_dict = generate_internal_data_and_check_authors(args, config_dict)
    
    captured = capsys.readouterr()
    
    assert len(captured.out) > 0
    assert expected_authors_by_project_dict == actual_authors_by_project_dict
    assert expected_config_dict == actual_config_dict



def test_build_publication_dict_all_sources(config_dict, mocker):
    args = {"<config_json_file>":os.path.join("testing_files", "config_truncated.json"), 
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False}
        
    expected_pub_dict = load_json(os.path.join("testing_files", "publication_dict_truncated.json"))
    ## Add a fourth entry that is a copy of one of the others just to have a 4th to assign to the 4 different queries.
    expected_pub_dict["32095798"] = expected_pub_dict["32095784"]
    
    def mock_query(*args, **kwargs):
        return {"32095784":expected_pub_dict["32095784"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_PubMed_for_pubs", mock_query)
    
    def mock_query2(*args, **kwargs):
        return {"https://doi.org/10.1002/adhm.202101820":expected_pub_dict["https://doi.org/10.1002/adhm.202101820"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_ORCID_for_pubs", mock_query2)
    
    def mock_query3(*args, **kwargs):
        return {"https://doi.org/10.1002/advs.202101999":expected_pub_dict["https://doi.org/10.1002/advs.202101999"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Crossref_for_pubs", mock_query3)
    
    def mock_query4(*args, **kwargs):
        return {"32095798":expected_pub_dict["32095798"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Google_Scholar_for_pubs", mock_query4)
    
    actual_publication_dict, prev_pubs = build_publication_dict(args, config_dict, {})
    
    assert expected_pub_dict == actual_publication_dict
    assert expected_pub_dict == prev_pubs



def test_build_publication_dict_no_ORCID(config_dict, mocker):
    args = {"<config_json_file>":os.path.join("testing_files", "config_truncated.json"), 
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":True,
            "--no_Crossref":False,
            "--no_GoogleScholar":False}
        
    expected_pub_dict = load_json(os.path.join("testing_files", "publication_dict_truncated.json"))
    ## Add a fourth entry that is a copy of one of the others just to have a 4th to assign to the 4 different queries.
    expected_pub_dict["32095798"] = expected_pub_dict["32095784"]
    del expected_pub_dict["https://doi.org/10.1002/adhm.202101820"]
    
    def mock_query(*args, **kwargs):
        return {"32095784":expected_pub_dict["32095784"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_PubMed_for_pubs", mock_query)
    
    def mock_query2(*args, **kwargs):
        return {"https://doi.org/10.1002/adhm.202101820":expected_pub_dict["https://doi.org/10.1002/adhm.202101820"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_ORCID_for_pubs", mock_query2)
    
    def mock_query3(*args, **kwargs):
        return {"https://doi.org/10.1002/advs.202101999":expected_pub_dict["https://doi.org/10.1002/advs.202101999"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Crossref_for_pubs", mock_query3)
    
    def mock_query4(*args, **kwargs):
        return {"32095798":expected_pub_dict["32095798"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Google_Scholar_for_pubs", mock_query4)
    
    actual_publication_dict, prev_pubs = build_publication_dict(args, config_dict, {})
    
    assert expected_pub_dict == actual_publication_dict
    assert expected_pub_dict == prev_pubs
    


def test_build_publication_dict_no_Crossref(config_dict, mocker):
    args = {"<config_json_file>":os.path.join("testing_files", "config_truncated.json"), 
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":True,
            "--no_GoogleScholar":False}
        
    expected_pub_dict = load_json(os.path.join("testing_files", "publication_dict_truncated.json"))
    ## Add a fourth entry that is a copy of one of the others just to have a 4th to assign to the 4 different queries.
    expected_pub_dict["32095798"] = expected_pub_dict["32095784"]
    del expected_pub_dict["https://doi.org/10.1002/advs.202101999"]
    
    def mock_query(*args, **kwargs):
        return {"32095784":expected_pub_dict["32095784"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_PubMed_for_pubs", mock_query)
    
    def mock_query2(*args, **kwargs):
        return {"https://doi.org/10.1002/adhm.202101820":expected_pub_dict["https://doi.org/10.1002/adhm.202101820"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_ORCID_for_pubs", mock_query2)
    
    def mock_query3(*args, **kwargs):
        return {"https://doi.org/10.1002/advs.202101999":expected_pub_dict["https://doi.org/10.1002/advs.202101999"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Crossref_for_pubs", mock_query3)
    
    def mock_query4(*args, **kwargs):
        return {"32095798":expected_pub_dict["32095798"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Google_Scholar_for_pubs", mock_query4)
    
    actual_publication_dict, prev_pubs = build_publication_dict(args, config_dict, {})
    
    assert expected_pub_dict == actual_publication_dict
    assert expected_pub_dict == prev_pubs
    


def test_build_publication_dict_no_Google_Scholar(config_dict, mocker):
    args = {"<config_json_file>":os.path.join("testing_files", "config_truncated.json"), 
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":True}
        
    expected_pub_dict = load_json(os.path.join("testing_files", "publication_dict_truncated.json"))
    ## Add a fourth entry that is a copy of one of the others just to have a 4th to assign to the 4 different queries.
    expected_pub_dict["32095798"] = expected_pub_dict["32095784"]
    del expected_pub_dict["32095798"]
    
    def mock_query(*args, **kwargs):
        return {"32095784":expected_pub_dict["32095784"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_PubMed_for_pubs", mock_query)
    
    def mock_query2(*args, **kwargs):
        return {"https://doi.org/10.1002/adhm.202101820":expected_pub_dict["https://doi.org/10.1002/adhm.202101820"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_ORCID_for_pubs", mock_query2)
    
    def mock_query3(*args, **kwargs):
        return {"https://doi.org/10.1002/advs.202101999":expected_pub_dict["https://doi.org/10.1002/advs.202101999"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Crossref_for_pubs", mock_query3)
    
    def mock_query4(*args, **kwargs):
        return {"32095798":expected_pub_dict["32095798"]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Google_Scholar_for_pubs", mock_query4)
    
    actual_publication_dict, prev_pubs = build_publication_dict(args, config_dict, {})
    
    assert expected_pub_dict == actual_publication_dict
    assert expected_pub_dict == prev_pubs



def test_build_publication_dict_no_pubs_found(config_dict, mocker, capsys):
    args = {"<config_json_file>":os.path.join("testing_files", "config_truncated.json"), 
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False}
           
    def mock_query(*args, **kwargs):
        return {}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_PubMed_for_pubs", mock_query)
    
    def mock_query2(*args, **kwargs):
        return {}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_ORCID_for_pubs", mock_query2)
    
    def mock_query3(*args, **kwargs):
        return {}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Crossref_for_pubs", mock_query3)
    
    def mock_query4(*args, **kwargs):
        return {}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_webio.search_Google_Scholar_for_pubs", mock_query4)
    
    with pytest.raises(SystemExit):
        actual_publication_dict, prev_pubs = build_publication_dict(args, config_dict, {})
    
    captured = capsys.readouterr()
    expected_message = "No new publications found." + "\n"
    assert expected_message in captured.out
    



def test_save_and_send_reports_and_emails_no_email(config_dict, mocker):
    args = {"--test":True}
    
    def emails(*args, **kwargs):
        return {"creation_date":"asdf", "emails":[]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_emails_and_reports.create_project_reports_and_emails", emails)
    
    pub_dict = load_json(os.path.join("testing_files", "publication_dict_truncated.json"))
    authors_by_project_dict = load_json(os.path.join("testing_files", "authors_by_project_dict_truncated.json"))
    
    config_dict["summary_report"] = {}
    config_dict["summary_report"]["template"] = read_text_from_txt(os.path.join("testing_files", "athr_srch_build_loop_template_string.txt"))
    
    save_dir = save_and_send_reports_and_emails(args, authors_by_project_dict, pub_dict, config_dict)
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert read_text_from_txt(os.path.join("testing_files", "athr_srch_summary_report_custom_template.txt")) == read_text_from_txt(os.path.join(save_dir, "summary_report.txt"))
    assert not os.path.exists(os.path.join(save_dir, "emails.json"))



def test_save_and_send_reports_and_emails_with_email(config_dict, mocker):
    args = {"--test":True}
    
    def emails(*args, **kwargs):
        return {"creation_date":"asdf", "emails":[]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_emails_and_reports.create_project_reports_and_emails", emails)
    
    pub_dict = load_json(os.path.join("testing_files", "publication_dict_truncated.json"))
    authors_by_project_dict = load_json(os.path.join("testing_files", "authors_by_project_dict_truncated.json"))
    
    config_dict["summary_report"] = {}
    config_dict["summary_report"]["template"] = read_text_from_txt(os.path.join("testing_files", "athr_srch_build_loop_template_string.txt"))
    config_dict["summary_report"]["from_email"] = "ptth222@uky.edu"
    config_dict["summary_report"]["to_email"] = ["ptth222@uky.edu"]
    config_dict["summary_report"]["cc_email"] = ["ptth222@uky.edu"]
    config_dict["summary_report"]["email_body"] = "Body"
    config_dict["summary_report"]["email_subject"] = "Subject"
    
    save_dir = save_and_send_reports_and_emails(args, authors_by_project_dict, pub_dict, config_dict)
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert read_text_from_txt(os.path.join("testing_files", "athr_srch_summary_report_custom_template.txt")) == read_text_from_txt(os.path.join(save_dir, "summary_report.txt"))
    assert os.path.exists(os.path.join(save_dir, "emails.json"))



def test_save_and_send_reports_and_emails_default_template(config_dict, mocker):
    args = {"--test":True}
    
    def emails(*args, **kwargs):
        return {"creation_date":"asdf", "emails":[]}
    mocker.patch("academic_tracker.athr_srch_modularized.athr_srch_emails_and_reports.create_project_reports_and_emails", emails)
    
    pub_dict = load_json(os.path.join("testing_files", "publication_dict_truncated.json"))
    authors_by_project_dict = load_json(os.path.join("testing_files", "authors_by_project_dict_truncated.json"))
    
    config_dict["summary_report"] = {}
    
    save_dir = save_and_send_reports_and_emails(args, authors_by_project_dict, pub_dict, config_dict)
    
    assert os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert read_text_from_txt(os.path.join("testing_files", "athr_srch_summary_report.txt")) == read_text_from_txt(os.path.join(save_dir, "summary_report.txt"))
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