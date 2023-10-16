# -*- coding: utf-8 -*-



import os
import copy

import pytest
import requests

from fixtures import  authors_dict
from academic_tracker.webio import search_ORCID_for_ids, search_Google_Scholar_for_ids
from academic_tracker.webio import get_DOI_from_Crossref
# from academic_tracker.webio import get_grants_from_Crossref
from academic_tracker.fileio import load_json


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())



@pytest.fixture
def ORCID_query():
    return load_json(os.path.join("tests", "testing_files", "ORCID_author_search_query.json"))


def test_search_ORCID_for_ids_already_has_id(ORCID_query, authors_dict, mocker):
    def mock_query(*args, **kwargs):
        return ORCID_query
    mocker.patch("academic_tracker.webio.orcid.PublicAPI.search", mock_query)
    
    def mock_token(*args, **kwargs):
        return "sdfg"
    mocker.patch("academic_tracker.webio.orcid.PublicAPI.get_search_token_from_orcid", mock_token)
    
    authors_dict_check = copy.deepcopy(authors_dict)
    
    assert search_ORCID_for_ids("qwerqwer", "asdfasdf", authors_dict) == authors_dict_check
    

def test_search_ORCID_for_ids_no_affiliations(ORCID_query, authors_dict, mocker):
    def mock_query(*args, **kwargs):
        return ORCID_query
    mocker.patch("academic_tracker.webio.orcid.PublicAPI.search", mock_query)
    
    def mock_token(*args, **kwargs):
        return "sdfg"
    mocker.patch("academic_tracker.webio.orcid.PublicAPI.get_search_token_from_orcid", mock_token)
    
    del authors_dict["Andrew Morris"]["affiliations"]
    authors_dict["Andrew Morris"]["ORCID"] = ""
    
    authors_dict_check = copy.deepcopy(authors_dict)
    
    assert search_ORCID_for_ids("qwerqwer", "asdfasdf", authors_dict) == authors_dict_check
    
    
def test_search_ORCID_for_ids_not_found(ORCID_query, authors_dict, mocker):
    def mock_query(*args, **kwargs):
        return ORCID_query
    mocker.patch("academic_tracker.webio.orcid.PublicAPI.search", mock_query)
    
    def mock_token(*args, **kwargs):
        return "sdfg"
    mocker.patch("academic_tracker.webio.orcid.PublicAPI.get_search_token_from_orcid", mock_token)
    
    authors_dict["Andrew Morris"]["ORCID"] = ""
    
    authors_dict_check = copy.deepcopy(authors_dict)
    
    assert search_ORCID_for_ids("qwerqwer", "asdfasdf", authors_dict) == authors_dict_check
    
    
def test_search_ORCID_for_ids_found(ORCID_query, authors_dict, mocker):
    def mock_query(*args, **kwargs):
        return ORCID_query
    mocker.patch("academic_tracker.webio.orcid.PublicAPI.search", mock_query)
    
    def mock_token(*args, **kwargs):
        return "sdfg"
    mocker.patch("academic_tracker.webio.orcid.PublicAPI.get_search_token_from_orcid", mock_token)
    
    authors_dict["Andrew Morris"]["ORCID"] = ""
    authors_dict["Andrew Morris"]["affiliations"] = ["Bristol"]
    
    authors_dict_check = copy.deepcopy(authors_dict)
    authors_dict_check["Andrew Morris"]["ORCID"] = "0000-0003-1910-4865"
    
    assert search_ORCID_for_ids("qwerqwer", "asdfasdf", authors_dict) == authors_dict_check




@pytest.fixture
def scholarly_authors():
    return load_json(os.path.join("tests", "testing_files", "scholarly_author_query.json"))


def test_search_Google_Scholar_for_ids_already_has_id(scholarly_authors, authors_dict, mocker):
    def mock_queried_author(*args, **kwargs):
        return scholarly_authors
    mocker.patch("academic_tracker.webio.scholarly.scholarly.search_author", mock_queried_author)
    
    authors_dict_check = copy.deepcopy(authors_dict)
    
    assert search_Google_Scholar_for_ids(authors_dict) == authors_dict_check
    
    
def test_search_Google_Scholar_for_ids_no_affiliations(scholarly_authors, authors_dict, mocker):
    def mock_queried_author(*args, **kwargs):
        return scholarly_authors
    mocker.patch("academic_tracker.webio.scholarly.scholarly.search_author", mock_queried_author)
    
    del authors_dict["Andrew Morris"]["affiliations"]
    authors_dict["Andrew Morris"]["scholar_id"] = ""
    
    authors_dict_check = copy.deepcopy(authors_dict)
    
    assert search_Google_Scholar_for_ids(authors_dict) == authors_dict_check
    
    
def test_search_Google_Scholar_for_ids_not_found(scholarly_authors, authors_dict, mocker):
    def mock_queried_author(*args, **kwargs):
        return scholarly_authors
    mocker.patch("academic_tracker.webio.scholarly.scholarly.search_author", mock_queried_author)
    
    authors_dict["Andrew Morris"]["scholar_id"] = ""
    authors_dict["Andrew Morris"]["first_name"] = "asdf"
    
    authors_dict_check = copy.deepcopy(authors_dict)
    
    assert search_Google_Scholar_for_ids(authors_dict) == authors_dict_check
    
    
def test_search_Google_Scholar_for_ids_found(scholarly_authors, authors_dict, mocker):
    def mock_queried_author(*args, **kwargs):
        return scholarly_authors
    mocker.patch("academic_tracker.webio.scholarly.scholarly.search_author", mock_queried_author)
    
    authors_dict["Andrew Morris"]["scholar_id"] = ""
    
    authors_dict_check = copy.deepcopy(authors_dict)
    authors_dict_check["Andrew Morris"]["scholar_id"] = "-j7fxnEAAAAJ"
    
    assert search_Google_Scholar_for_ids(authors_dict) == authors_dict_check
    
    
    


def test_get_DOI_from_Crossref_DOI_found(mocker):
    def mock_query(*args, **kwargs):
        return load_json(os.path.join("tests", "testing_files", "Crossref_DOI_query.json"))
    mocker.patch("academic_tracker.webio.habanero.Crossref.works", mock_query)
    
    assert get_DOI_from_Crossref("The Existential Dimension to Aging", "ptth222@uky.edu") == '10.1353/pbm.2020.0014'


def test_get_DOI_from_Crossref_DOI_not_found(mocker):
    def mock_query(*args, **kwargs):
        return load_json(os.path.join("tests", "testing_files", "Crossref_DOI_query.json"))
    mocker.patch("academic_tracker.webio.habanero.Crossref.works", mock_query)
    
    assert get_DOI_from_Crossref("asdfasdf", "ptth222@uky.edu") == None


## This function is unused in the actual code.
# def test_get_grants_from_Crossref_grants_found(mocker):
#     def mock_query(*args, **kwargs):
#         return load_json(os.path.join("tests", "testing_files", "Crossref_grant_query.json"))
#     mocker.patch("academic_tracker.webio.habanero.Crossref.works", mock_query)
    
#     assert get_grants_from_Crossref("Multifunctional temperature\u2010responsive polymers as advanced biomaterials and beyond", "ptth222@uky.edu", ['P42ES007380']) == ['P42ES007380']


# def test_get_grants_from_Crossref_grants_not_found(mocker):
#     def mock_query(*args, **kwargs):
#         return load_json(os.path.join("tests", "testing_files", "Crossref_grant_query.json"))
#     mocker.patch("academic_tracker.webio.habanero.Crossref.works", mock_query)
    
#     assert get_grants_from_Crossref("asdfasdf", "ptth222@uky.edu", ['P42ES007380']) == None









