# -*- coding: utf-8 -*-

from academic_tracker.helper_functions import create_citation, replace_body_magic_words, replace_subject_magic_words
from fixtures import pub_with_no_matching_author, pub_with_grants, authors_dict, publication_dict, pubs_by_author_dict, pub_with_matching_author


def test_create_citation():
    
    pub = {
            'abstract': "Following the publication of this article the authors noted that Torfi Sigurdsson's name was misspelled. Instead of Sigrudsson it should be Sigurdsson. The PDF and HTML versions of the paper have been modified accordingly.\xa0The authors would like to apologise for this error and the inconvenience this may have caused.",
             'authors': [
                     { 'affiliation': 'Department of Neurology, University Medical Center, Johannes Gutenberg-University, Mainz, Germany.',
                       'firstname': 'Carine',
                       'initials': 'C',
                       'lastname': 'Thalman'},],
             'conclusions': None,
             'copyrights': None,
             'doi': '10.1038/s41380-018-0320-1',
             'journal': 'Molecular psychiatry',
             'keywords': [],
             'methods': None,
             'publication_date': '2019-01-04',
             'pubmed_id': '30602735',
             'results': None,
             'title': 'Correction: Synaptic phospholipids as a new target for cortical hyperexcitability and E/I balance in psychiatric disorders.'}
             
             
    assert create_citation(pub) == 'Thalman C. 2019. Correction: Synaptic phospholipids as a new target for cortical hyperexcitability and E/I balance in psychiatric disorders.. Molecular psychiatry. 10.1038/s41380-018-0320-1 PMID:30602735'


def test_replace_body_magic_words(pubs_by_author_dict, authors_dict, publication_dict):
    
    assert replace_body_magic_words(pubs_by_author_dict["Andrew Morris"], authors_dict["Andrew Morris"], publication_dict) == 'Hey Andrew,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\nMottaleb MA, Ding QX, Pennell KG, Haynes EN, Morris AJ. 2021. Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry.. Journal of chromatography. A. 10.1016/j.chroma.2021.462426 PMID:34352431\n\nCited Grants:\nNone\n\n\nDeng P, Valentino T, Flythe MD, Moseley HNB, Leachman JR, Morris AJ, Hennig B. 2021. Untargeted Stable Isotope Probing of the Gut Microbiota Metabolome Using . Journal of proteome research. 10.1021/acs.jproteome.1c00124 PMID:33830777\n\nCited Grants:\nP42 ES007380\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu'


def test_replace_subject_magic_words(authors_dict):
    
    author_attributes = authors_dict["Andrew Morris"]
    author_attributes["email_subject"] = "Test replacement <author_first_name> <author_last_name>"
    
    assert replace_subject_magic_words(author_attributes) == "Test replacement Andrew Morris"




