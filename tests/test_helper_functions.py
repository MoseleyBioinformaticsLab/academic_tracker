# -*- coding: utf-8 -*-

from academic_tracker.helper_functions import create_citation





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








