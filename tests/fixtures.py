# -*- coding: utf-8 -*-

import pytest
import xml.etree.ElementTree as ET
import os
import pymed


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

