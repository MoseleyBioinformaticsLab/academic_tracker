# -*- coding: utf-8 -*-



import os
import time
from datetime import datetime
import re
import shutil

import pytest
import pandas

from academic_tracker.fileio import load_json, read_previous_publications, save_publications_to_file, save_emails_to_file, read_text_from_txt 
from academic_tracker.fileio import read_text_from_docx, read_csv, save_string_to_file, save_json_to_file
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
    path = os.path.join("tests", "testing_files", "load_json_error")
    
    with pytest.raises(BaseException):
        load_json(path)


def test_load_json_no_error(test_json):
    
    path = os.path.join("tests", "testing_files", "config.json")
    
    data = load_json(path)
    
    assert data == test_json
    
    
def test_load_json_no_path():
    path = os.path.join("tests", "testing_files", "asdf.asdf")
    
    with pytest.raises(SystemExit):
        load_json(path)



def test_read_text_from_txt_error():
    path = os.path.join("tests", "testing_files", "load_json_error")
    
    with pytest.raises(BaseException):
        read_text_from_txt(path)


def test_read_text_from_txt_no_error():
    
    path = os.path.join("tests", "testing_files", "testing_text.txt")
    
    data = read_text_from_txt(path)
    
    assert data == 'line 1\nline 2'
    

def test_read_text_from_txt_no_path():
    path = os.path.join("tests", "testing_files", "asdf.asdf")
    
    with pytest.raises(SystemExit):
        read_text_from_txt(path)
    


def test_read_text_from_docx_error():
    path = os.path.join("tests", "testing_files", "load_json_error")
    
    with pytest.raises(BaseException):
        read_text_from_docx(path)


def test_read_text_from_docx_no_error():
    
    path = os.path.join("tests", "testing_files", "testing_docx.docx")
    
    data = read_text_from_docx(path)
    
    assert data == 'Line 1\nLine 2'
    
    
def test_read_text_from_docx_no_path():
    path = os.path.join("tests", "testing_files", "asdf.asdf")
    
    with pytest.raises(SystemExit):
        read_text_from_docx(path)
    


def test_read_csv_error():
    path = os.path.join("tests", "testing_files", "load_json_error")
    
    with pytest.raises(BaseException):
        read_csv(path)


def test_read_csv_no_error():
    
    path = os.path.join("tests", "testing_files", "testing_csv.csv")
    
    data = read_csv(path)
    
    assert data.equals(pandas.DataFrame({"col1":["data1"], "col2":["data2"]}))
    

def test_read_csv_no_path():
    path = os.path.join("tests", "testing_files", "asdf.asdf")
    
    with pytest.raises(SystemExit):
        read_csv(path)



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
    
    save_publications_to_file(save_dir_name, {}, {"test":"test"})
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


    

def test_read_previous_publications_no_publications():
    
    has_previous_pubs, prev_pubs = read_previous_publications(None)
    
    assert not has_previous_pubs and prev_pubs == {}


def test_read_previous_publications_ignore():
    
    has_previous_pubs, prev_pubs = read_previous_publications("ignore")
    
    assert not has_previous_pubs and prev_pubs == {}
    
    
def test_read_previous_publications_read_until(tracker_latest_dir, tracker_today_dir):
    
    has_previous_pubs, prev_pubs = read_previous_publications(None)
    
    assert has_previous_pubs and prev_pubs == {"test":"test"}


def test_read_previous_publications_path_in_args(test_json):
    
    path = os.path.join("tests", "testing_files", "config.json")
    
    has_previous_pubs, prev_pubs = read_previous_publications(path)
    
    assert has_previous_pubs and prev_pubs == test_json







@pytest.fixture
def test_email_dir():
    save_dir_name = TESTING_DIR
    json_email_save_path = os.path.join(save_dir_name, "emails.json")
    os.mkdir(save_dir_name)
    time_to_wait = 10
    time_counter = 0
    
    while not os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(save_dir_name + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    
    yield save_dir_name, json_email_save_path
    
    os.remove(json_email_save_path)
    time_counter = 0
    while os.path.exists(json_email_save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(json_email_save_path + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
            
    
    os.rmdir(save_dir_name)
    time_counter = 0
    while os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(save_dir_name + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")






def test_save_emails_to_file_successful_save(test_email_dir, email_messages):
    
    save_dir_name, json_email_save_path = test_email_dir
    save_emails_to_file(email_messages, save_dir_name)
    
    time_to_wait = 10
    time_counter = 0
    while not os.path.exists(json_email_save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(json_email_save_path + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
            
    emails_json = load_json(json_email_save_path)
    
    del emails_json["creation_date"]
    del email_messages["creation_date"]

    assert emails_json == email_messages






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
def test_save_string_dir():
    save_dir_name = TESTING_DIR
    filename = "test.txt"
    save_path = os.path.join(save_dir_name, filename)
    os.mkdir(save_dir_name)
    time_to_wait = 10
    time_counter = 0
    
    while not os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(save_dir_name + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    
    yield save_dir_name, save_path, filename
    
    os.remove(save_path)
    time_counter = 0
    while os.path.exists(save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(save_path + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    
    os.rmdir(save_dir_name)
    time_counter = 0
    while os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(save_dir_name + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")



def test_save_string_to_file_successful_save(test_save_string_dir):
    
    save_dir_name, save_path, filename = test_save_string_dir
    save_string_to_file(save_dir_name, filename, "test")
    
    time_to_wait = 10
    time_counter = 0
    while not os.path.exists(save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(save_path + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")

    saved_text = read_text_from_txt(save_path)

    assert saved_text == "test"




@pytest.fixture
def test_save_json_dir():
    save_dir_name = TESTING_DIR
    filename = "test.json"
    save_path = os.path.join(save_dir_name, filename)
    os.mkdir(save_dir_name)
    time_to_wait = 10
    time_counter = 0
    
    while not os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(save_dir_name + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    
    yield save_dir_name, save_path, filename
    
    os.remove(save_path)
    time_counter = 0
    while os.path.exists(save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(save_path + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")
    
    os.rmdir(save_dir_name)
    time_counter = 0
    while os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileExistsError(save_dir_name + " was not deleted within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")



def test_save_json_to_file_successful_save(test_save_json_dir):
    
    save_dir_name, save_path, filename = test_save_json_dir
    save_json_to_file(save_dir_name, filename, {"test":"test"})
    
    time_to_wait = 10
    time_counter = 0
    while not os.path.exists(save_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(save_path + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")

    saved_json = load_json(save_path)

    assert saved_json == {"test":"test"}










@pytest.fixture(scope="module", autouse=True)
def cleanup(request):
    """Cleanup a testing directory once we are finished."""
    def remove_test_dir():
        if os.path.exists(TESTING_DIR):
            shutil.rmtree(TESTING_DIR)
    request.addfinalizer(remove_test_dir)

