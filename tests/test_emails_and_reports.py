# -*- coding: utf-8 -*-

import pytest
from academic_tracker.emails_and_reports import create_citation, replace_body_magic_words, replace_subject_magic_words, create_emails_dict, create_email_dict_for_no_PMCID_pubs, create_citations_for_author
from academic_tracker.emails_and_reports import add_indention_to_string, create_pubs_by_author_dict, build_project_email_body, create_indented_project_report
from fixtures import pub_with_no_matching_author, pub_with_grants, authors_dict, pub_with_matching_author, passing_config
from academic_tracker.fileio import load_json
from academic_tracker.helper_functions import create_authors_by_project_dict
import os


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
             'publication_date': {"year":2019, "month":1, "day":4},
             'pubmed_id': '30602735',
             'results': None,
             'PMCID':None,
             'title': 'Correction: Synaptic phospholipids as a new target for cortical hyperexcitability and E/I balance in psychiatric disorders.'}
             
             
    assert create_citation(pub) == 'Carine Thalman. 2019. Correction: Synaptic phospholipids as a new target for cortical hyperexcitability and E/I balance in psychiatric disorders.. Molecular psychiatry. DOI:10.1038/s41380-018-0320-1 PMID:30602735 PMCID:None'


@pytest.fixture
def publication_dict():
    return load_json(os.path.join("testing_files", "publication_dict.json"))

@pytest.fixture
def authors_json_file():
    return load_json(os.path.join("testing_files", "authors.json"))

@pytest.fixture
def authors_by_project_dict(authors_json_file, passing_config):
    print(passing_config)
    return create_authors_by_project_dict(passing_config, authors_json_file)

@pytest.fixture
def email_messages():
    return load_json(os.path.join("testing_files", "emails.json"))
                 
                 
def test_create_emails_dict_creates_successfully(authors_by_project_dict, authors_json_file, publication_dict, passing_config, email_messages):
    function_messages = create_emails_dict(authors_by_project_dict, publication_dict, passing_config)
    
    del function_messages["creation_date"]
    del email_messages["creation_date"]
    
    assert email_messages == function_messages
    
    
@pytest.fixture
def publications_with_no_PMCID_list():
    return [{'DOI': '10.1016/j.chroma.2021.462426',
  'PMID': '34352431',
  'line': 'Mottaleb MA, Ding QX, Pennell KG, Haynes E, Morris AJ. 2021. Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry. Journal of Chromatography. A. 1653:5. doi:10.1016/j.chroma.2021.462426 PMID:34352431 ',
  'Grants': ['P30 ES026529']},
 {'DOI': '10.13023/jah.0201.06',
  'PMID': '',
  'line': 'Hoover AG, Koempel A, Christian WJ, Tumlin KI, Pennell KG. 2020. Appalachian environmental health literacy: Building knowledge and skills to protect health. Journal of Appalachian Health. 2:doi:10.13023/jah.0201.06 ',
  'Grants': []}]
    
    
@pytest.fixture
def no_PMCID_email_message():
    return {'creation_date': '2021-11-06 02:32',
 'emails': [{'body': 'These are the publications I was able to find on PubMed. Are any missing?\n\nMottaleb MA, Ding QX, Pennell KG, Haynes E, Morris AJ. 2021. Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry. Journal of Chromatography. A. 1653:5. doi:10.1016/j.chroma.2021.462426 PMID:34352431 \n\nPMID: 34352431\n\nCited Grants:\nP30 ES026529\n\n\nHoover AG, Koempel A, Christian WJ, Tumlin KI, Pennell KG. 2020. Appalachian environmental health literacy: Building knowledge and skills to protect health. Journal of Appalachian Health. 2:doi:10.13023/jah.0201.06 \n\nPMID: None\n\nCited Grants:\nNone\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu',
   'subject': 'New PubMed Publications',
   'from': 'ptth222@uky.edu',
   'to': 'ptth222@uky.edu',
   'cc': ''}]}
        

#def test_create_email_dict_for_no_PMCID_pubs(publications_with_no_PMCID_list, passing_config, no_PMCID_email_message):
#    email_message = create_email_dict_for_no_PMCID_pubs(publications_with_no_PMCID_list, passing_config, "ptth222@uky.edu")
#    
#    del email_message["creation_date"]
#    del no_PMCID_email_message["creation_date"]
#    
#    assert email_message == no_PMCID_email_message
    

@pytest.fixture
def authors_pubs():
    return {'https://doi.org/10.1007/164_2019_320': ['K01 CA197073'],
                 'https://doi.org/10.1016/j.bbalip.2020.158734': [],
                 'https://doi.org/10.1016/j.celrep.2021.110013': [],
                 'https://doi.org/10.1016/j.chroma.2021.462426': ['P30 ES026529',
                  'P42 ES007380'],
                 'https://doi.org/10.1016/j.envint.2021.106907': [],
                   }
    

def test_replace_body_magic_words(authors_pubs, authors_dict, publication_dict):
    
    check_string = 'Hey Andrew,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\nFredrick O Onono, Andrew J Morris. 2020. Phospholipase D and Choline Metabolism.. Handbook of experimental pharmacology. DOI:10.1007/164_2019_320 PMID:32086667 PMCID:PMC7768751\n\nCited Grants:\nK01 CA197073\n\n\nSusan S Smyth, Maria Kraemer, Liping Yang, Patrick Van Hoose, Andrew J Morris. 2020. Roles for lysophosphatidic acid signaling in vascular development and disease.. Biochimica et biophysica acta. Molecular and cell biology of lipids. DOI:10.1016/j.bbalip.2020.158734 PMID:32376340 PMCID:None\n\nCited Grants:\nNone\n\n\nElisa Matas-Rico, Elselien Frijlink, Irene van der Haar Àvila, Apostolos Menegakis, Maaike van Zon, Andrew J Morris, Jan Koster, Fernando Salgado-Polo, Sander de Kivit, Telma Lança, Antonio Mazzocca, Zoë Johnson, John Haanen, Ton N Schumacher, Anastassis Perrakis, Inge Verbrugge, Joost H van den Berg, Jannie Borst, Wouter H Moolenaar. 2021. Autotaxin impedes anti-tumor immunity by suppressing chemotaxis and tumor infiltration of CD8. Cell reports. DOI:10.1016/j.celrep.2021.110013 PMID:34788605 PMCID:None\n\nCited Grants:\nNone\n\n\nM Abdul Mottaleb, Qunxing X Ding, Kelly G Pennell, Erin N Haynes, Andrew J Morris. 2021. Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry.. Journal of chromatography. A. DOI:10.1016/j.chroma.2021.462426 PMID:34352431 PMCID:None\n\nCited Grants:\nP30 ES026529\nP42 ES007380\n\n\nMichael C Petriello, M Abdul Mottaleb, Tara C Serio, Bharat Balyan, Matthew C Cave, Marian Pavuk, Linda S Birnbaum, Andrew J Morris. 2021. Serum concentrations of legacy and emerging per- and polyfluoroalkyl substances in the Anniston Community Health Surveys (ACHS I and ACHS II).. Environment international. DOI:10.1016/j.envint.2021.106907 PMID:34763231 PMCID:None\n\nCited Grants:\nNone\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu'
    
    assert replace_body_magic_words(authors_pubs, authors_dict["Andrew Morris"], publication_dict) == check_string


def test_replace_subject_magic_words(authors_dict):
    
    author_attributes = authors_dict["Andrew Morris"]
    author_attributes["email_subject"] = "Test replacement <author_first_name> <author_last_name>"
    
    assert replace_subject_magic_words(author_attributes) == "Test replacement Andrew Morris"



def test_create_citations_for_author(authors_pubs, publication_dict):
    
    check_string = 'Fredrick O Onono, Andrew J Morris. 2020. Phospholipase D and Choline Metabolism.. Handbook of experimental pharmacology. DOI:10.1007/164_2019_320 PMID:32086667 PMCID:PMC7768751\n\nCited Grants:\nK01 CA197073\n\n\nSusan S Smyth, Maria Kraemer, Liping Yang, Patrick Van Hoose, Andrew J Morris. 2020. Roles for lysophosphatidic acid signaling in vascular development and disease.. Biochimica et biophysica acta. Molecular and cell biology of lipids. DOI:10.1016/j.bbalip.2020.158734 PMID:32376340 PMCID:None\n\nCited Grants:\nNone\n\n\nElisa Matas-Rico, Elselien Frijlink, Irene van der Haar Àvila, Apostolos Menegakis, Maaike van Zon, Andrew J Morris, Jan Koster, Fernando Salgado-Polo, Sander de Kivit, Telma Lança, Antonio Mazzocca, Zoë Johnson, John Haanen, Ton N Schumacher, Anastassis Perrakis, Inge Verbrugge, Joost H van den Berg, Jannie Borst, Wouter H Moolenaar. 2021. Autotaxin impedes anti-tumor immunity by suppressing chemotaxis and tumor infiltration of CD8. Cell reports. DOI:10.1016/j.celrep.2021.110013 PMID:34788605 PMCID:None\n\nCited Grants:\nNone\n\n\nM Abdul Mottaleb, Qunxing X Ding, Kelly G Pennell, Erin N Haynes, Andrew J Morris. 2021. Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry.. Journal of chromatography. A. DOI:10.1016/j.chroma.2021.462426 PMID:34352431 PMCID:None\n\nCited Grants:\nP30 ES026529\nP42 ES007380\n\n\nMichael C Petriello, M Abdul Mottaleb, Tara C Serio, Bharat Balyan, Matthew C Cave, Marian Pavuk, Linda S Birnbaum, Andrew J Morris. 2021. Serum concentrations of legacy and emerging per- and polyfluoroalkyl substances in the Anniston Community Health Surveys (ACHS I and ACHS II).. Environment international. DOI:10.1016/j.envint.2021.106907 PMID:34763231 PMCID:None\n\nCited Grants:\nNone'
    
    assert create_citations_for_author(authors_pubs, publication_dict) == check_string



def test_add_indention_to_string():
    
    check_string = "\tasdf\n\tqwer"
    
    string_to_indent = "asdf\nqwer"
    
    assert add_indention_to_string(string_to_indent) == check_string
    

@pytest.fixture
def pubs_by_author_dict():  
    return {'Dustin Savage': {'https://doi.org/10.1039/d1an00144b': ['P42 ES007380'],
                              'https://doi.org/10.1039/d1sm00985k': []},
            'Hollie Swanson': {'https://doi.org/10.1177/23821205211006411': ['P30 ES026529',
           'P42 ES007380',
           'R25 ES027684']}}
    

def test_create_pubs_by_author_dict(publication_dict, pubs_by_author_dict):
    
    subset_keys = ["https://doi.org/10.1039/d1an00144b", "https://doi.org/10.1039/d1sm00985k", "https://doi.org/10.1177/23821205211006411"]
    publication_dict = {key: publication_dict[key] for key in subset_keys}
           
    assert create_pubs_by_author_dict(publication_dict) == pubs_by_author_dict



@pytest.mark.parametrize("project_dict, return_value", [
        
        ({"authors":["Dustin Savage", "Hollie Swanson"], "email_template":"Pubs go here: <total_pubs>"}, 'Pubs go here: Dustin Savage:\nDustin T Savage, J Zach Hilt, Thomas D Dziubla. 2021. Leveraging the thermoresponsiveness of fluorinated poly(N-isopropylacrylamide) copolymers as a sensing tool for perfluorooctane sulfonate.. The Analyst. DOI:10.1039/d1an00144b PMID:33928975 PMCID:PMC8224178\n\nCited Grants:\nP42 ES007380\n\n\nDustin T Savage, J Zach Hilt, Thomas D Dziubla. 2021. Assessing the perfluoroalkyl acid-induced swelling of Förster resonance energy transfer-capable poly(. Soft matter. DOI:10.1039/d1sm00985k PMID:34661226 PMCID:None\n\nCited Grants:\nNone\n\n\nHollie Swanson:\nMarianne Phelps, Catrina White, Lin Xiang, Hollie I Swanson. 2021. Improvisation as a Teaching Tool for Improving Oral Communication Skills in Premedical and Pre-Biomedical Graduate Students.. Journal of medical education and curricular development. DOI:10.1177/23821205211006411 PMID:33954254 PMCID:PMC8056562\n\nCited Grants:\nP30 ES026529\nP42 ES007380\nR25 ES027684'),
        ({"email_template":"Pubs go here: <total_pubs>"}, 'Pubs go here: Dustin Savage:\nDustin T Savage, J Zach Hilt, Thomas D Dziubla. 2021. Leveraging the thermoresponsiveness of fluorinated poly(N-isopropylacrylamide) copolymers as a sensing tool for perfluorooctane sulfonate.. The Analyst. DOI:10.1039/d1an00144b PMID:33928975 PMCID:PMC8224178\n\nCited Grants:\nP42 ES007380\n\n\nDustin T Savage, J Zach Hilt, Thomas D Dziubla. 2021. Assessing the perfluoroalkyl acid-induced swelling of Förster resonance energy transfer-capable poly(. Soft matter. DOI:10.1039/d1sm00985k PMID:34661226 PMCID:None\n\nCited Grants:\nNone\n\n\nHollie Swanson:\nMarianne Phelps, Catrina White, Lin Xiang, Hollie I Swanson. 2021. Improvisation as a Teaching Tool for Improving Oral Communication Skills in Premedical and Pre-Biomedical Graduate Students.. Journal of medical education and curricular development. DOI:10.1177/23821205211006411 PMID:33954254 PMCID:PMC8056562\n\nCited Grants:\nP30 ES026529\nP42 ES007380\nR25 ES027684'),
        ]) 



def test_build_project_email_body(project_dict, publication_dict, pubs_by_author_dict, return_value):
    
    assert build_project_email_body(project_dict, publication_dict, pubs_by_author_dict) == return_value


@pytest.mark.parametrize("project_dict, return_value", [
        
        ({"authors":["Dustin Savage", "Hollie Swanson"]}, '\tDustin Savage:\n\t\tDustin T Savage, J Zach Hilt, Thomas D Dziubla. 2021. Leveraging the thermoresponsiveness of fluorinated poly(N-isopropylacrylamide) copolymers as a sensing tool for perfluorooctane sulfonate.. The Analyst. DOI:10.1039/d1an00144b PMID:33928975 PMCID:PMC8224178\n\t\t\n\t\tCited Grants:\n\t\tP42 ES007380\n\t\t\n\t\t\n\t\tDustin T Savage, J Zach Hilt, Thomas D Dziubla. 2021. Assessing the perfluoroalkyl acid-induced swelling of Förster resonance energy transfer-capable poly(. Soft matter. DOI:10.1039/d1sm00985k PMID:34661226 PMCID:None\n\t\t\n\t\tCited Grants:\n\t\tNone\n\t\n\t\n\tHollie Swanson:\n\t\tMarianne Phelps, Catrina White, Lin Xiang, Hollie I Swanson. 2021. Improvisation as a Teaching Tool for Improving Oral Communication Skills in Premedical and Pre-Biomedical Graduate Students.. Journal of medical education and curricular development. DOI:10.1177/23821205211006411 PMID:33954254 PMCID:PMC8056562\n\t\t\n\t\tCited Grants:\n\t\tP30 ES026529\n\t\tP42 ES007380\n\t\tR25 ES027684'),
        ({}, '\tDustin Savage:\n\t\tDustin T Savage, J Zach Hilt, Thomas D Dziubla. 2021. Leveraging the thermoresponsiveness of fluorinated poly(N-isopropylacrylamide) copolymers as a sensing tool for perfluorooctane sulfonate.. The Analyst. DOI:10.1039/d1an00144b PMID:33928975 PMCID:PMC8224178\n\t\t\n\t\tCited Grants:\n\t\tP42 ES007380\n\t\t\n\t\t\n\t\tDustin T Savage, J Zach Hilt, Thomas D Dziubla. 2021. Assessing the perfluoroalkyl acid-induced swelling of Förster resonance energy transfer-capable poly(. Soft matter. DOI:10.1039/d1sm00985k PMID:34661226 PMCID:None\n\t\t\n\t\tCited Grants:\n\t\tNone\n\t\n\t\n\tHollie Swanson:\n\t\tMarianne Phelps, Catrina White, Lin Xiang, Hollie I Swanson. 2021. Improvisation as a Teaching Tool for Improving Oral Communication Skills in Premedical and Pre-Biomedical Graduate Students.. Journal of medical education and curricular development. DOI:10.1177/23821205211006411 PMID:33954254 PMCID:PMC8056562\n\t\t\n\t\tCited Grants:\n\t\tP30 ES026529\n\t\tP42 ES007380\n\t\tR25 ES027684'),
        ]) 

def test_create_indented_project_report(project_dict, pubs_by_author_dict, publication_dict, return_value):
    
    assert create_indented_project_report(project_dict, pubs_by_author_dict, publication_dict) == return_value
                                          






















