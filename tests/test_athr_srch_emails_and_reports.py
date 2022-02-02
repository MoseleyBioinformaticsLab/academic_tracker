# -*- coding: utf-8 -*-


import os
import time

import pytest
import shutil

from academic_tracker.athr_srch_emails_and_reports import create_pubs_by_author_dict, create_project_reports_and_emails, create_project_report
from academic_tracker.athr_srch_emails_and_reports import create_summary_report, build_author_loop
from academic_tracker.fileio import load_json, read_text_from_txt


TESTING_DIR = "test_dir"
@pytest.fixture(scope="module", autouse=True)
def test_email_dir():
    save_dir_name = TESTING_DIR
    os.mkdir(save_dir_name)
    time_to_wait = 10
    time_counter = 0
    
    while not os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(save_dir_name + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")



@pytest.fixture
def publication_dict():
    return load_json(os.path.join("testing_files", "publication_dict_truncated.json"))


def test_create_pubs_by_author_dict(publication_dict):
    expected = load_json(os.path.join("testing_files", "pubs_by_author_dict_truncated.json"))
    
    actual = create_pubs_by_author_dict(publication_dict)
    
    assert expected == actual



@pytest.fixture
def config_dict():
    return load_json(os.path.join("testing_files", "config_truncated.json"))


@pytest.fixture
def authors_by_project_dict():
    return load_json(os.path.join("testing_files", "authors_by_project_dict_truncated.json"))


def test_create_project_reports_and_emails(publication_dict, config_dict, authors_by_project_dict):
    
    expected_emails = load_json(os.path.join("testing_files", "athr_project_emails.json"))
    del expected_emails["creation_date"]
    
    actual_emails = create_project_reports_and_emails(authors_by_project_dict, publication_dict, config_dict, TESTING_DIR)
    del actual_emails["creation_date"]
    
    dir_contents = os.listdir(TESTING_DIR)
    expected_num_of_project_reports = 13
    actual_num_of_project_reports = len(dir_contents)
    
    assert expected_emails == actual_emails
    assert actual_num_of_project_reports == expected_num_of_project_reports
        



def test_create_project_report(publication_dict, config_dict, authors_by_project_dict):
    
    template_string = "<author_loop><author_first> <author_last>:\n<pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>"
    author_first = "Kelly"
    author_last = "Pennell"
    
    expected_text = read_text_from_txt(os.path.join("testing_files", "project_report.txt"))
    
    actual_text = create_project_report(publication_dict, config_dict, authors_by_project_dict, "Core A Administrative Core", template_string, author_first, author_last)
    
    assert expected_text == actual_text



def test_create_summary_report(publication_dict, config_dict, authors_by_project_dict):
    
    expected_text = read_text_from_txt(os.path.join("testing_files", "athr_srch_summary_report.txt"))
    
    actual_text = create_summary_report(publication_dict, config_dict, authors_by_project_dict)
    
    assert expected_text == actual_text



def test_build_author_loop(publication_dict, config_dict, authors_by_project_dict):
    
    template_string = read_text_from_txt(os.path.join("testing_files", "athr_srch_build_loop_template_string.txt"))
                         
    expected_text = read_text_from_txt(os.path.join("testing_files", "athr_srch_build_author_loop.txt"))
    
    actual_text = build_author_loop(publication_dict, config_dict, authors_by_project_dict, "No from_email", template_string)
    
    assert expected_text == actual_text






@pytest.fixture(scope="module", autouse=True)
def cleanup(request):
    """Cleanup a testing directory once we are finished."""
    def remove_test_dir():
        if os.path.exists(TESTING_DIR):
            shutil.rmtree(TESTING_DIR)
    request.addfinalizer(remove_test_dir)

