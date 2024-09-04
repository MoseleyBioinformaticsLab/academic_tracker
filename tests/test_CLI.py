# -*- coding: utf-8 -*-
import pytest

import pathlib
import os
import requests
import time
import json
import subprocess
import re

import shutil


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())


@pytest.fixture(scope="module", autouse=True)
def change_cwd():
    cwd = pathlib.Path.cwd()
    os.chdir(pathlib.Path("tests", "testing_files"))
    yield
    os.chdir(cwd)

@pytest.fixture(autouse=True)
def delete_folder(request):
    def delete_tracker_dir():
        paths = [os.path.abspath(name) for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
        for path in paths:
            path = pathlib.Path(path)
            shutil.rmtree(path)
            time_to_wait=10
            time_counter = 0
            while path.exists():
                time.sleep(1)
                time_counter += 1
                if time_counter > time_to_wait:
                    raise FileExistsError(path + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    delete_tracker_dir()
    request.addfinalizer(delete_tracker_dir)
    



def test_no_source_hyphens_author_search():
    """Test that the hyphen version of the no_source options work for author_search."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker author_search ./" + test_file  + " --no-PubMed --no-Crossref --no-ORCID --no-GoogleScholar" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert not [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "No new publications found." in output


def test_no_source_underscores_author_search():
    """Test that the underscore version of the no_source options work for author_search."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker author_search ./" + test_file  + " --no_PubMed --no_Crossref --no_ORCID --no_GoogleScholar" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert not [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "No new publications found." in output


def test_prev_pub_hyphen_author_search():
    """Test that the hyphen version of the prev_pub option works for author_search."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker author_search ./" + test_file  + " --no-PubMed --no-Crossref --no-ORCID --no-GoogleScholar --prev-pub publication_dict_truncated.json" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert not [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "No new publications found." in output
    

def test_prev_pub_underscore_author_search():
    """Test that the underscore version of the prev_pub option works for author_search."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker author_search ./" + test_file  + " --no-PubMed --no-Crossref --no-ORCID --no-GoogleScholar --prev_pub publication_dict_truncated.json" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert not [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "No new publications found." in output


def test_no_source_hyphen_ref_search():
    """Test that the hyphen version of the no_source options work for reference_search."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker reference_search ./" + test_file  + " tokenized_citations_duplicates_removed.json --no-PubMed --no-Crossref" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "Success" in output


def test_no_source_underscore_ref_search():
    """Test that the underscore version of the no_source options work for reference_search."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker reference_search ./" + test_file  + " tokenized_citations_duplicates_removed.json --no_PubMed --no_Crossref" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "Success" in output


def test_prev_pub_hyphen_ref_search():
    """Test that the hyphen version of the prev_pub option works for reference_search."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker reference_search ./" + test_file  + " tokenized_citations_duplicates_removed.json --no-PubMed --no-Crossref --prev-pub publication_dict_truncated.json" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "Success" in output


def test_prev_pub_underscore_ref_search():
    """Test that the underscore version of the prev_pub option works for reference_search."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker reference_search ./" + test_file  + " tokenized_citations_duplicates_removed.json --no-PubMed --no-Crossref --prev_pub publication_dict_truncated.json" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "Success" in output


def test_pmid_reference_hyphen_ref_search():
    """Test that the hyphen version of the PMID_reference option works for reference_search."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker reference_search ./" + test_file  + " PMID_reference.json --no-PubMed --no-Crossref --PMID-reference" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "Success" in output


def test_pmid_reference_underscore_ref_search():
    """Test that the underscore version of the PMID_reference option works for reference_search."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker reference_search ./" + test_file  + " PMID_reference.json --no-PubMed --no-Crossref --PMID_reference" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout
    
    assert [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "Success" in output


def test_medline_reference_hyphen_ref_search():
    """Test that the hyphen version of the MEDLINE_reference option works for reference_search."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker reference_search ./" + test_file  + " tokenized_MEDLINE2.json --no-PubMed --no-Crossref --MEDLINE-reference" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "Success" in output


def test_medline_reference_underscore_ref_search():
    """Test that the underscore version of the MEDLINE_reference option works for reference_search."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker reference_search ./" + test_file  + " tokenized_MEDLINE2.json --no-PubMed --no-Crossref --MEDLINE_reference" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "Success" in output


def test_medline_reference_hyphen_tokenize_ref():
    """Test that the hyphen version of the MEDLINE_reference option works for tokenize_reference."""
        
    command = "academic_tracker tokenize_reference tokenized_MEDLINE2.json --MEDLINE-reference" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "Success" in output


def test_medline_reference_underscore_tokenize_ref():
    """Test that the underscore version of the MEDLINE_reference option works for tokenize_reference."""
        
    command = "academic_tracker tokenize_reference tokenized_MEDLINE2.json --MEDLINE_reference" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "Success" in output


def test_medline_reference_hyphen_gen_reports_emails_ref():
    """Test that the hyphen version of the MEDLINE_reference option works for gen_reports_and_emails_ref."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker gen_reports_and_emails_ref ./" + test_file  + " tokenized_MEDLINE2.json publication_dict.json --MEDLINE-reference" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "Success" in output


def test_medline_reference_underscore_gen_reports_emails_ref():
    """Test that the underscore version of the MEDLINE_reference option works for gen_reports_and_emails_ref."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker gen_reports_and_emails_ref ./" + test_file  + " tokenized_MEDLINE2.json publication_dict.json --MEDLINE_reference" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "Success" in output


def test_prev_pub_hyphen_gen_reports_emails_ref():
    """Test that the hyphen version of the prev_pub option works for gen_reports_and_emails_ref."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker gen_reports_and_emails_ref ./" + test_file  + " tokenized_MEDLINE2.json publication_dict.json --prev-pub publication_dict_truncated.json --MEDLINE-reference" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "Success" in output


def test_prev_pub_underscore_gen_reports_emails_ref():
    """Test that the underscore version of the prev_pub option works for gen_reports_and_emails_ref."""
    
    test_file = "config_truncated.json"
    
    command = "academic_tracker gen_reports_and_emails_ref ./" + test_file  + " tokenized_MEDLINE2.json publication_dict.json --prev_pub publication_dict_truncated.json --MEDLINE-reference" 
    command = command.split(" ")
    subp = subprocess.run(command, capture_output=True, encoding="UTF-8")
    output = subp.stdout

    assert [name for name in os.listdir(".") if os.path.isdir(name) and re.match(r"tracker-.*", name)]
                
    assert "Success" in output


    
