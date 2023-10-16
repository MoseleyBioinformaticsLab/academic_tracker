# -*- coding: utf-8 -*-

import os

import pytest
import pickle
import requests
import xml.etree.ElementTree as ET
import json

import pymed

from fixtures import authors_dict
from academic_tracker.athr_srch_webio import search_PubMed_for_pubs, search_ORCID_for_pubs, search_Google_Scholar_for_pubs
from academic_tracker.athr_srch_webio import search_Crossref_for_pubs
from academic_tracker.fileio import load_json



@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
    


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



## The expected_dicts here are generated in test_athr_srch_modularized.py.

def test_search_PubMed_for_pubs_first_pass(config_dict_Hunter_only, original_queries):
    expected_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs1.json"))
    test_publication_dict, all_queries = search_PubMed_for_pubs({}, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", original_queries["PubMed"])
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["PubMed"]


def test_search_PubMed_for_pubs_second_pass(config_dict_Hunter_only, original_queries):
    running_pubs = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs4.json"))
    expected_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs5.json"))
    test_publication_dict, all_queries = search_PubMed_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", original_queries["PubMed"])
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["PubMed"]
    

def test_search_PubMed_for_pubs_merge(config_dict_Hunter_only, original_queries):
    """PubMed is always ran first, so the merge code isn't triggered in other tests. 
    Feed a publication dict created from Google Scholar alone into prev_query to test the merge code."""
    running_pubs = load_json(os.path.join("tests", "testing_files", "solo_Google_Scholar.json"))
    expected_dict = load_json(os.path.join("tests", "testing_files", "PubMed_merge.json"))
    test_publication_dict, all_queries = search_PubMed_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", original_queries["PubMed"])
    # with open(os.path.join("tests", "testing_files", "PubMed_merge_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(test_publication_dict, indent=2, sort_keys=True))
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["PubMed"]
    

def test_search_PubMed_for_pubs_continues(config_dict_Hunter_only, original_queries, mocker):
    "Feed in a prev_query that will trigger the continue lines."
    prev_queries = original_queries["PubMed"]
    prev_queries["Hunter Moseley"] = prev_queries["Hunter Moseley"][0:3]
    prev_queries["Hunter Moseley"][0] = prev_queries["Hunter Moseley"][0].toDict()
    prev_queries["Hunter Moseley"][1].publication_date = None
    mocker.patch("academic_tracker.athr_srch_webio.helper_functions.match_pub_authors_to_config_authors", 
                  side_effect=[[]])
    test_publication_dict, all_queries = search_PubMed_for_pubs({}, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", prev_queries)
    assert test_publication_dict == {}
    ## If the type is not pymed.article.PubMedArticle, then it is not added to all_queries.
    del prev_queries["Hunter Moseley"][0]
    assert all_queries == prev_queries


def test_search_ORCID_for_pubs_first_pass(config_dict_Hunter_only, original_queries):
    expected_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs1.json"))
    test_publication_dict, all_queries = search_ORCID_for_pubs({}, "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["ORCID"]


def test_search_ORCID_for_pubs_second_pass(config_dict_Hunter_only, original_queries):
    running_pubs = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs3.json"))
    expected_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "no_PubMed", "running_pubs4.json"))
    test_publication_dict, all_queries = search_ORCID_for_pubs(running_pubs, "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["ORCID"]


def test_search_ORCID_for_pubs_merge(config_dict_Hunter_only, original_queries):
    "Previous tests did not trigger a merge because everything was merged in other calls on the first pass."
    running_pubs = load_json(os.path.join("tests", "testing_files", "solo_Google_Scholar.json"))
    expected_dict = load_json(os.path.join("tests", "testing_files", "ORCID_merge.json"))
    test_publication_dict, all_queries = search_ORCID_for_pubs(running_pubs, "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
    # with open(os.path.join("tests", "testing_files", "ORCID_merge_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(test_publication_dict, indent=2, sort_keys=True))
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["ORCID"]


def test_search_ORCID_for_pubs_misc(config_dict_Hunter_only, original_queries):
    "Manually modifying some ORCID results to trigger miscellaneous code not triggered by other tests."
    prev_queries = original_queries["ORCID"]
    prev_queries["Hunter Moseley"] = prev_queries["Hunter Moseley"][0:3]
    
    ##Change doi external ID to something else.
    prev_queries["Hunter Moseley"][0]["work-summary"][0]["external-ids"]["external-id"][0]["external-id-type"] = "asdf"
    prev_queries["Hunter Moseley"][0]["work-summary"][0]["external-ids"]["external-id"][0]["external-id-url"]["value"] = "asdf"
    prev_queries["Hunter Moseley"][1]["work-summary"][0]["external-ids"]["external-id"][0]["external-id-type"] = "pmid"
    prev_queries["Hunter Moseley"][1]["work-summary"][0]["external-ids"]["external-id"][0]["external-id-url"] = None
    del prev_queries["Hunter Moseley"][1]["work-summary"][1]
    ## Create an entry with no title.
    prev_queries["Hunter Moseley"][2]["work-summary"][0]["title"] = None
    
    ## Add an author with no ORCID to trigger continue.
    config_dict_Hunter_only["Authors"]["asdf"] = {}
    
    ## Add a collective_name to Hunter to create this author style instead of the usual one.
    config_dict_Hunter_only["Authors"]["Hunter Moseley"]["collective_name"] = "Some Collective"
    
    expected_dict = load_json(os.path.join("tests", "testing_files", "ORCID_misc.json"))
    test_publication_dict, all_queries = search_ORCID_for_pubs({}, "asdf", "asdf", config_dict_Hunter_only["Authors"], prev_queries)
    # with open(os.path.join("tests", "testing_files", "ORCID_misc_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(test_publication_dict, indent=2, sort_keys=True))
    assert test_publication_dict == expected_dict
    ## An empty "asdf" author gets added that wasn't there in the original run.
    del all_queries["asdf"]
    assert all_queries == prev_queries


def test_search_ORCID_for_pubs_no_IDs(config_dict_Hunter_only, original_queries, mocker, capsys):
    "If we can't find a DOI, pubmed id or title, test that a message is printed."
    prev_queries = original_queries["ORCID"]
    prev_queries["Hunter Moseley"] = prev_queries["Hunter Moseley"][0:1]
    prev_queries["Hunter Moseley"][0]["work-summary"][0]["external-ids"]["external-id"] = []
    
    mock_orcid = mocker.MagicMock()
    mock_orcid.configure_mock(
        **{
            "get_search_token_from_orcid.return_value": "asdf",
            "read_record_public.return_value": {"group":prev_queries["Hunter Moseley"]}
        }
    )
    
    mocker.patch("academic_tracker.athr_srch_webio.orcid.PublicAPI", 
                  side_effect=[mock_orcid])
    
    test_publication_dict, all_queries = search_ORCID_for_pubs({}, "asdf", "asdf", config_dict_Hunter_only["Authors"], None)
    captured = capsys.readouterr()
    # with open(os.path.join("tests", "testing_files", "ORCID_misc_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(test_publication_dict, indent=2, sort_keys=True))
    assert test_publication_dict == {}
    assert captured.out == ("Warning: Could not find a DOI, URL, or PMID for a "
                            "publication when searching ORCID. It will not be in the publications\n"
                            "Title: The metabolomics workbench file status website: a metadata "
                            "repository promoting FAIR principles of metabolomics data\n")
    assert all_queries == prev_queries


def test_search_Google_Scholar_for_pubs_first_pass(config_dict_Hunter_only, original_queries):
    expected_dict = load_json(os.path.join("tests", "testing_files", "solo_Google_Scholar.json"))
    test_publication_dict, all_queries = search_Google_Scholar_for_pubs({}, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", original_queries["Google Scholar"])
    # with open(os.path.join("tests", "testing_files", "solo_Google_Scholar_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(test_publication_dict, indent=2, sort_keys=True))
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["Google Scholar"]


def test_search_Google_Scholar_for_pubs_second_pass(config_dict_Hunter_only, original_queries):
    running_pubs = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs6.json"))
    expected_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs7.json"))
    test_publication_dict, all_queries = search_Google_Scholar_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", original_queries["Google Scholar"])
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["Google Scholar"]
    

def test_search_Google_Scholar_for_pubs_merge(config_dict_Hunter_only, original_queries):
    "Previous tests did not trigger a merge because everything was merged in other calls on the first pass."
    running_pubs = load_json(os.path.join("tests", "testing_files", "solo_Crossref.json"))
    expected_dict = load_json(os.path.join("tests", "testing_files", "Google_Scholar_merge.json"))
    test_publication_dict, all_queries = search_Google_Scholar_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", original_queries["Google Scholar"])
    # with open(os.path.join("tests", "testing_files", "Google_Scholar_merge_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(test_publication_dict, indent=2, sort_keys=True))
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["Google Scholar"]


def test_search_Google_Scholar_for_pubs_misc(config_dict_Hunter_only, original_queries):
    "Manually modifying some Google Scholar results to trigger miscellaneous code not triggered by other tests."
    prev_queries = original_queries["Google Scholar"]
    prev_queries["Hunter Moseley"] = prev_queries["Hunter Moseley"][0:1]
    prev_queries["Hunter Moseley"][0]["bib"]["pub_year"] = 2022
    
    ## Add an author with no scholar_id to trigger continue.
    config_dict_Hunter_only["Authors"]["asdf"] = {}
    
    ## Add a collective_name to Hunter to create this author style instead of the usual one.
    config_dict_Hunter_only["Authors"]["Hunter Moseley"]["collective_name"] = "Some Collective"
    
    expected_dict = load_json(os.path.join("tests", "testing_files", "Google_Scholar_misc.json"))
    test_publication_dict, all_queries = search_Google_Scholar_for_pubs({}, config_dict_Hunter_only["Authors"], "asdf", prev_queries)
    # with open(os.path.join("tests", "testing_files", "Google_Scholar_misc_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(test_publication_dict, indent=2, sort_keys=True))
    assert test_publication_dict == expected_dict
    ## An empty "asdf" author gets added that wasn't there in the original run.
    del all_queries["asdf"]
    assert all_queries == prev_queries


def test_search_Google_Scholar_for_pubs_query_error(config_dict_Hunter_only, original_queries, capsys, mocker):
    "Mock an error to make sure it is caught and a message is printed."    
    mocker.patch("academic_tracker.athr_srch_webio.scholarly.scholarly.search_author_id", 
                  side_effect=[Exception])
    test_publication_dict, all_queries = search_Google_Scholar_for_pubs({}, config_dict_Hunter_only["Authors"], "asdf", None)
    captured = capsys.readouterr()
    
    assert ("Warning: The \"scholar_id\" for author Hunter Moseley is probably "
            "incorrect, an error occured when trying to query Google Scholar.\n") in captured.out
    assert r'Traceback (most recent call last):' in captured.out
    assert r'Exception' in captured.out


def test_search_Google_Scholar_for_pubs_scholar_id_mismatch(config_dict_Hunter_only, original_queries, mocker):
    "Make sure that if scholar_ids don't match the author is skipped."    
    mocker.patch("academic_tracker.athr_srch_webio.scholarly.scholarly.search_author_id", 
                  side_effect=[{"scholar_id": "qwer"}])
    test_publication_dict, all_queries = search_Google_Scholar_for_pubs({}, config_dict_Hunter_only["Authors"], "asdf", None)
    assert test_publication_dict == {}
    assert all_queries == {'Hunter Moseley': []}
    

def test_search_Google_Scholar_for_pubs_fill_author(config_dict_Hunter_only, original_queries, mocker):
    "Mock it so that the fill function is called."
    publications = original_queries["Google Scholar"]["Hunter Moseley"][0:1]
    publications[0]["bib"]["pub_year"] = 2022
    
    mocker.patch("academic_tracker.athr_srch_webio.scholarly.scholarly.search_author_id", 
                  side_effect=[{"scholar_id": config_dict_Hunter_only["Authors"]["Hunter Moseley"]["scholar_id"], "publications":{}}])
    mocker.patch("academic_tracker.athr_srch_webio.scholarly.scholarly.fill", 
                  side_effect=[{"publications": publications}])
    mocker.patch("academic_tracker.athr_srch_webio.webio.get_DOI_from_Crossref", 
                  side_effect=[publications[0]["doi"]])
    
    expected_dict = load_json(os.path.join("tests", "testing_files", "Google_Scholar_misc.json"))
    expected_dict["https://doi.org/10.1016/s0959-440x(99)00019-6"]["authors"] = [{
                                                                                    "ORCID": "0000-0003-3995-5368",
                                                                                    "affiliation": "kentucky",
                                                                                    "author_id": "Hunter Moseley",
                                                                                    "firstname": "Hunter",
                                                                                    "initials": None,
                                                                                    "lastname": "Moseley"
                                                                                  }]
    test_publication_dict, all_queries = search_Google_Scholar_for_pubs({}, config_dict_Hunter_only["Authors"], "asdf", None)
    assert test_publication_dict == expected_dict
    assert all_queries == {'Hunter Moseley': publications}


def test_search_Google_Scholar_for_pubs_fill_pub(config_dict_Hunter_only, original_queries, mocker):
    "Test that fill publication works."
    publications = original_queries["Google Scholar"]["Hunter Moseley"][0:1]
    publications[0]["bib"]["pub_year"] = 2022
    publications[0]["pub_url"] = "asdf"
    
    mocker.patch("academic_tracker.athr_srch_webio.scholarly.scholarly.search_author_id", 
                  side_effect=[{"scholar_id": config_dict_Hunter_only["Authors"]["Hunter Moseley"]["scholar_id"], "publications":{}}])
    mocker.patch("academic_tracker.athr_srch_webio.scholarly.scholarly.fill", 
                  side_effect=[{"publications": publications}, publications[0]])
    mocker.patch("academic_tracker.athr_srch_webio.webio.get_DOI_from_Crossref", 
                  side_effect=[None])
    
    expected_dict = load_json(os.path.join("tests", "testing_files", "Google_Scholar_misc.json"))
    expected_dict["https://doi.org/10.1016/s0959-440x(99)00019-6"]["authors"] = [{
                                                                                    "ORCID": "0000-0003-3995-5368",
                                                                                    "affiliation": "kentucky",
                                                                                    "author_id": "Hunter Moseley",
                                                                                    "firstname": "Hunter",
                                                                                    "initials": None,
                                                                                    "lastname": "Moseley"
                                                                                  }]
    expected_dict["asdf"] = expected_dict["https://doi.org/10.1016/s0959-440x(99)00019-6"]
    del expected_dict["https://doi.org/10.1016/s0959-440x(99)00019-6"]
    expected_dict["asdf"]["doi"] = None
    
    test_publication_dict, all_queries = search_Google_Scholar_for_pubs({}, config_dict_Hunter_only["Authors"], "asdf", None)
    assert test_publication_dict == expected_dict
    assert all_queries == {'Hunter Moseley': publications}


def test_search_Google_Scholar_for_pubs_no_pub_ID(config_dict_Hunter_only, original_queries, capsys, mocker):
    "Test that a message is printed when a pub ID cannot be found."
    publications = original_queries["Google Scholar"]["Hunter Moseley"][0:1]
    publications[0]["bib"]["pub_year"] = 2022
    
    mocker.patch("academic_tracker.athr_srch_webio.scholarly.scholarly.search_author_id", 
                  side_effect=[{"scholar_id": config_dict_Hunter_only["Authors"]["Hunter Moseley"]["scholar_id"], "publications":{}}])
    mocker.patch("academic_tracker.athr_srch_webio.scholarly.scholarly.fill", 
                  side_effect=[{"publications": publications}, publications[0]])
    mocker.patch("academic_tracker.athr_srch_webio.webio.get_DOI_from_Crossref", 
                  side_effect=[None])
        
    test_publication_dict, all_queries = search_Google_Scholar_for_pubs({}, config_dict_Hunter_only["Authors"], "asdf", None)
    captured = capsys.readouterr()
    
    assert test_publication_dict == {}
    assert all_queries == {'Hunter Moseley': publications}
    assert captured.out == ("Warning: Could not find a DOI, URL, or PMID for a publication "
                            "when searching Google Scholar. It will not be in the publications.\n"
                            "Title: Automated analysis of NMR assignments and structures for proteins\n")


def test_search_Crossref_for_pubs_first_pass(config_dict_Hunter_only, original_queries):
    expected_dict = load_json(os.path.join("tests", "testing_files", "solo_Crossref.json"))
    test_publication_dict, all_queries = search_Crossref_for_pubs({}, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", original_queries["Crossref"])
    # with open(os.path.join("tests", "testing_files", "solo_Crossref_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(test_publication_dict, indent=2, sort_keys=True))
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["Crossref"]


def test_search_Crossref_for_pubs_second_pass(config_dict_Hunter_only, original_queries):
    running_pubs = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs7.json"))
    expected_dict = load_json(os.path.join("tests", "testing_files", "intermediate_results", "author_search", "all", "running_pubs8.json"))
    test_publication_dict, all_queries = search_Crossref_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", original_queries["Crossref"])
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["Crossref"]


def test_search_Crossref_for_pubs_merge(config_dict_Hunter_only, original_queries):
    "Previous tests did not trigger a merge because everything was merged in other calls on the first pass."
    running_pubs = load_json(os.path.join("tests", "testing_files", "solo_Google_Scholar.json"))
    expected_dict = load_json(os.path.join("tests", "testing_files", "Crossref_merge.json"))
    test_publication_dict, all_queries = search_Crossref_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "ptth222@uky.edu", original_queries["Crossref"])
    # with open(os.path.join("tests", "testing_files", "Crossref_merge_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(test_publication_dict, indent=2, sort_keys=True))
    assert test_publication_dict == expected_dict
    assert all_queries == original_queries["Crossref"]


def test_search_Crossref_for_pubs_misc(config_dict_Hunter_only, original_queries):
    "Manually modifying some Crossref results to trigger miscellaneous code not triggered by other tests."
    prev_queries = original_queries["Crossref"]
    prev_queries["Hunter Moseley"] = prev_queries["Hunter Moseley"][0:4]
    ## get rid of sources of dates so values will be None and continue will be triggered.
    del prev_queries["Hunter Moseley"][0]["published"]
    del prev_queries["Hunter Moseley"][0]["published-online"]
    ## Make publication year less than cutoff to trigger continue.
    prev_queries["Hunter Moseley"][1]["published"]["date-parts"][0][0] = 1999
    ## delete URL and DOI to trigger continue.
    del prev_queries["Hunter Moseley"][2]["DOI"]
    del prev_queries["Hunter Moseley"][2]["URL"]
    del prev_queries["Hunter Moseley"][2]["link"]
            
    expected_dict = load_json(os.path.join("tests", "testing_files", "Crossref_misc.json"))
    test_publication_dict, all_queries = search_Crossref_for_pubs({}, config_dict_Hunter_only["Authors"], "asdf", prev_queries)
    # with open(os.path.join("tests", "testing_files", "Crossref_misc_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(test_publication_dict, indent=2, sort_keys=True))
    assert test_publication_dict == expected_dict
    assert all_queries == prev_queries


def test_search_Crossref_for_pubs_no_pub_ID(config_dict_Hunter_only, original_queries, capsys, mocker):
    "Test that a message is printed when a pub ID cannot be found."
    prev_queries = original_queries["Crossref"]
    prev_queries["Hunter Moseley"] = prev_queries["Hunter Moseley"][0:1]
    del prev_queries["Hunter Moseley"][0]["DOI"]
    del prev_queries["Hunter Moseley"][0]["URL"]
    del prev_queries["Hunter Moseley"][0]["link"]
    
    mock_crossref = mocker.MagicMock()
    mock_crossref.configure_mock(
        **{
            "works.return_value": {"message":{"items":prev_queries["Hunter Moseley"]}}
        }
    )
    
    mocker.patch("academic_tracker.athr_srch_webio.habanero.Crossref", 
                  side_effect=[mock_crossref])
            
    test_publication_dict, all_queries = search_Crossref_for_pubs({}, config_dict_Hunter_only["Authors"], "asdf", None)
    captured = capsys.readouterr()
    
    assert test_publication_dict == {}
    assert all_queries == prev_queries
    assert captured.out == ("Warning: Could not find a DOI or external URL for a publication when "
                            "searching Crossref. It will not be in the publications.\n"
                            "Title: kegg_pull: a software package for the RESTful access and "
                            "pulling from the Kyoto Encyclopedia of Gene and Genomes\n")






