# -*- coding: utf-8 -*-


import re
import os
import json
import copy

import pymed
import pytest
import xml.etree.ElementTree as ET 

from academic_tracker.fileio import load_json
from academic_tracker import __main__
from academic_tracker.helper_functions import vprint, regex_match_return, regex_group_return, regex_search_return
from academic_tracker.helper_functions import match_pub_authors_to_config_authors, match_pub_authors_to_citation_authors, match_authors_in_prev_pub
from academic_tracker.helper_functions import create_pub_dict_for_saving_PubMed, is_fuzzy_match_to_list, fuzzy_matches_to_list, is_pub_in_publication_dict 
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
    return {
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
            },
        "Hunter Moseley": {
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
          }}
    
    
@pytest.mark.parametrize("PM_author_list, returned_PM_author_list", [
        
        ([{ 'affiliation': 'Department of Neurology, University Medical Center, Johannes Gutenberg-University, Mainz, Germany.',
          'firstname': 'Carine',
          'initials': 'C',
          'lastname': 'Thalman',
          'ORCID':None},
        { 'affiliation': 'Department of Biostats, Kentucky',
          'firstname': 'Hunter',
          'initials': 'HM',
          'lastname': 'Moseley',
          'ORCID':None},],
        [{ 'affiliation': 'Department of Neurology, University Medical Center, Johannes Gutenberg-University, Mainz, Germany.',
          'firstname': 'Carine',
          'initials': 'C',
          'lastname': 'Thalman',
          'ORCID':None},
        { 'affiliation': 'Department of Biostats, Kentucky',
          'firstname': 'Hunter',
          'initials': 'HM',
          'lastname': 'Moseley',
          'author_id': 'Hunter Moseley',
          'ORCID':"0000-0003-3995-5368"},]),
           
        ([{ 'affiliation': 'Department of Neurology, University Medical Center, Johannes Gutenberg-University, Mainz, Germany.',
          'firstname': 'Carine',
          'initials': 'C',
          'lastname': 'Thalman',
          'ORCID':None}], 
            []),
        
        ([{ 'affiliation': 'Department of Biostats, Kentucky',
          'firstname': 'Hunter N. B.',
          'initials': 'HM',
          'lastname': 'Moseley',
          'ORCID':None},],
        [{ 'affiliation': 'Department of Biostats, Kentucky',
          'firstname': 'Hunter N. B.',
          'initials': 'HM',
          'lastname': 'Moseley',
          'author_id': 'Hunter Moseley',
          'ORCID':"0000-0003-3995-5368"},]),
        
        ([{ 'affiliation': 'Department of Biostats, Kentucky',
          'firstname': 'X Hunter',
          'initials': 'HM',
          'lastname': 'Moseley',
          'ORCID':None},],
        [{ 'affiliation': 'Department of Biostats, Kentucky',
          'firstname': 'X Hunter',
          'initials': 'HM',
          'lastname': 'Moseley',
          'author_id': 'Hunter Moseley',
          'ORCID':"0000-0003-3995-5368"},]),
        
        ([{ 'collectivename': 'some name',
          'ORCID':None},],
        [{ 'collectivename': 'some name',
          'author_id': 'Hunter Moseley',
          'ORCID':"0000-0003-3995-5368"},]),
        
        ([{ 'affiliation': 'Department of Biostats, Kentucky',
          'firstname': 'Hunter N. B.',
          'initials': 'HM',
          'lastname': None,
          'ORCID':None},],
        []),
        ])
        
        
        
def test_match_pub_authors_to_config_authors(authors_json_file, PM_author_list, returned_PM_author_list):
    if "collectivename" in PM_author_list[0]:
        authors_json_file["Hunter Moseley"]["collective_name"] = "some name"
    
    assert match_pub_authors_to_config_authors(authors_json_file, PM_author_list) == returned_PM_author_list



def test_match_authors_in_pub_PubMed_collective_names():
    
    citation_authors = [
                      {
                        "initials": "J",
                        "last": "Mitchell"
                      },
                      {"collective_name": "some name"},
                      {
                        "initials": "R",
                        "last": "Flight"
                      },
                      {
                        "initials": "H",
                        "last": "Moseley"
                      }
                    ]
    
    publication_authors = [
        {"collectivename": "some name",
          "ORCID": None}
        ]
    
    assert match_pub_authors_to_citation_authors(citation_authors, publication_authors) == True
    
    
def test_match_authors_in_pub_PubMed_ORCID():
    
    citation_authors = [
                      {
                        "initials": "J",
                        "last": "Mitchell"
                      },
                      {"ORCID": "asdf"},
                      {
                        "initials": "R",
                        "last": "Flight"
                      },
                      {
                        "initials": "H",
                        "last": "Moseley"
                      }
                    ]
    
    publication_authors = [
        {"ORCID": "asdf",
          "lastname": "qwer"}
        ]
    
    assert match_pub_authors_to_citation_authors(citation_authors, publication_authors) == True


@pytest.fixture
def pub_no_PMCID():
    xml_path = os.path.join("tests", "testing_files", "no_author.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())


def test_modify_pub_dict_for_saving_no_PMCID(pub_no_PMCID):
    modified_pub = load_json(os.path.join("tests", "testing_files", "PubMed_modified_to_save_no_PMCID.json"))
            
    _, pub_to_check = create_pub_dict_for_saving_PubMed(pub_no_PMCID)
    
    # with open(os.path.join("tests", "testing_files", "PubMed_modified_to_save_no_PMCID_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(pub_to_check, indent=2, sort_keys=True))
    
    assert pub_to_check == modified_pub



@pytest.fixture
def pub_with_PMCID():
    xml_path = os.path.join("tests", "testing_files", "pub_with_PMCID.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())


def test_modify_pub_dict_for_saving_with_PMCID(pub_with_PMCID):
    modified_pub = load_json(os.path.join("tests", "testing_files", "PubMed_modified_to_save_with_PMCID.json"))
            
    _, pub_to_check = create_pub_dict_for_saving_PubMed(pub_with_PMCID, True)
    
    # with open(os.path.join("tests", "testing_files", "PubMed_modified_to_save_with_PMCID_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(pub_to_check, indent=2, sort_keys=True))
    
    assert pub_to_check == modified_pub



@pytest.fixture
def modified_PubMed_XML():
    xml_path = os.path.join("tests", "testing_files", "modified_PubMed_XML.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())


def test_modify_pub_dict_for_saving_rare_cases(modified_PubMed_XML):
    modified_pub = load_json(os.path.join("tests", "testing_files", "PubMed_rare_cases.json"))
            
    _, pub_to_check = create_pub_dict_for_saving_PubMed(modified_PubMed_XML, True)
    
    # with open(os.path.join("tests", "testing_files", "PubMed_rare_cases_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(pub_to_check, indent=2, sort_keys=True))
    
    assert pub_to_check == modified_pub



@pytest.fixture
def collective_author_XML():
    xml_path = os.path.join("tests", "testing_files", "collective_author_XML.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())


def test_match_authors_in_prev_pub(collective_author_XML):
    _, pub_to_check = create_pub_dict_for_saving_PubMed(collective_author_XML, True)
    new_author_list = copy.deepcopy(pub_to_check['authors'])
    final_list = copy.deepcopy(pub_to_check['authors'])
    for author in new_author_list[0:-1]:
        author['author_id'] = ''
    
    pub_to_check['authors'].append({'author_id':None, 'firstname':None, 'lastname':None, 'ORCID':'some id'})
    new_author_list.append({'author_id':123, 'firstname':None, 'lastname':None, 'ORCID':'some id'})
    final_list.append({'author_id':123, 'firstname':None, 'lastname':None, 'ORCID':'some id'})
    
    new_author_list.append({'author_id':456, 'firstname':'name', 'lastname':'last', 'ORCID':'some id2'})
    final_list.append({'author_id':456, 'firstname':'name', 'lastname':'last', 'ORCID':'some id2'})
    
    pub_to_check['authors'].append({'author_id':None, 'collectivename':'some name', 'ORCID':None})
    new_author_list.append({'author_id':None, 'collectivename':'some name', 'ORCID':None})
    final_list.append({'author_id':None, 'collectivename':'some name', 'ORCID':None})
        
    combined_author_list = match_authors_in_prev_pub(pub_to_check['authors'], new_author_list)    
        
    assert [item in final_list for item in combined_author_list]



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
    
    tokenized_citations = [{"PMID":"35313030", "DOI":"", "title":""},
                            {"PMID":"", "DOI":"10.1038/s41467-023-35784-x", "title":""},
                            {"PMID":"", "DOI":"", "title":"kegg_pull: a software package for the RESTful access and pulling from the Kyoto Encyclopedia of Gene and Genomes."},
                            {"PMID":"1234", "DOI":"", "title":""}]
    
    is_citation_in_pubs_check = [True, True, True, False]
    
    is_citation_in_pubs = are_citations_in_pub_dict(tokenized_citations, publication_json)
    
    assert is_citation_in_pubs == is_citation_in_pubs_check
    
    
    
