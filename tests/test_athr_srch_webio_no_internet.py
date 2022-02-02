# -*- coding: utf-8 -*-

import os

import pytest
import pickle
import requests

from fixtures import  authors_dict
from academic_tracker.athr_srch_webio import search_PubMed_for_pubs, search_ORCID_for_pubs, search_Google_Scholar_for_pubs
from academic_tracker.athr_srch_webio import search_Crossref_for_pubs
from academic_tracker.fileio import load_json



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




def test_request_pubs_from_pubmed_success(pymed_query, mocker, authors_dict, expected_publication_dict):
    def mock_query(*args, **kwargs):
        return pymed_query
    mocker.patch("academic_tracker.athr_srch_webio.pymed.PubMed.query", mock_query)
    test_publication_dict = search_PubMed_for_pubs({}, authors_dict, "ptth222@uky.edu", False)
    assert test_publication_dict == expected_publication_dict



@pytest.fixture
def ORCID_query():
    return load_json(os.path.join("testing_files", "ORCID_query.json"))


def test_search_ORCID_for_pubs(ORCID_query, authors_dict, mocker):
    def mock_query(*args, **kwargs):
        return ORCID_query
    mocker.patch("academic_tracker.athr_srch_webio.orcid.PublicAPI.read_record_public", mock_query)
    
    def mock_token(*args, **kwargs):
        return "sdfg"
    mocker.patch("academic_tracker.athr_srch_webio.orcid.PublicAPI.get_search_token_from_orcid", mock_token)
    
    expected_dict = load_json(os.path.join("testing_files", "ORCID_pub_dict.json"))
    
    returned_dict = search_ORCID_for_pubs({}, "qwerqwer", "asdfasdf", authors_dict, False)
    
    ## There is a character in the title of this publication that saves funny 
    ## so it won't be the same when you check.
    del expected_dict["https://doi.org/10.1016/j.celrep.2021.110013"]
    del returned_dict["https://doi.org/10.1016/j.celrep.2021.110013"]
         
    assert returned_dict == expected_dict



@pytest.fixture
def scholarly_pubs():
    return load_json(os.path.join("testing_files", "scholarly_pubs.json"))

        
@pytest.fixture
def scholarly_doi():
    return load_json(os.path.join("testing_files", "scholarly_DOIs.json"))


def test_search_Google_Scholar_for_pubs(authors_dict, scholarly_pubs, scholarly_doi, mocker):
    def mock_queried_author(*args, **kwargs):
        return {'container_type': 'Author',
                 'filled': ['basics'],
                 'scholar_id': '-j7fxnEAAAAJ',
                 'name': 'Andrew J. Morris',
                 'affiliation': 'Stony Brook, University of North Carolina, University of Kentucky',
                 'interests': ['Medicine'],
                 'email_domain': '@uky.edu',
                 'citedby': 23618}
    mocker.patch("academic_tracker.athr_srch_webio.scholarly.scholarly.search_author_id", mock_queried_author)
    
    def mock_fill_publications(dictionary, *args, **kwargs):
        if "sections" in kwargs:
            filled_publications = load_json(os.path.join("testing_files", "scholarly_query.json"))
            return filled_publications
        else:
            for pub in scholarly_pubs:
                if pub["author_pub_id"] == dictionary["author_pub_id"]:
                    return pub
            
    mocker.patch("academic_tracker.athr_srch_webio.scholarly.scholarly.fill", mock_fill_publications)
    
    def mock_Crossref_DOI(title, *args, **kwargs):
        if title in scholarly_doi:
            return scholarly_doi[title]
        else:
            return None
        
    mocker.patch("academic_tracker.webio.get_DOI_from_Crossref", mock_Crossref_DOI)
    
    expected_pub_dict = load_json(os.path.join("testing_files", "scholarly_pub_dict.json"))
    
    actual_pub_dict = search_Google_Scholar_for_pubs({}, authors_dict, "ptth222@uky.edu", False)
    
    assert actual_pub_dict == expected_pub_dict



def test_search_Crossref_for_pubs(authors_dict, mocker):
    def mock_query(*args, **kwargs):
        return load_json(os.path.join("testing_files", "Crossref_query.json"))
    mocker.patch("academic_tracker.athr_srch_webio.habanero.Crossref.works", mock_query)
       
    expected_pub_dict = load_json(os.path.join("testing_files", "Crossref_pub_dict.json"))
    
    actual_pub_dict = search_Crossref_for_pubs({}, authors_dict, "ptth222@uky.edu", False)
        
    assert actual_pub_dict == expected_pub_dict






