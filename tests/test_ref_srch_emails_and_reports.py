# -*- coding: utf-8 -*-


import os
import time

import pytest
import shutil

from academic_tracker.ref_srch_emails_and_reports import convert_tokenized_authors_to_str, create_report_from_template, create_tokenization_report
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
def tokenized_citations():
    return load_json(os.path.join("testing_files", "tokenized_citations_for_report_test.json"))


def test_convert_tokenized_authors_to_str(tokenized_citations):
    
    expected_string = "Powell C, Moseley H, Travis Thompson"
    
    authors = tokenized_citations[0]["authors"]
    authors.append({"last":"Thompson", "first":"Travis"})
    actual_string = convert_tokenized_authors_to_str(authors)
    
    assert expected_string == actual_string


def test_convert_tokenized_authors_to_str_no_output():
    
    expected_string = str(None)
    
    actual_string = convert_tokenized_authors_to_str([])
    
    assert expected_string == actual_string



@pytest.fixture
def publication_dict():
    return load_json(os.path.join("testing_files", "ref_srch_Crossref_pub_dict.json"))


def test_create_report_from_template_no_comparison(publication_dict, tokenized_citations):
    
    expected_text = read_text_from_txt(os.path.join("testing_files", "ref_srch_report_test1.txt"))
    
    template_string = read_text_from_txt(os.path.join("testing_files", "ref_srch_report_template_string.txt"))
    actual_text = create_report_from_template(publication_dict, [], tokenized_citations, template_string)
    
    assert expected_text == actual_text
    
    
def test_create_report_from_template_no_reference(publication_dict, tokenized_citations):
    
    expected_text = read_text_from_txt(os.path.join("testing_files", "ref_srch_report_test2.txt"))
    
    template_string = read_text_from_txt(os.path.join("testing_files", "ref_srch_report_template_string.txt"))
    for citation in tokenized_citations:
        citation["reference_line"] = ""
    actual_text = create_report_from_template(publication_dict, [True, False], tokenized_citations, template_string)
    
    assert expected_text == actual_text




def test_create_tokenization_report(tokenized_citations):
    
    tokenized_citations.append({"authors":[], "title":"", "DOI":"", "PMID":"", "reference_line":""})
    
    expected_text = read_text_from_txt(os.path.join("testing_files", "tokenization_report.txt"))
    
    actual_text = create_tokenization_report(tokenized_citations)
    
    assert expected_text == actual_text



@pytest.fixture(scope="module", autouse=True)
def cleanup(request):
    """Cleanup a testing directory once we are finished."""
    def remove_test_dir():
        if os.path.exists(TESTING_DIR):
            shutil.rmtree(TESTING_DIR)
    request.addfinalizer(remove_test_dir)
