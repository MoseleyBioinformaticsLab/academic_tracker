# -*- coding: utf-8 -*-


import os
import time
import json

import pytest
import shutil

from academic_tracker.emails_and_reports_helpers import _replace_keywords
from academic_tracker.fileio import load_json


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
    return load_json(os.path.join("tests", "testing_files", "tokenized_citations_for_report_test.json"))


@pytest.fixture
def publication_dict():
    return load_json(os.path.join("tests", "testing_files", "ref_srch_Crossref_pub_dict.json"))


@pytest.fixture
def config_dict():
    config_dict = {"summary_report":{"columns":{'Authors': '<authors>',
                                                'Grants': '<grants>',
                                                'Abstract': '<abstract>',
                                                'Conclusions': '<conclusions>',
                                                'Copyrights': '<copyrights>',
                                                'DOI': '<DOI>',
                                                'Journal': '<journal>',
                                                'Keywords': '<keywords>',
                                                'Methods': '<methods>',
                                                'PMID': '<PMID>',
                                                'Results': '<results>',
                                                'Title': '<title>',
                                                'PMCID': '<PMCID>',
                                                'Publication Year': '<publication_year>',
                                                'Publication Month': '<publication_month>',
                                                'Publication Day': '<publication_day>',
                                                'Tok Title': '<tok_title>',
                                                'Tok DOI': '<tok_DOI>',
                                                'Tok PMID': '<tok_PMID>',
                                                'Tok Authors': '<tok_authors>',
                                                'Ref Line': '<ref_line>',
                                                'Comparison': '<is_in_comparison_file>',
                                                'First Author': '<first_author>',
                                                'Last Author': '<last_author>',
                                                'Pub_Authors': '<pub_author_last>, <pub_author_first> <pub_author_initials> <pub_author_affiliations>'},
                                     "column_order":['Authors', 'Grants', 'Abstract', 'Conclusions', 'Copyrights', 'DOI', 'Journal', 'Keywords', 'Methods',
                                                     'PMID', 'Results', 'Title', 'PMCID', 'Publication Year', 'Publication Month', 'Publication Day',
                                                     'Tok Title', 'Tok DOI', 'Tok PMID', 'Tok Authors', 'Ref Line', 'Comparison', 'First Author', 
                                                     'Last Author', 'Pub_Authors'],
                                     "sort":["Authors"],
                                     "file_format":"csv",
                                     "filename":"test_name.csv",
                                     "separator":"\t"}}
    
    return config_dict


def test_replace_keywords1(publication_dict, config_dict, tokenized_citations):
    
    template = config_dict["summary_report"]["columns"]
    
    expected_template = {'Authors': 'Huan Jin, Joshua M. Mitchell, Hunter N. B. Moseley',
                          'Grants': '1419282',
                          'Abstract': 'None',
                          'Conclusions': 'None',
                          'Copyrights': 'None',
                          'DOI': '10.3390/metabo10090368',
                          'Journal': 'MDPI AG',
                          'Keywords': 'None',
                          'Methods': 'None',
                          'PMID': 'None',
                          'Results': 'None',
                          'Title': 'Atom Identifiers Generated by a Neighborhood-Specific Graph Coloring Method Enable Compound Harmonization across Metabolic Databases',
                          'PMCID': 'None',
                          'Publication Year': '2020',
                          'Publication Month': '9',
                          'Publication Day': '11',
                          'Tok Title': 'Atom Identifiers Generated by a Neighborhood-Specific Graph Coloring Method Enable Compound Harmonization across Metabolic Databases.',
                          'Tok DOI': '10.3390/metabo10090368',
                          'Tok PMID': 'None',
                          'Tok Authors': 'Jin H, Mitchell J, Moseley H',
                          'Ref Line': 'Jin H, Mitchell J, Moseley H.  Atom Identifiers Generated by a Neighborhood-Specific Graph Coloring Method Enable Compound Harmonization across Metabolic Databases. Metabolites. 2020 September; 10(9):368-. doi: 10.3390/metabo10090368.',
                          'Comparison': 'N/A',
                          'First Author': 'Jin, Huan',
                          'Last Author': 'Moseley, Hunter N. B.',
                          'Pub_Authors': '<pub_author_last>, <pub_author_first> <pub_author_initials> <pub_author_affiliations>'}
    
    actual_template = _replace_keywords(template, 
                                        publication_dict, 
                                        None, 
                                        pub='https://doi.org/10.3390/metabo10090368', 
                                        tokenized_citation=tokenized_citations[1], 
                                        is_citation_in_prev_pubs=None, 
                                        pub_author={})
    # with open(os.path.join("tests", "testing_files", "aaa.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_template, indent=2, sort_keys=False))
    
    assert expected_template == actual_template
    

    
def test_replace_keywords2(publication_dict, config_dict, tokenized_citations):
    
    template = config_dict["summary_report"]["columns"]
    publication_dict['https://doi.org/10.3390/metabo10090368']["grants"] = ["asdf"]
    tokenized_citations[1]["reference_line"] = ""
    
    expected_template = {'Authors': 'Huan Jin, Joshua M. Mitchell, Hunter N. B. Moseley',
                          'Grants': 'asdf',
                          'Abstract': 'None',
                          'Conclusions': 'None',
                          'Copyrights': 'None',
                          'DOI': '10.3390/metabo10090368',
                          'Journal': 'MDPI AG',
                          'Keywords': 'None',
                          'Methods': 'None',
                          'PMID': 'None',
                          'Results': 'None',
                          'Title': 'Atom Identifiers Generated by a Neighborhood-Specific Graph Coloring Method Enable Compound Harmonization across Metabolic Databases',
                          'PMCID': 'None',
                          'Publication Year': '2020',
                          'Publication Month': '9',
                          'Publication Day': '11',
                          'Tok Title': 'Atom Identifiers Generated by a Neighborhood-Specific Graph Coloring Method Enable Compound Harmonization across Metabolic Databases.',
                          'Tok DOI': '10.3390/metabo10090368',
                          'Tok PMID': 'None',
                          'Tok Authors': 'Jin H, Mitchell J, Moseley H',
                          'Ref Line': 'N/A',
                          'Comparison': 'True',
                          'First Author': 'Jin, Huan',
                          'Last Author': 'Moseley, Hunter N. B.',
                          'Pub_Authors': 'Jin, Huan None None'}
    
    actual_template = _replace_keywords(template, 
                                        publication_dict,
                                        None,
                                        pub='https://doi.org/10.3390/metabo10090368', 
                                        tokenized_citation=tokenized_citations[1], 
                                        is_citation_in_prev_pubs=True, 
                                        pub_author=publication_dict['https://doi.org/10.3390/metabo10090368']["authors"][0])
    # with open(os.path.join("tests", "testing_files", "aaa.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_template, indent=2, sort_keys=False))
    
    assert expected_template == actual_template





@pytest.fixture
def publication_dict2():
    return load_json(os.path.join("tests", "testing_files", "publication_dict_truncated.json"))

@pytest.fixture
def config_dict2():
    return load_json(os.path.join("tests", "testing_files", "config_truncated.json"))


def test_replace_keywords(publication_dict2, config_dict2):
    
    template = {"Col1":"<project_name>", "Col2":"<author_first>", "Col3":"<title>", "Col4":"<pub_author_first>"}
    
    expected_template = {"Col1":"Project 1", "Col2":"Hunter", "Col3":"Identifying and sharing per-and polyfluoroalkyl substances hot-spot areas and exposures in drinking water.", "Col4":"Travis"}
    
    pub_author = {"firstname":"Travis",
                  "lastname":"Thompson",
                  "initials":"P.T.T.",
                  "affiliation":"University of Kentucky",
                  "ORCID": "0000-0002-8198-1327",
                  "author_id": "Travis Thompson"}
    
    actual_template = _replace_keywords(template, 
                                        publication_dict2, 
                                        config_dict2, 
                                        project_name="Project 1", 
                                        author="Hunter Moseley", 
                                        pub="https://doi.org/10.1038/s41597-023-02277-x", 
                                        pub_author=pub_author)
    
    assert expected_template == actual_template
    

def test_replace_keywords_more_keywords(publication_dict2, config_dict2):
    
    template = {"Col1":"<first_author>", "Col2":"<last_author>", "Col3":"<authors>", "Col4":"<grants>", "Col5":"<publication_year>"}
    
    expected_template = {"Col1":'Ojha, Sweta', "Col2":'Pennell, Kelly G', "Col3":'Sweta Ojha, P Travis Thompson, Christian D Powell, Hunter N B Moseley, Kelly G Pennell', "Col4":'P42 ES007380, 2020026', "Col5":"2023"}
    
    pub_author = {"firstname":"Travis",
                  "lastname":"Thompson",
                  "initials":"P.T.T.",
                  "affiliation":"University of Kentucky",
                  "ORCID": "0000-0002-8198-1327",
                  "author_id": "Travis Thompson"}
    
    actual_template = _replace_keywords(template, 
                                        publication_dict2, 
                                        config_dict2, 
                                        project_name="Project 1", 
                                        author="Hunter Moseley", 
                                        pub="https://doi.org/10.1038/s41597-023-02277-x", 
                                        pub_author=pub_author)
    
    assert expected_template == actual_template
    
    
    
def test_replace_keywords_no_change(publication_dict2, config_dict2):
    
    template = {"Col1":"<project_name>", "Col2":"<author_first>", "Col3":"<title>", "Col4":"<pub_author_first>"}
    
    expected_template = template
    
    actual_template = _replace_keywords(template, 
                                        publication_dict2, 
                                        config_dict2)
    
    assert expected_template == actual_template







@pytest.fixture(scope="module", autouse=True)
def cleanup(request):
    """Cleanup a testing directory once we are finished."""
    def remove_test_dir():
        if os.path.exists(TESTING_DIR):
            shutil.rmtree(TESTING_DIR)
    request.addfinalizer(remove_test_dir)

