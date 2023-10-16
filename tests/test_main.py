# -*- coding: utf-8 -*-

import os
import requests
import copy
import json
import re

import pytest
import shutil

from academic_tracker.__main__ import main, author_search, reference_search, PMID_reference
from academic_tracker.__main__ import find_ORCID, find_Google_Scholar, add_authors
from academic_tracker.__main__ import tokenize_reference, gen_reports_and_emails_auth, gen_reports_and_emails_ref
from academic_tracker.fileio import load_json, read_text_from_txt


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())





@pytest.mark.parametrize("func_name, options", [
        
        ("author_search", ["file_path"]),
        ("reference_search", ["file_path1", "file_path2"]),
        ("find_ORCID", ["file_path"]),
        ("find_Google_Scholar", ["file_path"]),
        ("add_authors", ["file_path1", "file_path2"]),
        ("tokenize_reference", ["file_path"]),
        ("gen_reports_and_emails_auth", ["file_path1", "file_path2"]),
        ("gen_reports_and_emails_ref", ["file_path1", "file_path2", "file_path3"]),
        ])



def test_main(func_name, options, mocker, capsys):
    mocker.patch("__main__.sys.argv", ["academic_tracker", func_name] + options)
    
    def mock_call(*args, **kwargs):
        print("Call Successful")
    mocker.patch("academic_tracker.__main__." + func_name, mock_call)
    
    main()
    
    captured = capsys.readouterr()
    assert captured.out == "Call Successful" + "\n"
    


def test_main_PMID_reference(mocker, capsys):
    mocker.patch("__main__.sys.argv", ["academic_tracker", "reference_search", "file_path1", "file_path2", "--PMID_reference"])
    
    def mock_call(*args, **kwargs):
        print("Call Successful")
    mocker.patch("academic_tracker.__main__.PMID_reference" , mock_call)
    
    main()
    
    captured = capsys.readouterr()
    assert captured.out == "Call Successful" + "\n"




def test_author_search(mocker, capsys):
    def mock_call(*args, **kwargs):
        publication_dict = load_json(os.path.join("tests", "testing_files", "publication_dict_truncated.json"))
        return publication_dict, {}
    mocker.patch("academic_tracker.__main__.athr_srch_modularized.build_publication_dict", mock_call)
    
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated.json"), 
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--no_PubMed":False,
            "--test":True,
            "--save-all-queries":True}
    
    author_search(args["<config_json_file>"], args["--no_ORCID"], 
                      args["--no_GoogleScholar"], args["--no_Crossref"], 
                      args["--no_PubMed"],
                      args["--test"], args["--prev_pub"],
                      args["--save-all-queries"])
    
    captured = capsys.readouterr()
    save_dir = captured.out.strip().split(" ")[-1]
    
    assert not os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert os.path.exists(os.path.join(save_dir, "emails.json"))
    assert os.path.exists(os.path.join(save_dir, "publications.json"))
    assert os.path.exists(os.path.join(save_dir, "all_results.json"))



def test_reference_search(mocker, capsys):
    def mock_call(*args, **kwargs):
        publication_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_Crossref_pub_dict.json"))
        tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_citations_for_report_test.json"))
        return publication_dict, tokenized_citations, {}
    mocker.patch("academic_tracker.__main__.ref_srch_modularized.build_publication_dict", mock_call)
    
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated.json"),
            "<references_file_or_URL>":os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json"),
            "--MEDLINE_reference":False,
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--no_PubMed":False,
            "--test":True,
            "--save-all-queries":True,
            "--keep-duplicates":False}
    
    reference_search(args["<config_json_file>"], args["<references_file_or_URL>"], 
                              args["--MEDLINE_reference"], args["--no_Crossref"], 
                              args["--no_PubMed"],
                              args["--test"], args["--prev_pub"],
                              args["--save-all-queries"],
                              not args["--keep-duplicates"])
    
    captured = capsys.readouterr()
    save_dir = captured.out.strip().split(" ")[-1]
    
    assert not os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert not os.path.exists(os.path.join(save_dir, "emails.json"))
    assert os.path.exists(os.path.join(save_dir, "publications.json"))
    assert os.path.exists(os.path.join(save_dir, "all_results.json"))



@pytest.mark.parametrize("reference_file", [
        
        ("PMID_reference.json"),
        ("PMID_reference.docx"),
        ("PMID_reference.txt"),
        ])



def test_PMID_reference(reference_file, mocker, capsys):
    def mock_call(*args, **kwargs):
        publication_dict = load_json(os.path.join("tests", "testing_files", "publication_dict_truncated.json"))
        publication_dict["32095784"] = publication_dict["https://doi.org/10.1038/s41597-023-02277-x"]
        publication_dict["34811960"] = publication_dict["https://aacrjournals.org/cancerres/article/83/7_Supplement/3673/719740"]
        publication_dict["34622577"] = publication_dict["https://doi.org/10.1002/hep.32467"]
        del publication_dict["https://aacrjournals.org/cancerres/article/83/7_Supplement/3673/719740"]
        del publication_dict["https://doi.org/10.1002/hep.32467"]
        del publication_dict["https://doi.org/10.1038/s41597-023-02277-x"]
        return publication_dict
    mocker.patch("academic_tracker.__main__.ref_srch_webio.build_pub_dict_from_PMID", mock_call)
    
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated.json"),
            "<references_file_or_URL>":os.path.join("tests", "testing_files", reference_file),
            "--MEDLINE_reference":False,
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--test":True}
    
    PMID_reference(args["<config_json_file>"], args["<references_file_or_URL>"], args["--test"])
    
    captured = capsys.readouterr()
    save_dir = captured.out.strip().split(" ")[-1]
    
    assert os.path.exists(os.path.join(save_dir, "publications.json"))
    
    


@pytest.mark.parametrize("error_file, error_message", [
        
        ("PMID_reference.asdf", "Unknown file type for PMID file."),
        ("empty_file.txt", "Nothing was read from the PMID file. Make sure the file is not empty or is a supported file type."),
        ])


def test_PMID_reference_errors(error_file, error_message, mocker, capsys):
    def mock_call(*args, **kwargs):
        publication_dict = load_json(os.path.join("tests", "testing_files", "publication_dict_truncated.json"))
        publication_dict["32095784"] = publication_dict["https://doi.org/10.1038/s41597-023-02277-x"]
        publication_dict["34811960"] = publication_dict["https://aacrjournals.org/cancerres/article/83/7_Supplement/3673/719740"]
        publication_dict["34622577"] = publication_dict["https://doi.org/10.1002/hep.32467"]
        del publication_dict["https://aacrjournals.org/cancerres/article/83/7_Supplement/3673/719740"]
        del publication_dict["https://doi.org/10.1002/hep.32467"]
        del publication_dict["https://doi.org/10.1038/s41597-023-02277-x"]
        return publication_dict
    mocker.patch("academic_tracker.__main__.ref_srch_webio.build_pub_dict_from_PMID", mock_call)
    
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated.json"),
            "<references_file_or_URL>":os.path.join("tests", "testing_files", error_file),
            "--MEDLINE_reference":False,
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--test":True}
    
    with pytest.raises(SystemExit):
        PMID_reference(args["<config_json_file>"], args["<references_file_or_URL>"], args["--test"])
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
    


def test_find_ORCID(mocker, capsys):
    def mock_call(*args, **kwargs):
        config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated.json"))
        return config_dict["Authors"]
    mocker.patch("academic_tracker.__main__.webio.search_ORCID_for_ids", mock_call)
    
    def mock_config(*args, **kwargs):
        config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated.json"))
        del config_dict["Authors"]["Andrew Morris"]["ORCID"]
        return config_dict
    mocker.patch("academic_tracker.__main__.fileio.load_json", mock_config)
    
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated.json"),
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--test":True}
    
    find_ORCID(args["<config_json_file>"])
    
    captured = capsys.readouterr()
    save_dir = captured.out.strip().split(" ")[-1]
    
    assert os.path.exists(os.path.join(save_dir, "configuration.json"))
    


def test_find_ORCID_no_new(mocker, capsys):
    def mock_call(*args, **kwargs):
        config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated.json"))
        return config_dict["Authors"]
    mocker.patch("academic_tracker.__main__.webio.search_ORCID_for_ids", mock_call)
        
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated.json"),
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--test":True}
    
    find_ORCID(args["<config_json_file>"])
    
    captured = capsys.readouterr()
    
    assert captured.out.split("\n")[-2] == "No authors were matched from the ORCID results. No new file saved."
    
   

def test_find_Google_Scholar(mocker, capsys):
    def mock_call(*args, **kwargs):
        config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated.json"))
        return config_dict["Authors"]
    mocker.patch("academic_tracker.__main__.webio.search_Google_Scholar_for_ids", mock_call)
    
    def mock_config(*args, **kwargs):
        config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated.json"))
        del config_dict["Authors"]["Andrew Morris"]["scholar_id"]
        return config_dict
    mocker.patch("academic_tracker.__main__.fileio.load_json", mock_config)
    
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated.json"),
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--test":True}
    
    find_Google_Scholar(args["<config_json_file>"])
    
    captured = capsys.readouterr()
    save_dir = captured.out.strip().split(" ")[-1]
    
    assert os.path.exists(os.path.join(save_dir, "configuration.json"))
    


def test_find_Google_Scholar_no_new(mocker, capsys):
    def mock_call(*args, **kwargs):
        config_dict = load_json(os.path.join("tests", "testing_files", "config_truncated.json"))
        return config_dict["Authors"]
    mocker.patch("academic_tracker.__main__.webio.search_Google_Scholar_for_ids", mock_call)
        
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated.json"),
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--test":True}
    
    find_Google_Scholar(args["<config_json_file>"])
    
    captured = capsys.readouterr()
    
    assert captured.out.split("\n")[-2] == "No authors were matched from the Google Scholar results. No new file saved."
    
    

def test_add_authors(capsys):
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated.json"),
            "<authors_file>":os.path.join("tests", "testing_files", "add_authors.csv"),
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--test":True}
    
    expected_config = load_json(os.path.join("tests", "testing_files", "config_truncated.json"))
    expected_config["Authors"]["Name McNamerson"] = {"first_name":"Name",
                                                      "last_name":"McNamerson",
                                                      "pubmed_name_search":"Name McNamerson",
                                                      "email":"ptth222@uky.edu",
                                                      "affiliations":["kentucky","asdf","qwr"]}
    
    add_authors(args["<config_json_file>"], args["<authors_file>"])
    
    captured = capsys.readouterr()
    save_dir = captured.out.strip().split(" ")[-1]
        
    assert expected_config == load_json(os.path.join(save_dir, "configuration.json"))
    


@pytest.mark.parametrize("error_file, error_message", [
        
        ("empty_file.txt", "Unknown file type for author file."),
        ("add_authors_missing_column.csv", "Error: The following columns are required but are missing:\npubmed_name_search"),
        ("add_authors_missing_value.csv", "Error: The following columns have null values:\npubmed_name_search"),
        ("add_authors_missing_all_names.csv", "Error: The following rows have incomplete name columns:\n3\nEach row must have values in either the 'collective_name' column or the 'first_name' and 'last_name' columns."),
        ("add_authors_missing_last_name_column.csv", "Error: There is a 'first_name' column without a matching 'last_name' column."),
        ("add_authors_missing_first_name_column.csv", "Error: There is a 'last_name' column without a matching 'first_name' column."),
        ("add_authors_missing_all_name_columns.csv", "Error: There must be either a 'collective_name' column or 'first_name' and 'last_name' columns."),
        ("add_authors_missing_first_and_last_names.csv", "Error: The following rows have incomplete name columns:\n2\nEach row must have values in either the 'collective_name' column or the 'first_name' and 'last_name' columns."),
        ("add_authors_missing_collective_name.csv", "Error: The following rows have incomplete name columns:\n1\nEach row must have values in either the 'collective_name' column or the 'first_name' and 'last_name' columns."),
        ])


def test_add_authors_errors(error_file, error_message, capsys):
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated.json"),
            "<authors_file>":os.path.join("tests", "testing_files", error_file),
            "--verbose":True,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--test":True}
    
    expected_config = load_json(os.path.join("tests", "testing_files", "config_truncated.json"))
    expected_config["Authors"]["Name McNamerson"] = {"first_name":"Name",
                                                      "last_name":"McNamerson",
                                                      "pubmed_name_search":"Name McNamerson",
                                                      "email":"ptth222@uky.edu",
                                                      "affiliations":["kentucky","asdf","qwr"]}
    
    with pytest.raises(SystemExit):
        add_authors(args["<config_json_file>"], args["<authors_file>"])
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"




def test_tokenize_reference(mocker, capsys):
    def mock_call(*args, **kwargs):
        tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_citations_for_report_test.json"))
        tokenized_citations.append({"authors":[], "title":"", "DOI":"", "PMID":"", "reference_line":""})
        return tokenized_citations
    mocker.patch("academic_tracker.__main__.ref_srch_webio.tokenize_reference_input", mock_call)
    
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated.json"),
            "<references_file_or_URL>":os.path.join("tests", "testing_files", "tokenized_citations_for_report_test.json"),
            "--verbose":True,
            "--MEDLINE_reference":False,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--test":True,
            "--keep-duplicates":False}
    
    expected_text = read_text_from_txt(os.path.join("tests", "testing_files", "tokenization_report.txt"))
    
    tokenize_reference(args["<references_file_or_URL>"], args["--MEDLINE_reference"], not args["--keep-duplicates"])
    
    captured = capsys.readouterr()
    save_dir = captured.out.strip().split(" ")[-1]
    
    assert expected_text == read_text_from_txt(os.path.join(save_dir, "tokenization_report.txt"))




def test_gen_reports_and_emails_auth(capsys):
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated.json"),
            "<publication_json_file>":os.path.join("tests", "testing_files", "publication_dict_truncated.json"),
            "--verbose":True,
            "--MEDLINE_reference":False,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--test":True}
    
    gen_reports_and_emails_auth(args["<config_json_file>"], args["<publication_json_file>"], args["--test"])
    
    captured = capsys.readouterr()
    save_dir = captured.out.strip().split(" ")[-1]
    
    assert os.path.exists(os.path.join(save_dir, "emails.json"))
    ## Should be emails.json and project reports.
    assert len(os.listdir()) > 3
    



def test_gen_reports_and_emails_ref(mocker, capsys):
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated_ref_srch_summary_report.json"),
            "<publication_json_file>":os.path.join("tests", "testing_files", "ref_srch_Crossref_pub_dict.json"),
            "<references_file_or_URL>":os.path.join("tests", "testing_files", "tokenized_citations_for_report_test.json"),
            "--verbose":True,
            "--MEDLINE_reference":False,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--test":True,
            "--keep-duplicates":False}
    
    gen_reports_and_emails_ref(args["<config_json_file>"], args["<references_file_or_URL>"], 
                                    args["<publication_json_file>"], args["--MEDLINE_reference"], 
                                    args["--test"], args["--prev_pub"], not args["--keep-duplicates"])
    
    captured = capsys.readouterr()
    save_dir = captured.out.strip().split(" ")[-1]
    
    assert not os.path.exists(os.path.join(save_dir, "emails.json"))
    assert os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    
    

def test_gen_reports_and_emails_ref_no_pub_dict_keys(mocker, capsys):    
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated_ref_srch_summary_report.json"),
            "<publication_json_file>":os.path.join("tests", "testing_files", "ref_srch_gen_reports_test_pub_dict.json"),
            "<references_file_or_URL>":os.path.join("tests", "testing_files", "tokenized_citations_for_report_test2.json"),
            "--verbose":True,
            "--MEDLINE_reference":False,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--test":True,
            "--keep-duplicates":True}
    
    expected_report = read_text_from_txt(os.path.join("tests", "testing_files", "gen_reports_ref_summary_report.txt"))
    
    gen_reports_and_emails_ref(args["<config_json_file>"], args["<references_file_or_URL>"], 
                                    args["<publication_json_file>"], args["--MEDLINE_reference"], 
                                    args["--test"], args["--prev_pub"], not args["--keep-duplicates"])
    
    captured = capsys.readouterr()
    save_dir = captured.out.strip().split(" ")[-1]
    # with open(os.path.join("tests", "testing_files", "gen_reports_ref_summary_report_new.txt"), 'wb') as outFile:
    #     outFile.write(read_text_from_txt(os.path.join(save_dir, "summary_report.txt")).encode("utf-8"))
    
    assert not os.path.exists(os.path.join(save_dir, "emails.json"))
    assert os.path.exists(os.path.join(save_dir, "summary_report.txt"))
    assert expected_report == read_text_from_txt(os.path.join(save_dir, "summary_report.txt"))
    
    

def test_gen_reports_and_emails_ref_no_matches(mocker, capsys):       
    args = {"<config_json_file>":os.path.join("tests", "testing_files", "config_truncated_ref_srch_summary_report.json"),
            "<publication_json_file>":os.path.join("tests", "testing_files", "ref_srch_Crossref_pub_dict.json"),
            "<references_file_or_URL>":os.path.join("tests", "testing_files", "tokenized_citations_for_report_test_empty.json"),
            "--verbose":True,
            "--MEDLINE_reference":False,
            "--prev_pub":"ignore",
            "--no_ORCID":False,
            "--no_Crossref":False,
            "--no_GoogleScholar":False,
            "--test":True,
            "--keep-duplicates":False}
    
    with pytest.raises(SystemExit):    
        gen_reports_and_emails_ref(args["<config_json_file>"], args["<references_file_or_URL>"], 
                                    args["<publication_json_file>"], args["--MEDLINE_reference"], 
                                    args["--test"], args["--prev_pub"], not args["--keep-duplicates"])
    
    captured = capsys.readouterr()
    assert captured.out == "Error: No entries in the publication JSON matched any reference in the provided reference." + "\n"
    
    




@pytest.fixture(autouse=True)
def cleanup(request):
    """Cleanup a testing directory once we are finished."""
    def remove_test_dir():
        dir_contents = os.listdir()
        tracker_dirs = [folder for folder in dir_contents if re.match(r"tracker-(\d{10})", folder) or re.match(r"tracker-test-(\d{10})", folder)]
        for directory in tracker_dirs:
            shutil.rmtree(directory)
    request.addfinalizer(remove_test_dir)