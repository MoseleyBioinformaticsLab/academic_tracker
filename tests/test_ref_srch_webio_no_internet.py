# -*- coding: utf-8 -*-

import os
import json

import pytest
import pymed
import pickle
import requests
import xml.etree.ElementTree as ET

from academic_tracker.ref_srch_webio import build_pub_dict_from_PMID, search_references_on_source
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
    

def test_search_references_on_source_unknown_source(capsys):
    with pytest.raises(SystemExit):
        search_references_on_source("asdf", {}, [], "ptth222@uky.edu")
    captured = capsys.readouterr()
    
    assert captured.out == "Error: When searching references there was an attempt to query an unknown source, 'asdf'.\n"



def test_search_references_on_PubMed(tokenized_citations, ref_pymed_query, mocker):
    def mock_query(*args, **kwargs):
        return ref_pymed_query
    mocker.patch("academic_tracker.ref_srch_webio.pymed.PubMed.query", mock_query)
    
    expected_publication_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_publication_dict.json"))
    expected_citation_keys = load_json(os.path.join("tests", "testing_files", "ref_srch_keys_for_citations.json"))
    
    actual_publication_dict, actual_citation_keys, all_pubs = search_references_on_source("PubMed", {}, tokenized_citations, "ptth222@uky.edu")
    # with open(os.path.join("tests", "testing_files", "ref_srch_publication_dict_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "ref_srch_keys_for_citations_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_citation_keys, indent=2, sort_keys=True))
    
    assert expected_publication_dict == actual_publication_dict
    assert expected_citation_keys == actual_citation_keys


def test_search_references_on_PubMed_merge(original_queries):
    running_pubs = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "publication_dict.json"))
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "tokenized_reference.json"))
    
    expected_publication_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_publication_dict_PubMed_merge.json"))
    expected_citation_keys = load_json(os.path.join("tests", "testing_files", "ref_srch_keys_for_citations_PubMed_merge.json"))
    
    actual_publication_dict, actual_citation_keys, all_pubs = search_references_on_source("PubMed", running_pubs, tokenized_citations, "ptth222@uky.edu", original_queries["PubMed"])
    # with open(os.path.join("tests", "testing_files", "ref_srch_publication_dict_PubMed_merge_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "ref_srch_keys_for_citations_PubMed_merge_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_citation_keys, indent=2, sort_keys=True))
    
    assert expected_publication_dict == actual_publication_dict
    assert expected_citation_keys == actual_citation_keys    


def test_search_references_on_PubMed_unsearchable_citation(original_queries, mocker):
    def mock_query(*args, **kwargs):
        return ref_pymed_query
    mocker.patch("academic_tracker.ref_srch_webio.pymed.PubMed.query", mock_query)
    
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "tokenized_reference.json"))
    tokenized_citations = [tokenized_citations[0]]
    tokenized_citations[0]["PMID"] = None
    tokenized_citations[0]["DOI"] = None
    tokenized_citations[0]["title"] = None
    
    actual_publication_dict, actual_citation_keys, all_pubs = search_references_on_source("PubMed", {}, tokenized_citations, "ptth222@uky.edu")

    assert {} == actual_publication_dict
    assert [None] == actual_citation_keys  


def test_search_references_on_PubMed_non_article(original_queries):
    running_pubs = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "publication_dict.json"))
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "tokenized_reference.json"))
    
    expected_publication_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_publication_dict_PubMed_merge.json"))
    del expected_publication_dict["https://doi.org/10.1007/978-1-4939-1258-2_11"]
    expected_citation_keys = load_json(os.path.join("tests", "testing_files", "ref_srch_keys_for_citations_PubMed_merge.json"))
    expected_citation_keys[2] = None
    
    ## Make a query not a dict to trigger a continue.
    original_queries["PubMed"][2][0] = original_queries["PubMed"][2][0].toDict()
    actual_publication_dict, actual_citation_keys, all_pubs = search_references_on_source("PubMed", running_pubs, tokenized_citations, "ptth222@uky.edu", original_queries["PubMed"])
    
    assert expected_publication_dict == actual_publication_dict
    assert expected_citation_keys == actual_citation_keys    


def test_search_references_on_PubMed_title_match(original_queries):
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "tokenized_reference.json"))
    tokenized_citations = [tokenized_citations[0]]
    tokenized_citations[0]["PMID"] = None
    tokenized_citations[0]["DOI"] = None
    
    expected_publication_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_publication_dict_PubMed_title_match.json"))
    
    actual_publication_dict, actual_citation_keys, all_pubs = search_references_on_source("PubMed", {}, tokenized_citations, "ptth222@uky.edu", original_queries["PubMed"])
    # with open(os.path.join("tests", "testing_files", "ref_srch_publication_dict_PubMed_title_match_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))

    assert expected_publication_dict == actual_publication_dict
    assert ['https://doi.org/10.3390/metabo3040853'] == actual_citation_keys  


def test_search_references_on_PubMed_duplicate_citation(original_queries):
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_PubMed", "tokenized_reference.json"))
    tokenized_citations = [tokenized_citations[0], tokenized_citations[0]]
    
    original_queries["PubMed"] = [original_queries["PubMed"][0], original_queries["PubMed"][0]]
    
    expected_publication_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_publication_dict_PubMed_duplicate_citation.json"))
    expected_citation_keys = load_json(os.path.join("tests", "testing_files", "ref_srch_keys_for_citations_PubMed_duplicate_citation.json"))
    
    actual_publication_dict, actual_citation_keys, all_pubs = search_references_on_source("PubMed", {}, tokenized_citations, "ptth222@uky.edu", original_queries["PubMed"])
    # with open(os.path.join("tests", "testing_files", "ref_srch_publication_dict_PubMed_duplicate_citation_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "ref_srch_keys_for_citations_PubMed_duplicate_citation_new.json"),'w') as jsonFile:
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
    
    actual_pub_dict, actual_citation_keys, all_pubs = search_references_on_source("Crossref", {}, tokenized_citations, "ptth222@uky.edu")
    # with open(os.path.join("tests", "testing_files", "ref_srch_Crossref_pub_dict_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_pub_dict, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "ref_srch_Crossref_keys_for_citations_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_citation_keys, indent=2, sort_keys=True))
        
    assert actual_pub_dict == expected_pub_dict
    assert actual_citation_keys == expected_citation_keys


def test_search_references_on_Crossref_merge(original_queries):
    running_pubs = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "publication_dict.json"))
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "tokenized_reference.json"))
    
    expected_publication_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_publication_dict_Crossref_merge.json"))
    expected_citation_keys = load_json(os.path.join("tests", "testing_files", "ref_srch_keys_for_citations_Crossref_merge.json"))
    
    actual_publication_dict, actual_citation_keys, all_pubs = search_references_on_source("Crossref", running_pubs, tokenized_citations, "ptth222@uky.edu", original_queries["Crossref"])
    # with open(os.path.join("tests", "testing_files", "ref_srch_publication_dict_Crossref_merge_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "ref_srch_keys_for_citations_Crossref_merge_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_citation_keys, indent=2, sort_keys=True))
    
    assert expected_publication_dict == actual_publication_dict
    assert expected_citation_keys == actual_citation_keys    


def test_search_references_on_Crossref_unsearchable_citation(original_queries, mocker):
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "tokenized_reference.json"))
    tokenized_citations = [tokenized_citations[0]]
    tokenized_citations[0]["PMID"] = None
    tokenized_citations[0]["DOI"] = None
    tokenized_citations[0]["title"] = None
    
    mock_crossref = mocker.MagicMock()
    mock_crossref.configure_mock(
        **{
            "works.return_value": {"message":{"items":original_queries["Crossref"][0]}}
        }
    )
    
    mocker.patch("academic_tracker.ref_srch_webio.habanero.Crossref", 
                  side_effect=[mock_crossref])
    
    actual_publication_dict, actual_citation_keys, all_pubs = search_references_on_source("Crossref", {}, tokenized_citations, "ptth222@uky.edu", None)

    assert {} == actual_publication_dict
    assert [None] == actual_citation_keys  


def test_search_references_on_Crossref_no_pub_id(original_queries, mocker, capsys):
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "tokenized_reference.json"))
    tokenized_citations = [tokenized_citations[0]]
    
    modified_query = original_queries["Crossref"][0]
    del modified_query[0]["DOI"]
    del modified_query[0]["URL"]
    del modified_query[0]["link"]
    
    mock_crossref = mocker.MagicMock()
    mock_crossref.configure_mock(
        **{
            "works.return_value": {"message":{"items":modified_query}}
        }
    )
    
    mocker.patch("academic_tracker.ref_srch_webio.habanero.Crossref", 
                  side_effect=[mock_crossref])
    
    actual_publication_dict, actual_citation_keys, all_pubs = search_references_on_source("Crossref", {}, tokenized_citations, "ptth222@uky.edu", None)
    captured = capsys.readouterr()

    assert {} == actual_publication_dict
    assert [None] == actual_citation_keys
    assert captured.out == ("Warning: Could not find a DOI or external URL for a publication when "
                            "searching Crossref. It will not be in the publications.\n"
                            "Title: A Computational Framework for High-Throughput Isotopic "
                            "Natural Abundance Correction of Omics-Level Ultra-High Resolution FT-MS Datasets\n")


def test_search_references_on_Crossref_title_match(original_queries):
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "tokenized_reference.json"))
    tokenized_citations = [tokenized_citations[0]]
    tokenized_citations[0]["PMID"] = None
    tokenized_citations[0]["DOI"] = None
    
    expected_publication_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_publication_dict_Crossref_title_match.json"))
    
    actual_publication_dict, actual_citation_keys, all_pubs = search_references_on_source("Crossref", {}, tokenized_citations, "ptth222@uky.edu", original_queries["Crossref"])
    # with open(os.path.join("tests", "testing_files", "ref_srch_publication_dict_Crossref_title_match_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))

    assert expected_publication_dict == actual_publication_dict
    assert ['https://doi.org/10.3390/metabo3040853'] == actual_citation_keys  
    

def test_search_references_on_Crossref_duplicate_citation(original_queries):
    tokenized_citations = load_json(os.path.join("tests", "testing_files", "intermediate_results", "ref_search", "no_Crossref", "tokenized_reference.json"))
    tokenized_citations = [tokenized_citations[0], tokenized_citations[0]]
    
    original_queries["Crossref"] = [original_queries["Crossref"][0], original_queries["Crossref"][0]]
    
    expected_publication_dict = load_json(os.path.join("tests", "testing_files", "ref_srch_publication_dict_Crossref_duplicate_citation.json"))
    expected_citation_keys = load_json(os.path.join("tests", "testing_files", "ref_srch_keys_for_citations_Crossref_duplicate_citation.json"))
    
    actual_publication_dict, actual_citation_keys, all_pubs = search_references_on_source("Crossref", {}, tokenized_citations, "ptth222@uky.edu", original_queries["Crossref"])
    # with open(os.path.join("tests", "testing_files", "ref_srch_publication_dict_Crossref_duplicate_citation_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_publication_dict, indent=2, sort_keys=True))
    # with open(os.path.join("tests", "testing_files", "ref_srch_keys_for_citations_Crossref_duplicate_citation_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_citation_keys, indent=2, sort_keys=True))
    
    assert expected_publication_dict == actual_publication_dict
    assert expected_citation_keys == actual_citation_keys 


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


def test_parse_myncbi_citations_bad_web_address(mocker, capsys):
    def mock_query(*args, **kwargs):
        return None
    mocker.patch("academic_tracker.ref_srch_webio.webio.get_url_contents_as_str", mock_query)
    
    with pytest.raises(SystemExit):
        parse_myncbi_citations("asdf")
    captured = capsys.readouterr()
    
    assert captured.out == "Error: Could not access the MYNCBI webpage. Make sure the address is correct.\n"


def test_parse_myncbi_citations_bad_page(mocker, capsys):
    def page_generator():
        pages = load_json(os.path.join("tests", "testing_files", "myncbi_webpages.json"))
        for i, page in enumerate(pages):
            if i == 1:
                yield None
            else:
                yield page
            
    pages = page_generator()
        
    def mock_query(*args, **kwargs):
        return next(pages)
    mocker.patch("academic_tracker.ref_srch_webio.webio.get_url_contents_as_str", mock_query)
    
    with pytest.raises(SystemExit):
        parse_myncbi_citations("asdf")
    captured = capsys.readouterr()
    
    assert captured.out == "Error: Could not access page 2 of the MYNCBI webpage. Aborting run.\n"



## Test that the JSON read in works and finds and eliminates duplicates.
def test_tokenize_reference_input_JSON(capsys):
    
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_citations_duplicates_removed.json"))
    expected_tokenized_citations[55]["reference_line"] = ""
    
    actual_tokenized_citations = tokenize_reference_input(os.path.join("tests", "testing_files", "tokenized_citations_missing_ref_line.json"), False)
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


def test_tokenize_reference_input_myncbi(mocker):
    def page_generator():
        pages = load_json(os.path.join("tests", "testing_files", "myncbi_webpages.json"))
        for page in pages:
            yield page
            
    pages = page_generator()
        
    def mock_query(*args, **kwargs):
        return next(pages)
    mocker.patch("academic_tracker.ref_srch_webio.webio.get_url_contents_as_str", mock_query)
    
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_citations.json"))
    
    actual_tokenized_citations = tokenize_reference_input("https://www.asdf/ncbi.nlm.nih.gov/myncbi/", False, False)
    
    assert expected_tokenized_citations == actual_tokenized_citations







