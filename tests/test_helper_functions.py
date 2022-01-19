# -*- coding: utf-8 -*-

import pytest
import re
import os
import pymed
import xml.etree.ElementTree as ET 
from academic_tracker.helper_functions import parse_string_for_pub_info, regex_match_return, regex_group_return, regex_search_return
from academic_tracker.helper_functions import match_authors_in_pub_PubMed, match_authors_in_pub_Crossref
from academic_tracker.helper_functions import modify_pub_dict_for_saving, overwrite_config_with_CLI, is_fuzzy_match_to_list, is_pub_in_publication_dict 
from academic_tracker.helper_functions import create_authors_by_project_dict, adjust_author_attributes
from fixtures import publication_dict, pub_with_grants, pub_with_matching_author, passing_config, authors_by_project_dict


def test_parse_string_for_pub_info():
    
    document_string = "doi:10.1515/reveh-2020-0092 PMID:33001857 PMCID:PMC7933073\n" +\
                         "doi:10.1111/gwmr.12449 \n" +\
                         "doi:10.3390/membranes11010018 PMID:33375603 \n" +\
                         "asdfasdfasdfadsf"
    DOI_regex = r"(?i).*doi:\s*([^\s]+\w).*"
    PMID_regex = r"(?i).*pmid:\s*(\d+).*"
    PMCID_regex = r"(?i).*pmcid:\s*(pmc\d+).*"
    
    output_list = [{"DOI": "10.1111/gwmr.12449", "PMID": "", "line": "doi:10.1111/gwmr.12449 "},
                   {"DOI": "10.3390/membranes11010018", "PMID": "33375603", "line": "doi:10.3390/membranes11010018 PMID:33375603 "}]
    
    assert parse_string_for_pub_info(document_string, DOI_regex, PMID_regex, PMCID_regex) == output_list
    


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
    xml_path = os.path.join("testing_files", "no_author.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())


def test_modify_pub_dict_for_saving_no_PMCID(pub_no_PMCID):
    modified_pub = {'pubmed_id': '34601942',
                     'title': 'Genome-Wide Association Study of Peripheral Artery Disease.',
                     'abstract': 'Peripheral artery disease (PAD) affects >200 million people worldwide and is associated with high mortality and morbidity. We sought to identify genomic variants associated with PAD overall and in the contexts of diabetes and smoking status.\nWe identified genetic variants associated with PAD and then meta-analyzed with published summary statistics from the Million Veterans Program and UK Biobank to replicate their findings. Next, we ran stratified genome-wide association analysis in ever smokers, never smokers, individuals with diabetes, and individuals with no history of diabetes and corresponding interaction analyses, to identify variants that modify the risk of PAD by diabetic or smoking status.\nWe identified 5 genome-wide significant (\nOur analyses confirm the published genetic associations with PAD and identify novel variants that may influence susceptibility to PAD in the context of diabetes or smoking status.',
                     'keywords': ['diabetes',
                      'genome-wide association study',
                      'peripheral vascular disease',
                      'smoking'],
                     'journal': 'Circulation. Genomic and precision medicine',
                     'publication_date': {'year': 2021, 'month': 10, 'day': 5},
                     'methods': None,
                     'conclusions': None,
                     'results': 'We identified 5 genome-wide significant (',
                     'copyrights': None,
                     'doi': '10.1161/CIRCGEN.119.002862',
                     'grants': [],
                     'PMCID': None}
            
    pub_to_check = modify_pub_dict_for_saving(pub_no_PMCID)
    del pub_to_check["authors"]
    
    assert pub_to_check == modified_pub



@pytest.fixture
def pub_with_PMCID():
    xml_path = os.path.join("testing_files", "pub_with_PMCID.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())


def test_modify_pub_dict_for_saving_with_PMCID(pub_with_PMCID):
    modified_pub = {'pubmed_id': '33001857',
                     'title': 'Balancing incomplete COVID-19 evidence and local priorities: risk communication and stakeholder engagement strategies for school re-opening.',
                     'abstract': 'In the midst of the COVID-19 pandemic, United States (U.S.) educational institutions must weigh incomplete scientific evidence to inform decisions about how best to re-open schools without sacrificing public health. While many communities face surging case numbers, others are experiencing case plateaus or even decreasing numbers. Simultaneously, some U.S. school systems face immense infrastructure challenges and resource constraints, while others are better positioned to resume face-to-face instruction. In this review, we first examine potential engineering controls to reduce SARS-CoV-2 exposures; we then present processes whereby local decision-makers can identify and partner with scientists, faculty, students, parents, public health officials, and others to determine the controls most appropriate for their communities. While no solution completely eliminates risks of SARS-CoV-2 exposure and illness, this mini-review discusses engaged decision and communication processes that incorporate current scientific knowledge, school district constraints, local tolerance for health risk, and community priorities to help guide schools in selecting and implementing re-opening strategies that are acceptable, feasible, and context-specific.',
                     'keywords': ['COVID-19',
                      'airborne transmission',
                      'children health',
                      'indoor air',
                      'stakeholder engagement'],
                     'journal': 'Reviews on environmental health',
                     'publication_date': {'year': 2020, 'month': 10, 'day': 2},
                     'methods': None,
                     'conclusions': None,
                     'results': None,
                     'copyrights': '© 2020 Walter de Gruyter GmbH, Berlin/Boston.',
                     'doi': '10.1515/reveh-2020-0092',
                     'grants': ['G08 LM013185', 'P30 ES026529', 'P42 ES007380', 'P42 ES007381'],
                     'PMCID': 'PMC7933073'}
            
    pub_to_check = modify_pub_dict_for_saving(pub_with_PMCID)
    del pub_to_check["authors"]
    
    assert pub_to_check == modified_pub



def test_overwrite_config_with_CLI():
    config_file = {"project_descriptions":{
                  "Core A Administrative Core": {
                    "affiliations": [
                      "kentucky"
                    ],
                    "authors": [
                      "Kelly Pennell",
                      "Bernhard Hennig",
                      "Angela Gutierrez"
                    ],
                    "cc_email": [],
                    "cutoff_year": 2020,
                    "email_subject": "New PubMed Publications",
                    "email_template": "Hey <author_first_name>,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\n<total_pubs>\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu",
                    "from_email": "ptth222@uky.edu",
                    "grants": [
                      "P42ES007380",
                      "P42 ES007380"
                    ]
                  }}}
    
    args = {"--grants":["asdf"], "--cutoff_year":2018, "--from_email":"email@email.com", "--cc_email":["asdf@email.com"], "--affiliations":["qwer"]}
    
    modified_config = {"project_descriptions":{
                      "Core A Administrative Core": {
                        "affiliations": ["qwer"],
                        "authors": [
                          "Kelly Pennell",
                          "Bernhard Hennig",
                          "Angela Gutierrez"
                        ],
                        "cc_email": ["asdf@email.com"],
                        "cutoff_year": 2018,
                        "email_subject": "New PubMed Publications",
                        "email_template": "Hey <author_first_name>,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\n<total_pubs>\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu",
                        "from_email": "email@email.com",
                        "grants": ["asdf"]
                      }}}
    
    assert overwrite_config_with_CLI(config_file, args) == modified_config
    


@pytest.mark.parametrize("str_to_match, list_to_matched, is_match", [
        
        ("asdf", ["qwer", "asdf", "zxcv"], True),
        ("asdf", ["qwer", "zxcv"], False)
        ]) 

def test_is_fuzzy_match_to_list(str_to_match, list_to_matched, is_match):
    assert is_fuzzy_match_to_list(str_to_match, list_to_matched) == is_match



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
    
    authors_by_project_dict_check = create_authors_by_project_dict(passing_config, authors_json_file) 
    captured = capsys.readouterr()
    
    assert authors_by_project_dict_check == authors_by_project_dict and captured.out == "Warning: The author, Andrew Morris, in the project 1 project of the project tracking configuration file could not be found in the authors' JSON file.\n"
    
    
    
def test_adjust_author_attributes(authors_by_project_dict, authors_json_file):
    
    authors_by_project_dict["project 1"]["Hunter Moseley"]["affiliations"] = ["asdf"]
    authors_by_project_dict["project 1"]["Hunter Moseley"]["grants"] = ["asdf", "qwer"]
    authors_by_project_dict["project 1"]["Hunter Moseley"]["cutoff_year"] = 2000
    
    del authors_by_project_dict["project 2"]["Hunter Moseley"]["affiliations"]
    del authors_by_project_dict["project 2"]["Hunter Moseley"]["grants"]
    del authors_by_project_dict["project 2"]["Hunter Moseley"]["cutoff_year"]
    
    modified_authors_json_file = {'Hunter Moseley': {'ORCID': '0000-0003-3995-5368',
                                  'affiliations': set(['asdf', 'kentucky']),
                                  'cutoff_year': 2000,
                                  'email': 'hunter.moseley@gmail.com',
                                  'first_name': 'Hunter',
                                  'last_name': 'Moseley',
                                  'pubmed_name_search': 'Hunter Moseley',
                                  'scholar_id': 'ctE_FZMAAAAJ',
                                  'grants': set(['asdf', 'P42ES007380', 'qwer', 'P42 ES007380'])},
                                 'Isabel Escobar': {'ORCID': '0000-0001-9269-5927',
                                  'affiliations': set(['kentucky']),
                                  'cutoff_year': 2020,
                                  'email': 'isabel.escobar@uky.edu',
                                  'first_name': 'Isabel',
                                  'last_name': 'Escobar',
                                  'pubmed_name_search': 'Isabel Escobar',
                                  'scholar_id': 'RfB5L8kAAAAJ',
                                  'grants': set(['P42ES007380', 'P42 ES007380'])}}
        
    adjust_author_attributes(authors_by_project_dict, authors_json_file)
    
    for author_attr in authors_json_file.values():
        author_attr["affiliations"] = set(author_attr["affiliations"])
        author_attr["grants"] = set(author_attr["grants"])
    
    assert authors_json_file == modified_authors_json_file
    
    
    
    
    
    
    
    
