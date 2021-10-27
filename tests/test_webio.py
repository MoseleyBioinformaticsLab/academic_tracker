# -*- coding: utf-8 -*-


import pytest
import xml.etree.ElementTree as ET
import os
import pymed
import pickle
from collections import OrderedDict
from academic_tracker.webio import is_relevant_publication, check_pubmed_for_grants, create_emails_dict, request_pubs_from_pubmed




@pytest.fixture
def pub_with_no_matching_author():
    xml_path = os.path.join("testing_files", "no_author.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())


@pytest.fixture
def pub_with_matching_author():
    xml_path = os.path.join("testing_files", "has_author.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())


@pytest.fixture
def author_info():
    cutoff_year = 2019
    author_first_name = "Andrew"
    author_last_name = "Morris"
    author_affiliations = ["kentucky"]
    author_id = "Andrew Morris"
    
    return cutoff_year, author_first_name, author_last_name, author_affiliations, author_id



def test_is_relevant_publication_no_author(pub_with_no_matching_author, author_info):
    
    pub = pub_with_no_matching_author
    
    cutoff_year, author_first_name, author_last_name, author_affiliations, author_id = author_info
    
    pub_dict = is_relevant_publication(pub, cutoff_year, author_first_name, author_last_name, author_affiliations, author_id, {})
    
    assert pub_dict == {}


def test_is_relevant_publication_with_author(pub_with_matching_author, author_info):
    
    pub = pub_with_matching_author
    
    cutoff_year, author_first_name, author_last_name, author_affiliations, author_id = author_info
    
    pub_dict = is_relevant_publication(pub, cutoff_year, author_first_name, author_last_name, author_affiliations, author_id, {})
    
    matching_dict = pub.toDict()
    del matching_dict["xml"]
    matching_dict["publication_date"] = str(matching_dict["publication_date"])
    
    assert pub_dict == matching_dict


def test_is_relevant_publication_is_in_prev_pubs(pub_with_matching_author, author_info):
    
    pub = pub_with_matching_author
    
    cutoff_year, author_first_name, author_last_name, author_affiliations, author_id = author_info
    
    pub_dict = is_relevant_publication(pub, cutoff_year, author_first_name, author_last_name, author_affiliations, author_id, {pub.pubmed_id})
    
    assert pub_dict == {}


def test_is_relevant_publication_is_before_cutoff_year(pub_with_matching_author, author_info):
    
    pub = pub_with_matching_author
    
    cutoff_year, author_first_name, author_last_name, author_affiliations, author_id = author_info
    
    pub_dict = is_relevant_publication(pub, 3000, author_first_name, author_last_name, author_affiliations, author_id, {})
    
    assert pub_dict == {}
    



@pytest.mark.network_access
def test_check_pubmed_for_grants_has_grant():
    grants = check_pubmed_for_grants("33830777", ["P42 ES007380"])
    
    assert grants == set(["P42 ES007380"])

@pytest.mark.network_access
def test_check_pubmed_for_grants_no_grant():
    grants = check_pubmed_for_grants("34352431", ["P42 ES007380"])
    
    assert grants == set()




@pytest.fixture
def pub_with_grants():
    xml_path = os.path.join("testing_files", "has_pubmed_grants.xml")
    tree = ET.parse(xml_path)
    return pymed.article.PubMedArticle(xml_element=tree.getroot())


@pytest.fixture
def publication_dict(pub_with_grants, pub_with_matching_author):
    publication_dict = {}
    
    pub_dict = pub_with_grants.toDict()
    del pub_dict["xml"]
    pub_dict["publication_date"] = str(pub_dict["publication_date"])
    
    publication_dict[pub_dict["pubmed_id"].split("\n")[0]] = pub_dict
    
    pub_dict = pub_with_matching_author.toDict()
    del pub_dict["xml"]
    pub_dict["publication_date"] = str(pub_dict["publication_date"])
    
    publication_dict[pub_dict["pubmed_id"].split("\n")[0]] = pub_dict
    
    return publication_dict


@pytest.fixture
def pubs_by_author_dict():
    return {"Andrew Morris":{"34352431":set(), "33830777":set(["P42 ES007380"])}}

@pytest.fixture
def authors_dict():
    return {'Andrew Morris': {'email': 'a.j.morris@uky.edu',
                                  'first_name': 'Andrew',
                                  'last_name': 'Morris',
                                  'pubmed_name_search': 'Andrew Morris',
                                  'affiliations': ['kentucky'],
                                  'cc_email': ["ptth222@uky.edu", "ptth222@gmail.com"],
                                  'cutoff_year': 2019,
                                  'email_subject': 'New PubMed Publications',
                                  'email_template': 'Hey <author_first_name>,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\n<total_pubs>\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
                                  'from_email': 'ptth222@uky.edu',
                                  'grants': ['P42ES007380', 'P42 ES007380']}}

@pytest.fixture
def email_messages():
    return {'creation_date': '2021-10-20 21:50',
             'emails': [{'body': 'Hey Andrew,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\nMottaleb MA, Ding QX, Pennell KG, Haynes EN, Morris AJ. 2021. Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry.. Journal of chromatography. A. 10.1016/j.chroma.2021.462426 PMID:34352431\n\nCited Grants:\nNone\n\n\nDeng P, Valentino T, Flythe MD, Moseley HNB, Leachman JR, Morris AJ, Hennig B. 2021. Untargeted Stable Isotope Probing of the Gut Microbiota Metabolome Using . Journal of proteome research. 10.1021/acs.jproteome.1c00124 PMID:33830777\n\nCited Grants:\nP42 ES007380\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
               'subject': 'New PubMed Publications',
               'from': 'ptth222@uky.edu',
               'to': 'a.j.morris@uky.edu',
               'cc': 'ptth222@uky.edu,ptth222@gmail.com',
               'author': 'Andrew Morris'}]}


def test_create_emails_dict_creates_successfully(pubs_by_author_dict, authors_dict, publication_dict, email_messages):
    function_messages = create_emails_dict(pubs_by_author_dict, authors_dict, publication_dict)
    
    del function_messages["creation_date"]
    del email_messages["creation_date"]
    print(function_messages)
    print()
    print(email_messages)
    
    assert email_messages == function_messages






## pymed's PubMed.query() actually returns an itertools.chain where the elements are actually the _getArticles method of PubMed, not the articles directly.
## Each call to the iterator does an http request. Here I simply put the articles in a list. 
@pytest.fixture
def pymed_query():
    with open(os.path.join("testing_files", "pymed_pubs.pkl"), "rb") as f:
        articles = pickle.load(f)
    return articles


@pytest.fixture
def expected_publication_dict():
    return OrderedDict([('34352431',
              {'pubmed_id': '34352431',
               'title': 'Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry.',
               'abstract': 'We developed and validated a method for direct determination of per- and polyfluoroalkylated substances (PFASs) in environmental water samples without prior sample concentration. Samples are centrifuged and supernatants passed through an Acrodisc Filter (GXF/GHP 0.2\xa0\xa0um, 25\xa0\xa0mm diameter). After addition of ammonium acetate, samples are analyzed by UPLC-MS/MS using an AB Sciex 6500 plus Q-Trap mass spectrometer operated in negative multiple reaction-monitoring (MRM) mode. The instrument system incorporates a delay column between the pumps and autosampler to mitigate interference from background PFAS. The method monitors eight short-/long-chain PFAS which are identified by monitoring specific precursor product ion pairs and by their retention times and quantified using isotope mass-labeled internal standard based calibration plots. Average spiked recoveries (n\xa0=\xa08) of target analytes ranged from 84 to 110% with 4-9% relative standard deviation (RSD). The mean spiked recoveries (n\xa0=\xa08) of four surrogates were 94-106% with 3-8% RSD. For continuous calibration verification (CCV), average spiked recoveries (n\xa0=\xa08) for target analytes ranged from 88 to 114% with 4-11% RSD and for surrogates ranged from 104-112% with 3-11% RSD. The recoveries (n\xa0=\xa06) of matrix spike (MX), matrix spike duplicate (MXD), and field reagent blank (FRB) met our acceptance criteria. The limit of detection for the target analytes was between 0.007 and 0.04\xa0ng/mL. The method was used to measure PFAS in tap water and surface water.',
               'keywords': ['Acrodisc filtration',
                'Direct injection',
                'Drinking and surface water',
                'PFAS',
                'UPLC-MS/MS'],
               'journal': 'Journal of chromatography. A',
               'publication_date': '2021-08-06',
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
                 'affiliation': 'Superfund Research Center, University of Kentucky, Lexington KY, 40506, United States; Center for Appalachian Research in Environmental Sciences, University of Kentucky, Lexington KY, 40506, United States; Department of Civil Engineering, College of Engineering, University of Kentucky, Lexington KY, 40506, United States. Electronic address: kellypennell@uky.edu.'},
                {'lastname': 'Haynes',
                 'firstname': 'Erin N',
                 'initials': 'EN',
                 'affiliation': 'Superfund Research Center, University of Kentucky, Lexington KY, 40506, United States; Center for Appalachian Research in Environmental Sciences, University of Kentucky, Lexington KY, 40506, United States; Department of Epidemiology, College of Public Health, University of Kentucky, Lexington KY, 40536, United States. Electronic address: erin.haynes@uky.edu.'},
                {'lastname': 'Morris',
                 'firstname': 'Andrew J',
                 'initials': 'AJ',
                 'affiliation': 'Superfund Research Center, University of Kentucky, Lexington KY, 40506, United States; Center for Appalachian Research in Environmental Sciences, University of Kentucky, Lexington KY, 40506, United States; Division of Cardiovascular, Medicine, College of Medicine, University of Kentucky and Lexington VA Medical Center, Lexington, KY, 40536, United States. a.j.morris@uky.edu; Pressent address: Institute of Drug & Biotherapeutic Innovation, DRC, 1100 South Grand Blvd, Saint Louis University, Saint Louis, MO 63104 United States. Electronic address: a.j.morris@uky.edu.',
                 'author_id': 'Andrew Morris'}],
               'methods': None,
               'conclusions': None,
               'results': None,
               'copyrights': 'Copyright © 2021. Published by Elsevier B.V.',
               'doi': '10.1016/j.chroma.2021.462426'})])


@pytest.fixture
def expected_pubs_by_author():
    return {"Andrew Morris": {"34352431": set()}}


def test_request_pubs_from_pubmed_success(pymed_query, mocker, authors_dict):
    mocker.patch("academic_tracker.webio.PubMed.query", return_value=pymed_query)
    mocker.patch("academic_tracker.webio.check_pubmed_for_grants", return_value=set())
    publication_dict, pubs_by_author_dict = request_pubs_from_pubmed({}, authors_dict, "ptth222@uky.edu", False)




























