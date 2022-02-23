# -*- coding: utf-8 -*-

import os

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
    with open(os.path.join("testing_files", "pymed_pubs.pkl"), "rb") as f:
        articles = pickle.load(f)
    return articles


@pytest.fixture
def expected_publication_dict():
    return {'https://doi.org/10.1016/j.chroma.2021.462426': {'pubmed_id': '34352431',
  'title': 'Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry.',
  'abstract': 'We developed and validated a method for direct determination of per- and polyfluoroalkylated substances (PFASs) in environmental water samples without prior sample concentration. Samples are centrifuged and supernatants passed through an Acrodisc Filter (GXF/GHP 0.2\xa0\xa0um, 25\xa0\xa0mm diameter). After addition of ammonium acetate, samples are analyzed by UPLC-MS/MS using an AB Sciex 6500 plus Q-Trap mass spectrometer operated in negative multiple reaction-monitoring (MRM) mode. The instrument system incorporates a delay column between the pumps and autosampler to mitigate interference from background PFAS. The method monitors eight short-/long-chain PFAS which are identified by monitoring specific precursor product ion pairs and by their retention times and quantified using isotope mass-labeled internal standard based calibration plots. Average spiked recoveries (n\xa0=\xa08) of target analytes ranged from 84 to 110% with 4-9% relative standard deviation (RSD). The mean spiked recoveries (n\xa0=\xa08) of four surrogates were 94-106% with 3-8% RSD. For continuous calibration verification (CCV), average spiked recoveries (n\xa0=\xa08) for target analytes ranged from 88 to 114% with 4-11% RSD and for surrogates ranged from 104-112% with 3-11% RSD. The recoveries (n\xa0=\xa06) of matrix spike (MX), matrix spike duplicate (MXD), and field reagent blank (FRB) met our acceptance criteria. The limit of detection for the target analytes was between 0.007 and 0.04\xa0ng/mL. The method was used to measure PFAS in tap water and surface water.',
  'keywords': ['Acrodisc filtration',
   'Direct injection',
   'Drinking and surface water',
   'PFAS',
   'UPLC-MS/MS'],
  'journal': 'Journal of chromatography. A',
  'publication_date': {'year': 2021, 'month': 8, 'day': 6},
  'authors': [{'lastname': 'Mottaleb',
    'firstname': 'M Abdul',
    'initials': 'MA',
    'affiliation': 'Superfund Research Center, University of Kentucky, Lexington KY, 40506, United States; Center for Appalachian Research in Environmental Sciences, University of Kentucky, Lexington KY, 40506, United States; Division of Cardiovascular, Medicine, College of Medicine, University of Kentucky and Lexington VA Medical Center, Lexington, KY, 40536, United States. a.j.morris@uky.edu; Pressent address: Institute of Drug & Biotherapeutic Innovation, DRC, 1100 South Grand Blvd, Saint Louis University, Saint Louis, MO 63104 United States. Electronic address: m.a.mottaleb@uky.edu.'},
   {'lastname': 'Ding',
    'firstname': 'Qunxing X',
    'initials': 'QX',
    'affiliation': 'Department of Biology, College of Arts and Sciences, Kent State University, Kent, OH, 44242, United States. Electronic address: qding@kent.edu.'},
   {'lastname': 'Pennell',
    'firstname': 'Kelly G',
    'initials': 'KG',
    'affiliation': 'Superfund Research Center, University of Kentucky, Lexington KY, 40506, United States; Center for Appalachian Research in Environmental Sciences, University of Kentucky, Lexington KY, 40506, United States; Department of Civil Engineering, College of Engineering, University of Kentucky, Lexington KY, 40506, United States. Electronic address: kellypennell@uky.edu.',},
   {'lastname': 'Haynes',
    'firstname': 'Erin N',
    'initials': 'EN',
    'affiliation': 'Superfund Research Center, University of Kentucky, Lexington KY, 40506, United States; Center for Appalachian Research in Environmental Sciences, University of Kentucky, Lexington KY, 40506, United States; Department of Epidemiology, College of Public Health, University of Kentucky, Lexington KY, 40536, United States. Electronic address: erin.haynes@uky.edu.',},
   {'lastname': 'Morris',
    'firstname': 'Andrew J',
    'initials': 'AJ',
    'affiliation': 'Superfund Research Center, University of Kentucky, Lexington KY, 40506, United States; Center for Appalachian Research in Environmental Sciences, University of Kentucky, Lexington KY, 40506, United States; Division of Cardiovascular, Medicine, College of Medicine, University of Kentucky and Lexington VA Medical Center, Lexington, KY, 40536, United States. a.j.morris@uky.edu; Pressent address: Institute of Drug & Biotherapeutic Innovation, DRC, 1100 South Grand Blvd, Saint Louis University, Saint Louis, MO 63104 United States. Electronic address: a.j.morris@uky.edu.',
    'author_id': 'Andrew Morris'}],
  'methods': None,
  'conclusions': None,
  'results': None,
  'copyrights': 'Copyright © 2021. Published by Elsevier B.V.',
  'doi': '10.1016/j.chroma.2021.462426',
  'grants': ['P30 ES026529'],
  'PMCID': None}}


def test_build_pub_dict_from_PMID(pymed_query, mocker, expected_publication_dict):
    def mock_query(*args, **kwargs):
        return pymed_query
    mocker.patch("academic_tracker.ref_srch_webio.pymed.PubMed.query", mock_query)
    test_publication_dict = build_pub_dict_from_PMID(['34352431', '11111111'], "ptth222@uky.edu")
    assert test_publication_dict == expected_publication_dict



## For whatever reason I couldn't pickle a list of pymed articles like I did before, 
## so I saved them as a string. Here they are loaded back in and converted to an article.
@pytest.fixture
def ref_pymed_query():
    xml_strings = load_json(os.path.join("testing_files", "ref_srch_PubMed_pubs.json"))
    return [pymed.article.PubMedArticle(xml_element=ET.fromstring(string)) for string in xml_strings]


@pytest.fixture
def tokenized_citations():
    tokenized_citations = load_json(os.path.join("testing_files", "tokenized_citations.json"))
    return [tokenized_citations[i] for i in [6,8,63]]
    


def test_search_references_on_PubMed(tokenized_citations, ref_pymed_query, mocker):
    def mock_query(*args, **kwargs):
        return ref_pymed_query
    mocker.patch("academic_tracker.ref_srch_webio.pymed.PubMed.query", mock_query)
    
    expected_publication_dict = load_json(os.path.join("testing_files", "ref_srch_publication_dict.json"))
    expected_citation_keys = load_json(os.path.join("testing_files", "ref_srch_keys_for_citations.json"))
    
    actual_publication_dict, actual_citation_keys = search_references_on_PubMed(tokenized_citations, "ptth222@uky.edu")
    
    assert expected_publication_dict == actual_publication_dict
    assert expected_citation_keys == actual_citation_keys
    



def test_search_references_on_Crossref(tokenized_citations, mocker):
    def query_generator():
        queries = load_json(os.path.join("testing_files", "ref_srch_Crossref_queries.json"))
        for query in queries:
            yield query
            
    queries = query_generator()
        
    def mock_query(*args, **kwargs):
        return next(queries)
    mocker.patch("academic_tracker.ref_srch_webio.habanero.Crossref.works", mock_query)
       
    expected_pub_dict = load_json(os.path.join("testing_files", "ref_srch_Crossref_pub_dict.json"))
    expected_citation_keys = load_json(os.path.join("testing_files", "ref_srch_Crossref_keys_for_citations.json"))
    
    actual_pub_dict, actual_citation_keys = search_references_on_Crossref(tokenized_citations, "ptth222@uky.edu")
        
    assert actual_pub_dict == expected_pub_dict
    assert actual_citation_keys == expected_citation_keys




def test_parse_myncbi_citations(mocker):
    def page_generator():
        pages = load_json(os.path.join("testing_files", "myncbi_webpages.json"))
        for page in pages:
            yield page
            
    pages = page_generator()
        
    def mock_query(*args, **kwargs):
        return next(pages)
    mocker.patch("academic_tracker.ref_srch_webio.webio.get_url_contents_as_str", mock_query)
    
    expected_tokenized_citations = load_json(os.path.join("testing_files", "tokenized_citations.json"))
    
    actual_tokenized_citations = parse_myncbi_citations("asdf")
    
    assert expected_tokenized_citations == actual_tokenized_citations



## Test that the JSON read in works and finds and eliminates duplicates.
def test_tokenize_reference_input_JSON(capsys):
    
    expected_tokenized_citations = load_json(os.path.join("testing_files", "tokenized_citations_duplicates_removed.json"))
    
    actual_tokenized_citations = tokenize_reference_input(os.path.join("testing_files", "tokenized_citations.json"), False)
    captured = capsys.readouterr()
    
    assert expected_tokenized_citations == actual_tokenized_citations
    ## There should be something about duplicates in stdout.
    assert len(captured.out) > 0



def test_tokenize_reference_input_html(mocker):
    def mock_query(*args, **kwargs):
        return read_text_from_txt(os.path.join("testing_files", "nsf_award_page.txt"))
    mocker.patch("academic_tracker.ref_srch_webio.webio.clean_tags_from_url", mock_query)
    
    expected_tokenized_citations = load_json(os.path.join("testing_files", "tokenized_nsf_award_page.json"))
    
    actual_tokenized_citations = tokenize_reference_input("https://www.nsf.gov/awardsearch/showAward?AWD_ID=1419282", False)
    
    assert expected_tokenized_citations == actual_tokenized_citations



def test_tokenize_reference_input_no_html_content(capsys, mocker):
    def mock_query(*args, **kwargs):
        return read_text_from_txt(os.path.join("testing_files", "empty_file.txt"))
    mocker.patch("academic_tracker.ref_srch_webio.webio.clean_tags_from_url", mock_query)
    
    with pytest.raises(SystemExit):
        tokenize_reference_input("https://www.nsf.gov/awardsearch/showAward?AWD_ID=1419282", False)
    captured = capsys.readouterr()
    
    assert captured.out == "Nothing was read from the URL. Make sure the address is correct.\n"



def test_tokenize_reference_input_docx():
    
    expected_tokenized_citations = load_json(os.path.join("testing_files", "tokenized_ref_test.json"))
    
    actual_tokenized_citations = tokenize_reference_input(os.path.join("testing_files", "reference_test.docx"), False)
    
    assert expected_tokenized_citations == actual_tokenized_citations



def test_tokenize_reference_input_txt():
    
    expected_tokenized_citations = load_json(os.path.join("testing_files", "tokenized_ref_test.json"))
    
    actual_tokenized_citations = tokenize_reference_input(os.path.join("testing_files", "reference_test.txt"), False)
    
    assert expected_tokenized_citations == actual_tokenized_citations



def test_tokenize_reference_input_wrong_file_extension(capsys):
    
    with pytest.raises(SystemExit):
        tokenize_reference_input("asdf.asdf", False)
    captured = capsys.readouterr()
    
    assert captured.out == "Unknown file type for reference file.\n"



def test_tokenize_reference_input_empty_file(capsys):
    
    with pytest.raises(SystemExit):
        tokenize_reference_input(os.path.join("testing_files", "empty_file.txt"), False)
    captured = capsys.readouterr()
    
    assert captured.out == "Nothing was read from the reference file. Make sure the file is not empty or is a supported file type.\n"



def test_tokenize_reference_input_MEDLINE():
    
    expected_tokenized_citations = load_json(os.path.join("testing_files", "tokenized_MEDLINE.json"))
    
    actual_tokenized_citations = tokenize_reference_input(os.path.join("testing_files", "medline.txt"), True)
    
    assert expected_tokenized_citations == actual_tokenized_citations



def test_tokenize_reference_input_no_references(capsys):
    
    with pytest.raises(SystemExit):
        tokenize_reference_input(os.path.join("testing_files", "testing_text.txt"), False)
    captured = capsys.readouterr()
    
    assert captured.out == "Warning: Could not tokenize any citations in provided reference. Check setup and formatting and try again.\n"







