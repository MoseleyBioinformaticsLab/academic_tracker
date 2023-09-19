# -*- coding: utf-8 -*-


import re
import os

import pymed
import pytest
import xml.etree.ElementTree as ET 

from academic_tracker.fileio import load_json
from academic_tracker import __main__
from academic_tracker.helper_functions import vprint, regex_match_return, regex_group_return, regex_search_return
from academic_tracker.helper_functions import match_authors_in_pub_PubMed, match_authors_in_pub_Crossref
from academic_tracker.helper_functions import modify_pub_dict_for_saving, is_fuzzy_match_to_list, fuzzy_matches_to_list, is_pub_in_publication_dict 
from academic_tracker.helper_functions import create_authors_by_project_dict, adjust_author_attributes, find_duplicate_citations, are_citations_in_pub_dict
from fixtures import publication_dict, pub_with_grants, pub_with_matching_author, passing_config, authors_by_project_dict



def test_vprint(capsys):
    
    vprint("asdf")
    captured = capsys.readouterr()
    
    assert captured.out == "asdf\n"
    

def test_vprint_silent(monkeypatch, capsys):
    monkeypatch.setattr(__main__, "SILENT", True)
    
    vprint("asdf")
    captured = capsys.readouterr()
    
    assert captured.out == ""
    
    
def test_vprint_verbose_on(capsys):
    
    vprint("asdf", verbosity=1)
    captured = capsys.readouterr()
    
    assert captured.out == "asdf\n"
    

def test_vprint_verbose_off(monkeypatch, capsys):
    monkeypatch.setattr(__main__, "VERBOSE", False)
    
    vprint("asdf", verbosity=1)
    captured = capsys.readouterr()
    
    assert captured.out == ""


@pytest.mark.parametrize("regex, string_to_match, return_value", [
        
        (r"(?i).*doi:\s*([^\s]+\w).*", "asdfasdfasdf", ()),
        (r"(?i).*doi:\s*([^\s]+\w).*", "doi: asdf", re.match(r"(?i).*doi:\s*([^\s]+\w).*", "doi: asdf").groups()),
        ]) 
    
def test_regex_match_return(regex, string_to_match, return_value):
    
    assert regex_match_return(regex, string_to_match) == return_value



@pytest.mark.parametrize("regex_group, index, return_value", [
        
        (re.match(r"(?i).*doi:\s*([^\s]+\w).*", "doi: asdf").groups(), 0, "asdf"),
        ((), 0, ""),
        (re.match(r"(a*)(b*)", "aaaaabb").groups(), 1, "bb")
        ]) 
    
def test_regex_group_return(regex_group, index, return_value):
    
    assert regex_group_return(regex_group, index) == return_value



@pytest.mark.parametrize("regex, string_to_match, return_value", [
        
        (r"(?i).*doi:\s*([^\s]+\w).*", "asdfasdfasdf", ()),
        (r"(?i).*doi:\s*([^\s]+\w).*", "doi: asdf", re.search(r"(?i).*doi:\s*([^\s]+\w).*", "doi: asdf").groups()),
        ]) 
    
def test_regex_search_return(regex, string_to_match, return_value):
    
    assert regex_search_return(regex, string_to_match) == return_value



@pytest.fixture
def authors_json_file():
    return {"Hunter Moseley": {
            "ORCID": "0000-0003-3995-5368",
            "affiliations": [
              "kentucky"
            ],
            "cutoff_year": 2020,
            "email": "hunter.moseley@gmail.com",
            "first_name": "Hunter",
            "last_name": "Moseley",
            "pubmed_name_search": "Hunter Moseley",
            "scholar_id": "ctE_FZMAAAAJ"
          },
          "Isabel Escobar": {
            "ORCID": "0000-0001-9269-5927",
            "affiliations": [
              "kentucky"
            ],
            "cutoff_year": 2020,
            "email": "isabel.escobar@uky.edu",
            "first_name": "Isabel",
            "last_name": "Escobar",
            "pubmed_name_search": "Isabel Escobar",
            "scholar_id": "RfB5L8kAAAAJ"
          },}
    
    
@pytest.mark.parametrize("PM_author_list, returned_PM_author_list", [
        
        ([{ 'affiliation': 'Department of Neurology, University Medical Center, Johannes Gutenberg-University, Mainz, Germany.',
          'firstname': 'Carine',
          'initials': 'C',
          'lastname': 'Thalman'},
        { 'affiliation': 'Department of Biostats, Kentucky',
          'firstname': 'Hunter',
          'initials': 'HM',
          'lastname': 'Moseley'},],
        [{ 'affiliation': 'Department of Neurology, University Medical Center, Johannes Gutenberg-University, Mainz, Germany.',
          'firstname': 'Carine',
          'initials': 'C',
          'lastname': 'Thalman'},
        { 'affiliation': 'Department of Biostats, Kentucky',
          'firstname': 'Hunter',
          'initials': 'HM',
          'lastname': 'Moseley',
          'author_id': 'Hunter Moseley'},]),
           
        ([{ 'affiliation': 'Department of Neurology, University Medical Center, Johannes Gutenberg-University, Mainz, Germany.',
          'firstname': 'Carine',
          'initials': 'C',
          'lastname': 'Thalman'}], 
            []),
        
        ([{ 'affiliation': 'Department of Biostats, Kentucky',
          'firstname': 'Hunter N. B.',
          'initials': 'HM',
          'lastname': 'Moseley'},],
        [{ 'affiliation': 'Department of Biostats, Kentucky',
          'firstname': 'Hunter N. B.',
          'initials': 'HM',
          'lastname': 'Moseley',
          'author_id': 'Hunter Moseley'},]),
        
        ([{ 'affiliation': 'Department of Biostats, Kentucky',
          'firstname': 'X Hunter',
          'initials': 'HM',
          'lastname': 'Moseley'},],
        [{ 'affiliation': 'Department of Biostats, Kentucky',
          'firstname': 'X Hunter',
          'initials': 'HM',
          'lastname': 'Moseley',
          'author_id': 'Hunter Moseley'},]),
        ])
        
        
        
def test_match_authors_in_pub_PubMed(authors_json_file, PM_author_list, returned_PM_author_list):
    
    assert match_authors_in_pub_PubMed(authors_json_file, PM_author_list) == returned_PM_author_list



@pytest.mark.parametrize("CR_author_list, returned_CR_author_list", [
        
        ([{'given': 'Li',
            'family': 'Xiao',
            'sequence': 'first',
            'affiliation': [{'name': 'Department of Chemical and Materials\rEngineering and &Dagger;Department of Civil Engineering, University of Kentucky, Lexington, Kentucky 40506, United States'}]},
        {'given': 'Hunter',
        'family': 'Moseley',
        'sequence': 'additional',
        'affiliation': [{'name': 'Department of Chemical and Materials\rEngineering and &Dagger;Department of Civil Engineering, University of Kentucky, Lexington, Kentucky 40506, United States'}],
        'ORCID':'0000-0003-3995-5368'},],
        [{'given': 'Li',
            'family': 'Xiao',
            'sequence': 'first',
            'affiliation': [{'name': 'Department of Chemical and Materials\rEngineering and &Dagger;Department of Civil Engineering, University of Kentucky, Lexington, Kentucky 40506, United States'}]},
        {'given': 'Hunter',
        'family': 'Moseley',
        'sequence': 'additional',
        'affiliation': [{'name': 'Department of Chemical and Materials\rEngineering and &Dagger;Department of Civil Engineering, University of Kentucky, Lexington, Kentucky 40506, United States'}],
        'ORCID':'0000-0003-3995-5368',
        'author_id':'Hunter Moseley'},]),
           
        ([{'given': 'Li',
            'family': 'Xiao',
            'sequence': 'first',
            'affiliation': [{'name': 'Department of Chemical and Materials\rEngineering and &Dagger;Department of Civil Engineering, University of Kentucky, Lexington, Kentucky 40506, United States'}]}], 
            []),
        ]) 
        
def test_match_authors_in_pub_Crossref(CR_author_list, returned_CR_author_list, authors_json_file):
    
    assert match_authors_in_pub_Crossref(authors_json_file, CR_author_list) == returned_CR_author_list



@pytest.fixture
def pub_no_PMCID():
    xml_path = os.path.join("tests", "testing_files", "no_author.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())


def test_modify_pub_dict_for_saving_no_PMCID(pub_no_PMCID):
    modified_pub = load_json(os.path.join("tests", "testing_files", "PubMed_modified_to_save_no_PMCID.json"))
    del modified_pub["xml"]
            
    pub_to_check = modify_pub_dict_for_saving(pub_no_PMCID)
    
    assert pub_to_check == modified_pub



@pytest.fixture
def pub_with_PMCID():
    xml_path = os.path.join("tests", "testing_files", "pub_with_PMCID.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())


def test_modify_pub_dict_for_saving_with_PMCID(pub_with_PMCID):
    modified_pub = load_json(os.path.join("tests", "testing_files", "PubMed_modified_to_save_with_PMCID.json"))
            
    pub_to_check = modify_pub_dict_for_saving(pub_with_PMCID, True)
    
    assert pub_to_check == modified_pub




@pytest.mark.parametrize("str_to_match, list_to_matched, is_match", [
        
        ("asdf", ["qwer", "asdf", "zxcv"], True),
        ("asdf", ["qwer", "zxcv"], False)
        ]) 

def test_is_fuzzy_match_to_list(str_to_match, list_to_matched, is_match):
    assert is_fuzzy_match_to_list(str_to_match, list_to_matched) == is_match
    

@pytest.mark.parametrize("str_to_match, list_to_matched, matches", [
        
        ("asdf", ["qwer", "asdf", "zxcv"], [(1,"asdf")]),
        ("asdf", ["qwer", "zxcv"], [])
        ]) 

def test_fuzzy_matches_to_list(str_to_match, list_to_matched, matches):
    assert fuzzy_matches_to_list(str_to_match, list_to_matched) == matches


@pytest.mark.parametrize("pub_id, title, titles, is_in_pub_dict", [
        
        ("https://doi.org/10.1016/j.chroma.2021.462426", "asdf", [], True),
        ("asdf", "Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry.", 
          ["Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry.",          
          "Untargeted Stable Isotope Probing of the Gut Microbiota Metabolome Using 13C-Labeled Dietary Fibers."], True),
        ("asdf", "qwer", [], False)
        ]) 

def test_is_pub_in_publication_dict(pub_id, title, publication_dict, titles, is_in_pub_dict):
    assert is_pub_in_publication_dict(pub_id, title, publication_dict, titles) == is_in_pub_dict

  

def test_create_authors_by_project_dict(passing_config, authors_json_file, authors_by_project_dict, capsys):
    
    authors_by_project_dict_check = create_authors_by_project_dict(passing_config) 
    captured = capsys.readouterr()
    
    assert authors_by_project_dict_check == authors_by_project_dict and captured.out == "Warning: The author, Isabel Escobar, in the project 1 project of the project tracking configuration file could not be found in the Authors section of the Configuration JSON file.\n"
    
    
    
def test_adjust_author_attributes(authors_by_project_dict, passing_config):
    
    authors_by_project_dict["project 1"]["Hunter Moseley"]["affiliations"] = ["asdf"]
    authors_by_project_dict["project 1"]["Hunter Moseley"]["grants"] = ["asdf", "qwer"]
    authors_by_project_dict["project 1"]["Hunter Moseley"]["cutoff_year"] = 2000
    
#    del authors_by_project_dict["project 2"]["Hunter Moseley"]["affiliations"]
#    del authors_by_project_dict["project 2"]["Hunter Moseley"]["grants"]
#    del authors_by_project_dict["project 2"]["Hunter Moseley"]["cutoff_year"]
    
    modified_authors_json_file = {'Andrew Morris': {'ORCID': '0000-0003-1910-4865',
                                      'affiliations': ['kentucky'],
                                      'collaborator_report': {},
                                      'cutoff_year': 2020,
                                      'email': 'a.j.morris@uky.edu',
                                      'first_name': 'Andrew',
                                      'last_name': 'Morris',
                                      'pubmed_name_search': 'Andrew Morris',
                                      'scholar_id': '-j7fxnEAAAAJ',
                                      'grants': ['P42 ES007380', 'P42ES007380']},
                                  'Hunter Moseley': {'ORCID': '0000-0003-3995-5368',
                                      'affiliations': ['asdf', 'kentucky'],
                                      'collaborator_report': {},
                                      'cutoff_year': 2000,
                                      'email': 'hunter.moseley@gmail.com',
                                      'first_name': 'Hunter',
                                      'last_name': 'Moseley',
                                      'pubmed_name_search': 'Hunter Moseley',
                                      'scholar_id': 'ctE_FZMAAAAJ',
                                      'grants': ['P42 ES007380', 'P42ES007380', 'asdf', 'qwer']}}
        
    adjust_author_attributes(authors_by_project_dict, passing_config)
    
    assert passing_config["Authors"] == modified_authors_json_file
    
    


@pytest.fixture
def tokenized_citations():
    return [{"PMID":"1234", "DOI":"ASDF", "title":"made up title"},
            {"PMID":"", "DOI":"ASDF", "title":""},
            {"PMID":"1234", "DOI":"ASDF", "title":""},
            
            {"PMID":"", "DOI":"QWER", "title":""},
            {"PMID":"", "DOI":"qwer", "title":""},
            
            {"PMID":"4567", "DOI":"", "title":""},
            {"PMID":"4567", "DOI":"", "title":""},
            
            {"PMID":"", "DOI":"", "title":"new title"},
            {"PMID":"", "DOI":"", "title":"new titles"},]
    
def test_find_duplicate_citations(tokenized_citations):
    
    duplicate_citations_check = set([(0,1,2), (3,4), (5,6), (7,8)])
    
    duplicate_citations = find_duplicate_citations(tokenized_citations)
    
    duplicate_citations = {tuple(duplicates) for duplicates in duplicate_citations}
    
    assert duplicate_citations == duplicate_citations_check
    
    
    
@pytest.fixture
def publication_json():
    return load_json(os.path.join("tests", "testing_files", "publication_dict.json"))


def test_are_citations_in_pub_dict(publication_json):
    
    tokenized_citations = [{"PMID":"32095784", "DOI":"", "title":""},
                            {"PMID":"", "DOI":"10.1002/adhm.202101820", "title":""},
                            {"PMID":"", "DOI":"", "title":"Cellular Origins of EGFR-Driven Lung Cancer Cells Determine Sensitivity to Therapy."},
                            {"PMID":"1234", "DOI":"", "title":""}]
    
    is_citation_in_pubs_check = [True, True, True, False]
    
    is_citation_in_pubs = are_citations_in_pub_dict(tokenized_citations, publication_json)
    
    assert is_citation_in_pubs == is_citation_in_pubs_check
    
    
    
