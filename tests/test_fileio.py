# -*- coding: utf-8 -*-



import os
import time
from datetime import datetime
import re
import shutil
from academic_tracker.fileio import load_json, read_previous_publications, save_publications_to_file, save_emails_to_file, read_text_from_txt, save_project_reports_to_file, read_text_from_docx
import pytest
from fixtures import email_messages


TESTING_DIR = "test_dir"


@pytest.fixture
def test_json():
    return {
              "affiliations": [
                "kentucky"
              ],
              "cc_email": [],
              "cutoff_year": 2019,
              "email_subject": "New PubMed Publications",
              "email_template": "Hey <author_first_name>,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\n<total_pubs>\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu",
              "from_email": "ptth222@uky.edu",
              "grants": [
                "P42ES007380",
                "P42 ES007380"
              ]
            }


def test_load_json_error():
    path = os.path.join(".", "testing_files", "load_json_error")
    
    with pytest.raises(Exception):
        load_json(path)


def test_load_json_no_error(test_json):
    
    path = os.path.join(".", "testing_files", "config.json")
    
    data = load_json(path)
    
    assert data == test_json



def test_read_text_from_txt_error():
    path = os.path.join(".", "testing_files", "load_json_error")
    
    with pytest.raises(Exception):
        read_text_from_txt(path)


def test_read_text_from_txt_no_error():
    
    path = os.path.join(".", "testing_files", "testing_text.txt")
    
    data = read_text_from_txt(path)
    
    assert data == 'line 1\nline 2'
    


def test_read_text_from_docx_error():
    path = os.path.join(".", "testing_files", "load_json_error")
    
    with pytest.raises(Exception):
        read_text_from_docx(path)


def test_read_text_from_docx_no_error():
    
    path = os.path.join(".", "testing_files", "testing_docx.docx")
    
    data = read_text_from_docx(path)
    
    assert data == 'Line 1\nLine 2'



@pytest.fixture
def tracker_latest_dir():
    dir_name = "tracker-9999999999"
    os.mkdir(dir_name)
    yield
    os.rmdir(dir_name)


@pytest.fixture
def tracker_today_dir():
    save_dir_name = "tracker-" + re.sub(r"\-| |\:", "", str(datetime.now())[2:16])
    publication_save_path = os.path.join(save_dir_name, "publications.json")
    os.mkdir(save_dir_name)
    time_to_wait = 10
    time_counter = 0
    
    while not os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(save_dir_name + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    
    save_publications_to_file(save_dir_name, {}, {})
    time_counter = 0
    while not os.path.exists(publication_save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(publication_save_path + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    
    yield
    
    os.remove(publication_save_path)
    time_counter = 0
    while os.path.exists(publication_save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(publication_save_path + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    
    os.rmdir(save_dir_name)
    time_counter = 0
    while os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(save_dir_name + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")



def test_read_previous_publications_error(tracker_latest_dir):
    
    with pytest.raises(SystemExit):
        read_previous_publications({"--prev_pub":None})
        


def test_read_previous_publications_warning(tracker_today_dir, capsys):
    
    has_previous_pubs, prev_pubs = read_previous_publications({"--prev_pub":None})
    captured = capsys.readouterr()
    
    assert captured.out == "Warning: The latest tracker directory was made earlier today." + "\n" and has_previous_pubs and prev_pubs == {}
    

def test_read_previous_publications_no_publications():
    
    has_previous_pubs, prev_pubs = read_previous_publications({"--prev_pub":None})
    
    assert not has_previous_pubs and prev_pubs == {}


def test_read_previous_publications_path_in_args(test_json):
    
    path = os.path.join(".", "testing_files", "config.json")
    
    has_previous_pubs, prev_pubs = read_previous_publications({"--prev_pub":path})
    
    assert has_previous_pubs and prev_pubs == test_json







@pytest.fixture
def test_email_dir():
    save_dir_name = TESTING_DIR
    json_email_save_path = os.path.join(save_dir_name, "emails.json")
    text_email_save_path = os.path.join(save_dir_name, "emails.txt")
    os.mkdir(save_dir_name)
    time_to_wait = 10
    time_counter = 0
    
    while not os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(save_dir_name + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    
    yield save_dir_name, json_email_save_path, text_email_save_path
    
    os.remove(json_email_save_path)
    time_counter = 0
    while os.path.exists(json_email_save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(json_email_save_path + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
            
    os.remove(text_email_save_path)
    time_counter = 0
    while os.path.exists(text_email_save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(text_email_save_path + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    
    os.rmdir(save_dir_name)
    time_counter = 0
    while os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(save_dir_name + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")



@pytest.fixture
def email_text_file():
    return ['Subject: New PubMed Publications\n',
 'To: a.j.morris@uky.edu\n',
 'From: New PubMed Publications\n',
 'CC: ptth222@uky.edu,ptth222@gmail.com\n',
 'Body:\n',
 'Hey Andrew,\n',
 '\n',
 'These are the publications I was able to find on PubMed. Are any missing?\n',
 '\n',
 'Mottaleb MA, Ding QX, Pennell KG, Haynes EN, Morris AJ. 2021. Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry.. Journal of chromatography. A. 10.1016/j.chroma.2021.462426 PMID:34352431\n',
 '\n',
 'Cited Grants:\n',
 'None\n',
 '\n',
 '\n',
 'Deng P, Valentino T, Flythe MD, Moseley HNB, Leachman JR, Morris AJ, Hennig B. 2021. Untargeted Stable Isotope Probing of the Gut Microbiota Metabolome Using . Journal of proteome research. 10.1021/acs.jproteome.1c00124 PMID:33830777\n',
 '\n',
 'Cited Grants:\n',
 'P42 ES007380\n',
 '\n',
 'Kind regards,\n',
 '\n',
 'This email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu']



def test_save_emails_to_file_successful_save(test_email_dir, email_messages, email_text_file):
    
    save_dir_name, json_email_save_path, text_email_save_path = test_email_dir
    save_emails_to_file(email_messages, save_dir_name)
    
    time_to_wait = 10
    time_counter = 0
    while not os.path.exists(json_email_save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(json_email_save_path + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
            
    time_counter = 0
    while not os.path.exists(text_email_save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(text_email_save_path + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")

    emails_json = load_json(json_email_save_path)
    with open(text_email_save_path, "r") as infile:
        email_text = infile.readlines()
    
    del emails_json["creation_date"]
    del email_messages["creation_date"]

    assert emails_json == email_messages and email_text == email_text_file






@pytest.fixture
def test_pub_dir():
    save_dir_name = TESTING_DIR
    pub_save_path = os.path.join(save_dir_name, "publications.json")
    os.mkdir(save_dir_name)
    time_to_wait = 10
    time_counter = 0
    
    while not os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(save_dir_name + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    
    yield save_dir_name, pub_save_path
    
    os.remove(pub_save_path)
    time_counter = 0
    while os.path.exists(pub_save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(pub_save_path + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    
    os.rmdir(save_dir_name)
    time_counter = 0
    while os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(save_dir_name + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")




def test_save_publications_to_file_successful_save(test_pub_dir):
    
    save_dir_name, pub_save_path = test_pub_dir
    save_publications_to_file(save_dir_name, {}, {})
    
    time_to_wait = 10
    time_counter = 0
    while not os.path.exists(pub_save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(pub_save_path + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")

    publications_json = load_json(pub_save_path)

    assert publications_json == {}




@pytest.fixture
def test_report_dir():
    save_dir_name = TESTING_DIR
    report_save_path = os.path.join(save_dir_name, "summary_report.txt")
    os.mkdir(save_dir_name)
    time_to_wait = 10
    time_counter = 0
    
    while not os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(save_dir_name + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    
    yield save_dir_name, report_save_path
    
    os.remove(report_save_path)
    time_counter = 0
    while os.path.exists(report_save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(report_save_path + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    
    os.rmdir(save_dir_name)
    time_counter = 0
    while os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(save_dir_name + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")


def test_save_project_reports_to_file_successful_save(test_report_dir):
    
    save_dir_name, report_save_path = test_report_dir
    save_project_reports_to_file({}, save_dir_name, {})
    
    time_to_wait = 10
    time_counter = 0
    while not os.path.exists(report_save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(report_save_path + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")

    report_txt = read_text_from_txt(report_save_path)

    assert report_txt == ""






























@pytest.fixture(scope="module", autouse=True)
def cleanup(request):
    """Cleanup a testing directory once we are finished."""
    def remove_test_dir():
        if os.path.exists(TESTING_DIR):
            shutil.rmtree(TESTING_DIR)
    request.addfinalizer(remove_test_dir)

