# -*- coding: utf-8 -*-


import os
import time

import pytest
import shutil
import pandas

from academic_tracker.ref_srch_emails_and_reports import convert_tokenized_authors_to_str, create_report_from_template, create_tokenization_report
from academic_tracker.ref_srch_emails_and_reports import create_tabular_report, replace_keywords
from academic_tracker.fileio import load_json, read_text_from_txt


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


def test_convert_tokenized_authors_to_str(tokenized_citations):
    
    expected_string = "Powell C, Moseley H, Travis Thompson"
    
    authors = tokenized_citations[0]["authors"]
    authors.append({"last":"Thompson", "first":"Travis"})
    actual_string = convert_tokenized_authors_to_str(authors)
    
    assert expected_string == actual_string


def test_convert_tokenized_authors_to_str_no_output():
    
    expected_string = str(None)
    
    actual_string = convert_tokenized_authors_to_str([])
    
    assert expected_string == actual_string



@pytest.fixture
def publication_dict():
    return load_json(os.path.join("tests", "testing_files", "ref_srch_Crossref_pub_dict.json"))


def test_create_report_from_template_no_comparison(publication_dict, tokenized_citations):
    
    expected_text = read_text_from_txt(os.path.join("tests", "testing_files", "ref_srch_report_test1.txt"))
    
    template_string = read_text_from_txt(os.path.join("tests", "testing_files", "ref_srch_report_template_string.txt"))
    actual_text = create_report_from_template(publication_dict, [], tokenized_citations, template_string)
    
    assert expected_text == actual_text
    
    
def test_create_report_from_template_no_reference(publication_dict, tokenized_citations):
    
    expected_text = read_text_from_txt(os.path.join("tests", "testing_files", "ref_srch_report_test2.txt"))
    
    template_string = read_text_from_txt(os.path.join("tests", "testing_files", "ref_srch_report_template_string.txt"))
    for citation in tokenized_citations:
        citation["reference_line"] = ""
    actual_text = create_report_from_template(publication_dict, [True, False], tokenized_citations, template_string)
    
    assert expected_text == actual_text



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


def test_create_tabular_report_no_comparison(publication_dict, tokenized_citations, config_dict):
    
    expected_text = read_text_from_txt(os.path.join("tests", "testing_files", "ref_srch_report_tabular1.csv"))
    
    report, filename = create_tabular_report(publication_dict, config_dict, [], tokenized_citations, TESTING_DIR)
    
    actual_text = read_text_from_txt(os.path.join(TESTING_DIR, filename))
    
    assert expected_text == actual_text
    

def test_create_tabular_report_no_reference(publication_dict, tokenized_citations, config_dict):
    
    for citation in tokenized_citations:
        citation["reference_line"] = ""
    
    expected_text = read_text_from_txt(os.path.join("tests", "testing_files", "ref_srch_report_tabular2.csv"))
    
    report, filename = create_tabular_report(publication_dict, config_dict, [True, False], tokenized_citations, TESTING_DIR)
    
    actual_text = read_text_from_txt(os.path.join(TESTING_DIR, filename))
    
    assert expected_text == actual_text
    

def test_create_tabular_report_defaults(publication_dict, tokenized_citations, config_dict):
    
    config_dict["summary_report"] = {"columns":config_dict["summary_report"]["columns"]}
    
    expected_text = read_text_from_txt(os.path.join("tests", "testing_files", "ref_srch_report_tabular3.csv"))
    
    report, filename = create_tabular_report(publication_dict, config_dict, [], tokenized_citations, TESTING_DIR)
    
    actual_text = read_text_from_txt(os.path.join(TESTING_DIR, filename))
    
    assert expected_text == actual_text
    
    
def test_create_tabular_report_excel(publication_dict, tokenized_citations, config_dict):
    
    config_dict["summary_report"] = {"columns":config_dict["summary_report"]["columns"]}
    config_dict["summary_report"]["file_format"] = ".xlsx"
    config_dict["summary_report"]["filename"] = "test_name.csv"
    
    expected_text = pandas.read_excel(os.path.join("tests", "testing_files", "ref_srch_report_tabular4.xlsx"))
    
    report, filename = create_tabular_report(publication_dict, config_dict, [], tokenized_citations, TESTING_DIR)
    
    actual_text = pandas.read_excel(os.path.join(TESTING_DIR, filename))
    
    assert expected_text.to_csv() == actual_text.to_csv()
    
    


def test_replace_keywords1(publication_dict, config_dict, tokenized_citations):
    
    template = config_dict["summary_report"]["columns"]
    
    expected_template = {'Authors': 'Huan Jin, Joshua M. Mitchell, Hunter N. B. Moseley',
                         'Grants': 'None Found',
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
                         'Publication Month': 'None',
                         'Publication Day': 'None',
                         'Tok Title': 'Atom Identifiers Generated by a Neighborhood-Specific Graph Coloring Method Enable Compound Harmonization across Metabolic Databases.',
                         'Tok DOI': '10.3390/metabo10090368',
                         'Tok PMID': 'None',
                         'Tok Authors': 'Jin H, Mitchell J, Moseley H',
                         'Ref Line': 'Jin H, Mitchell J, Moseley H.  Atom Identifiers Generated by a Neighborhood-Specific Graph Coloring Method Enable Compound Harmonization across Metabolic Databases. Metabolites. 2020 September; 10(9):368-. doi: 10.3390/metabo10090368.',
                         'Comparison': 'N/A',
                         'First Author': 'Jin, Huan',
                         'Last Author': 'Moseley, Hunter N. B.',
                         'Pub_Authors': '<pub_author_last>, <pub_author_first> <pub_author_initials> <pub_author_affiliations>'}
    
    actual_template = replace_keywords(template, publication_dict, 'https://doi.org/10.3390/metabo10090368', tokenized_citations[1], None, pub_author={})
    
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
                         'Publication Month': 'None',
                         'Publication Day': 'None',
                         'Tok Title': 'Atom Identifiers Generated by a Neighborhood-Specific Graph Coloring Method Enable Compound Harmonization across Metabolic Databases.',
                         'Tok DOI': '10.3390/metabo10090368',
                         'Tok PMID': 'None',
                         'Tok Authors': 'Jin H, Mitchell J, Moseley H',
                         'Ref Line': 'N/A',
                         'Comparison': 'True',
                         'First Author': 'Jin, Huan',
                         'Last Author': 'Moseley, Hunter N. B.',
                         'Pub_Authors': 'Jin, Huan None None'}
    
    actual_template = replace_keywords(template, publication_dict, 'https://doi.org/10.3390/metabo10090368', tokenized_citations[1], True, publication_dict['https://doi.org/10.3390/metabo10090368']["authors"][0])
    
    assert expected_template == actual_template




def test_create_tokenization_report(tokenized_citations):
    
    tokenized_citations.append({"authors":[], "title":"", "DOI":"", "PMID":"", "reference_line":""})
    
    expected_text = read_text_from_txt(os.path.join("tests", "testing_files", "tokenization_report.txt"))
    
    actual_text = create_tokenization_report(tokenized_citations)
    
    assert expected_text == actual_text



@pytest.fixture(scope="module", autouse=True)
def cleanup(request):
    """Cleanup a testing directory once we are finished."""
    def remove_test_dir():
        if os.path.exists(TESTING_DIR):
            shutil.rmtree(TESTING_DIR)
    request.addfinalizer(remove_test_dir)
