# -*- coding: utf-8 -*-

import os

import pytest

from academic_tracker.citation_parsing import parse_text_for_citations, tokenize_Vancouver_authors, tokenize_MLA_or_Chicago_authors
from academic_tracker.citation_parsing import tokenize_APA_or_Harvard_authors, tokenize_myncbi_citations, parse_MEDLINE_format
from academic_tracker.fileio import load_json, read_text_from_txt




def test_parse_text_for_citations():
    
    text = read_text_from_txt(os.path.join("tests", "testing_files", "parse_citations_test.txt"))
    
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_parsing_test.json"))
    
    actual_tokenized_citations = parse_text_for_citations(text)
    
    assert expected_tokenized_citations == actual_tokenized_citations



@pytest.mark.parametrize("authors_string, authors", [
        ("last_name initials", [{"last":"last_name", "initials":"initials"}]),
        ("last_name initials et al", [{"last":"last_name", "initials":"initials"}]),
        ("last_name1 initials1, last_name2 initials2", [{"last":"last_name1", "initials":"initials1"},
                                                       {"last":"last_name2", "initials":"initials2"}]),
        ("last_name1 initials1, and last_name2 initials2", [{"last":"last_name1", "initials":"initials1"},
                                                            {"last":"last_name2", "initials":"initials2"}]),
        ("last_name1 initials1 and last_name2 initials2", [{"last":"last_name1", "initials":"initials1"},
                                                           {"last":"last_name2", "initials":"initials2"}]),
        ("last_name1 initials1 & last_name2 initials2", [{"last":"last_name1", "initials":"initials1"},
                                                           {"last":"last_name2", "initials":"initials2"}]),
        ])

def test_tokenize_Vancouver_authors(authors_string, authors):
    
    assert authors == tokenize_Vancouver_authors(authors_string)
    


@pytest.mark.parametrize("authors_string, authors", [
        ("last_name, first_name middle_name", [{"first":"first_name", "middle":"middle_name", "last":"last_name"}]),
        ("last_name, first_name", [{"first":"first_name", "middle":"", "last":"last_name"}]),
        ("last_name, first_name middle_name et al.", [{"first":"first_name", "middle":"middle_name", "last":"last_name"}]),
        ("first_name middle_name last_name", [{"first":"first_name", "middle":"middle_name", "last":"last_name"}]),
        ("last_name1, first_name1 middle_name1, first_name2 middle_name2 last_name2", [{"first":"first_name1", "middle":"middle_name1", "last":"last_name1"},
                                                                                       {"first":"first_name2", "middle":"middle_name2", "last":"last_name2"}]),
        ("last_name1, first_name1 middle_name1, and first_name2 middle_name2 last_name2", [{"first":"first_name1", "middle":"middle_name1", "last":"last_name1"},
                                                                                           {"first":"first_name2", "middle":"middle_name2", "last":"last_name2"}]),
        ("last_name1, first_name1 middle_name1 and first_name2 middle_name2 last_name2", [{"first":"first_name1", "middle":"middle_name1", "last":"last_name1"},
                                                                                          {"first":"first_name2", "middle":"middle_name2", "last":"last_name2"}]),
        ("last_name1, first_name1 middle_name1, & first_name2 middle_name2 last_name2", [{"first":"first_name1", "middle":"middle_name1", "last":"last_name1"},
                                                                                         {"first":"first_name2", "middle":"middle_name2", "last":"last_name2"}]),
        ("last_name1, first_name1 middle_name1, & last_name2", [{"first":"first_name1", "middle":"middle_name1", "last":"last_name1"},
                                                                {"first":"", "middle":"", "last":"last_name2"}]),
        ("last_name1, first_name1 middle_name1, & first_name2 last_name2", [{"first":"first_name1", "middle":"middle_name1", "last":"last_name1"},
                                                                            {"first":"first_name2", "middle":"", "last":"last_name2"}]),
        ])


def test_tokenize_MLA_or_Chicago_authors(authors_string, authors):
    
    assert authors == tokenize_MLA_or_Chicago_authors(authors_string)




@pytest.mark.parametrize("authors_string, authors", [
        ("last_name, A.B.", [{"last":"last_name", "initials":"A.B."}]),
        (", A.B.", [{"last":"", "initials":"A.B."}]),
        ("last_name, A.B. et al.", [{"last":"last_name", "initials":"A.B."}]),
        ("last_name1, A.B., last_name2, C.D.", [{"last":"last_name1", "initials":"A.B."},
                                                {"last":"last_name2", "initials":"C.D."}]),
        ("last_name1, A.B., and last_name2, C.D.", [{"last":"last_name1", "initials":"A.B."},
                                                    {"last":"last_name2", "initials":"C.D."}]),
        ("last_name1, A.B. and last_name2, C.D.", [{"last":"last_name1", "initials":"A.B."},
                                                   {"last":"last_name2", "initials":"C.D."}]),
        ("last_name1, A.B. & last_name2, C.D.", [{"last":"last_name1", "initials":"A.B."},
                                                 {"last":"last_name2", "initials":"C.D."}]),
        ("last_name1, A.B. & last_name2, C.D.,", [{"last":"last_name1", "initials":"A.B."},
                                                  {"last":"last_name2", "initials":"C.D."}]),
        ("last_name1, A.B. & last_name2", [{"last":"last_name1", "initials":"A.B."},
                                           {"last":"last_name2", "initials":""}]),
        ])

def test_tokenize_APA_or_Harvard_authors(authors_string, authors):
    
    assert authors == tokenize_APA_or_Harvard_authors(authors_string)




def test_tokenize_myncbi_citations():
    pages = load_json(os.path.join("tests", "testing_files", "myncbi_webpages.json"))
    
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_myncbi_page1.json"))
    
    actual_tokenized_citations = tokenize_myncbi_citations(pages[0])
    
    assert expected_tokenized_citations == actual_tokenized_citations




def test_parse_MEDLINE_format():
    expected_tokenized_citations = load_json(os.path.join("tests", "testing_files", "tokenized_MEDLINE.json"))
    
    actual_tokenized_citations = parse_MEDLINE_format(read_text_from_txt(os.path.join("tests", "testing_files", "medline.txt")))
    
    assert expected_tokenized_citations == actual_tokenized_citations







