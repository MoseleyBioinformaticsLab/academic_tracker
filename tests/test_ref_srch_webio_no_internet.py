# -*- coding: utf-8 -*-

import os
import json

import pytest
import pymed
import pickle
import requests
import xml.etree.ElementTree as ET

from academic_tracker.ref_srch_webio import build_pub_dict_from_PMID, search_references_on_PubMed, search_references_on_Crossref
from academic_tracker.ref_srch_webio import parse_myncbi_citations, tokenize_reference_input
from academic_tracker.fileio import load_json, read_text_from_txt



@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())


## pymed's PubMed.query() actually returns an itertools.chain where the elements are actually the _getArticles method of PubMed, not the articles directly.
## Each call to the iterator does an http request. Here I simply put the articles in a list. 
@pytest.fixture
def pymed_query():
    with open(os.path.join("tests", "testing_files", "pymed_pubs.pkl"), "rb") as f:
        articles = pickle.load(f)
    return articles




def test_build_pub_dict_from_PMID(pymed_query, mocker):
    def mock_query(*args, **kwargs):
        return pymed_query
    mocker.patch("academic_tracker.ref_srch_webio.pymed.PubMed.query", mock_query)
    test_publication_dict = build_pub_dict_from_PMID(['34352431', '11111111'], "ptth222@uky.edu")
    expected_publication_dict = load_json(os.path.join("tests", "testing_files", "pub_dict_from_PMID.json"))
    # with open(os.path.join("tests", "testing_files", "pub_dict_from_PMID_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(test_publication_dict, indent=2, sort_keys=True))
    assert test_publication_dict == expected_publication_dict



## For whatever reason I couldn't pickle a list of pymed articles like I did before, 
## so I saved them as a string. Here they are loaded back in and converted to an article.
@pytest.fixture
def ref_pymed_query():
    xml_strings = load_json(os.path.join("tests", "testing_files", "ref_srch_PubMed_pubs.json"))
    return [pymed.article.PubMedArticle(xml_element=ET.fromstring(string)) for string in xml_strings]


@pytest.fixture
def tokenized_citations():
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_citations.json"))
    return [tokenized_citations[i] for i in [6,8,63]]
    


def test_search_references_on_PubMed(tokenized_citations, ref_pymed_query, mocker):
    def mock_query(*args, **kwargs):
        return ref_pymed_query
    mocker.patch("academic_tracker.ref_srch_webio.pymed.PubMed.query", mock_query)
    
    expected_publication_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_publication_dict.json"))
    expected_citation_keys = load_json(os.path.join("tests", "testing_files", "ref_srch_keys_for_citations.json"))
    
    actual_publication_dict, actual_citation_keys, all_pubs = search_references_on_PubMed({}, tokenized_citations, "ptth222@uky.edu")
    # with open(os.path.join("tests", "testing_files", "ref_srch_publication_dict_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "ref_srch_keys_for_citations_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_citation_keys, indent=2, sort_keys=True))
    
    assert expected_publication_dict == actual_publication_dict
    assert expected_citation_keys == actual_citation_keys
    



def test_search_references_on_Crossref(tokenized_citations, mocker):
    def query_generator():
        queries = load_json(os.path.join("tests", "testing_files", "ref_srch_Crossref_queries.json"))
        for query in queries:
            yield query
            
    queries = query_generator()
        
    def mock_query(*args, **kwargs):
        return next(queries)
    mocker.patch("academic_tracker.ref_srch_webio.habanero.Crossref.works", mock_query)
       
    expected_pub_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_Crossref_pub_dict.json"))
    expected_citation_keys = load_json(os.path.join("tests", "testing_files", "ref_srch_Crossref_keys_for_citations.json"))
    
    actual_pub_dict, actual_citation_keys, all_pubs = search_references_on_Crossref({}, tokenized_citations, "ptth222@uky.edu")
    # with open(os.path.join("tests", "testing_files", "ref_srch_Crossref_pub_dict_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_pub_dict, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "ref_srch_Crossref_keys_for_citations_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_citation_keys, indent=2, sort_keys=True))
        
    assert actual_pub_dict == expected_pub_dict
    assert actual_citation_keys == expected_citation_keys




def test_parse_myncbi_citations(mocker):
    def page_generator():
        pages = load_json(os.path.join("tests", "testing_files", "myncbi_webpages.json"))
        for page in pages:
            yield page
            
    pages = page_generator()
        
    def mock_query(*args, **kwargs):
        return next(pages)
    mocker.patch("academic_tracker.ref_srch_webio.webio.get_url_contents_as_str", mock_query)
    
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_citations.json"))
    
    actual_tokenized_citations = parse_myncbi_citations("asdf")
    # with open(os.path.join("tests", "testing_files", "tokenized_citations_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_tokenized_citations, indent=2, sort_keys=True))
    
    assert expected_tokenized_citations == actual_tokenized_citations



## Test that the JSON read in works and finds and eliminates duplicates.
def test_tokenize_reference_input_JSON(capsys):
    
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json"))
    
    actual_tokenized_citations = tokenize_reference_input(os.path.join("tests", "testing_files", "tokenized_citations.json"), False)
    captured = capsys.readouterr()
    # with open(os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_tokenized_citations, indent=2, sort_keys=True))
    
    assert expected_tokenized_citations == actual_tokenized_citations
    ## There should be something about duplicates in stdout.
    assert len(captured.out) > 0



def test_tokenize_reference_input_html(mocker):
    def mock_query(*args, **kwargs):
        return read_text_from_txt(os.path.join("tests", "testing_files", "nsf_award_page.txt"))
    mocker.patch("academic_tracker.ref_srch_webio.webio.clean_tags_from_url", mock_query)
    
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_nsf_award_page.json"))
    
    actual_tokenized_citations = tokenize_reference_input("https://www.nsf.gov/awardsearch/showAward?AWD_ID=1419282", False)
    # with open(os.path.join("tests", "testing_files", "tokenized_nsf_award_page_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_tokenized_citations, indent=2, sort_keys=True))
    
    assert expected_tokenized_citations == actual_tokenized_citations



def test_tokenize_reference_input_no_html_content(capsys, mocker):
    def mock_query(*args, **kwargs):
        return read_text_from_txt(os.path.join("tests", "testing_files", "empty_file.txt"))
    mocker.patch("academic_tracker.ref_srch_webio.webio.clean_tags_from_url", mock_query)
    
    with pytest.raises(SystemExit):
        tokenize_reference_input("https://www.nsf.gov/awardsearch/showAward?AWD_ID=1419282", False)
    captured = capsys.readouterr()
    
    assert captured.out == "Nothing was read from the URL. Make sure the address is correct.\n"



def test_tokenize_reference_input_docx():
    
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_ref_test.json"))
    
    actual_tokenized_citations = tokenize_reference_input(os.path.join("tests", "testing_files", "reference_test.docx"), False)
    
    assert expected_tokenized_citations == actual_tokenized_citations



def test_tokenize_reference_input_txt():
    
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_ref_test.json"))
    
    actual_tokenized_citations = tokenize_reference_input(os.path.join("tests", "testing_files", "reference_test.txt"), False)
    
    assert expected_tokenized_citations == actual_tokenized_citations



def test_tokenize_reference_input_wrong_file_extension(capsys):
    
    with pytest.raises(SystemExit):
        tokenize_reference_input("asdf.asdf", False)
    captured = capsys.readouterr()
    
    assert captured.out == "Unknown file type for reference file.\n"



def test_tokenize_reference_input_empty_file(capsys):
    
    with pytest.raises(SystemExit):
        tokenize_reference_input(os.path.join("tests", "testing_files", "empty_file.txt"), False)
    captured = capsys.readouterr()
    
    assert captured.out == "Nothing was read from the reference file. Make sure the file is not empty or is a supported file type.\n"



def test_tokenize_reference_input_MEDLINE():
    
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_MEDLINE.json"))
    
    actual_tokenized_citations = tokenize_reference_input(os.path.join("tests", "testing_files", "medline.txt"), True, False)
    
    assert expected_tokenized_citations == actual_tokenized_citations



def test_tokenize_reference_input_no_references(capsys):
    
    with pytest.raises(SystemExit):
        tokenize_reference_input(os.path.join("tests", "testing_files", "testing_text.txt"), False)
    captured = capsys.readouterr()
    
    assert captured.out == "Warning: Could not tokenize any citations in provided reference. Check setup and formatting and try again.\n"







