# -*- coding: utf-8 -*-


import os
import time
import json

import pytest
import shutil
import pandas

from academic_tracker.athr_srch_emails_and_reports import create_pubs_by_author_dict, create_project_reports_and_emails, create_project_report
from academic_tracker.athr_srch_emails_and_reports import create_summary_report, build_author_loop, create_collaborators_reports_and_emails
from academic_tracker.athr_srch_emails_and_reports import create_tabular_collaborator_report, create_collaborator_report, create_tabular_summary_report
from academic_tracker.athr_srch_emails_and_reports import create_tabular_project_report, _build_report_rows
from academic_tracker.fileio import load_json, read_text_from_txt


TESTING_DIR = "test_dir"
@pytest.fixture(scope="module", autouse=True)
def test_email_dir():
    save_dir_name = TESTING_DIR
    os.mkdir(save_dir_name)
    time_to_wait = 10
    time_counter = 0
    
    while not os.path.exists(save_dir_name):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            raise FileNotFoundError(save_dir_name + " was not created within " + str(time_to_wait) + " seconds, so it is assumed that it won't be and something went wrong.")



@pytest.fixture
def publication_dict():
    return load_json(os.path.join("tests", "testing_files", "publication_dict_truncated.json"))


def test_create_pubs_by_author_dict(publication_dict):
    expected = load_json(os.path.join("tests", "testing_files", "pubs_by_author_dict_truncated.json"))
    
    actual = create_pubs_by_author_dict(publication_dict)
    
    assert expected == actual



@pytest.fixture
def config_dict():
    return load_json(os.path.join("tests", "testing_files", "config_truncated.json"))


@pytest.fixture
def authors_by_project_dict():
    return load_json(os.path.join("tests", "testing_files", "authors_by_project_dict_truncated.json"))


def test_create_project_reports_and_emails(publication_dict, config_dict, authors_by_project_dict):
    
    ## Add Travis to a publication so we can test that multiple authors are sent emails.
    publication_dict["https://doi.org/10.1038/s41597-023-02277-x"]["authors"][1]["author_id"] = "Travis Thompson"
    
    expected_emails = load_json(os.path.join("tests", "testing_files", "athr_project_emails.json"))
    del expected_emails["creation_date"]
    
    actual_emails = create_project_reports_and_emails(authors_by_project_dict, publication_dict, config_dict, TESTING_DIR)
    # with open(os.path.join("tests", "testing_files", "athr_project_emails_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_emails, indent=2, sort_keys=True))
    del actual_emails["creation_date"]
    
    dir_contents = os.listdir(TESTING_DIR)
    expected_num_of_project_reports = 5
    actual_num_of_project_reports = len(dir_contents)
    
    assert expected_emails == actual_emails
    assert actual_num_of_project_reports == expected_num_of_project_reports
    
    
@pytest.fixture
def config_dict_tabular():
    return load_json(os.path.join("tests", "testing_files", "config_tabular.json"))


@pytest.fixture
def authors_by_project_dict_tabular():
    return load_json(os.path.join("tests", "testing_files", "authors_by_project_dict_tabular.json"))
    
    
def test_create_project_reports_and_emails_tabular(publication_dict, config_dict_tabular, authors_by_project_dict_tabular):
    ## Add a filename to a project report to test that it will create it correctly.
    authors_by_project_dict_tabular["Core A Administrative Core"]["Hunter Moseley"]["project_report"]["filename"] = "asdf.csv"
    ## Add Travis to a publication so we can test that multiple authors are sent emails.
    publication_dict["https://doi.org/10.1038/s41597-023-02277-x"]["authors"][1]["author_id"] = "Travis Thompson"
            
    expected_emails = load_json(os.path.join("tests", "testing_files", "athr_project_emails_tabular.json"))
    del expected_emails["creation_date"]
    ## attachment for xlsx files is a filepath and it differs between OS's.
    del expected_emails["emails"][1]["attachment"]
    
    actual_emails = create_project_reports_and_emails(authors_by_project_dict_tabular, publication_dict, config_dict_tabular, TESTING_DIR)
    # with open(os.path.join("tests", "testing_files", "athr_project_emails_tabular_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_emails, indent=2, sort_keys=True))
    del actual_emails["creation_date"]
    del actual_emails["emails"][1]["attachment"]
    
    dir_contents = os.listdir(TESTING_DIR)
    expected_num_of_project_reports = 5
    actual_num_of_project_reports = len(dir_contents)
    
    number_of_excel_files = len([name for name in dir_contents if ".xlsx" in name])
    
    assert "asdf.csv" in dir_contents
    assert expected_emails == actual_emails
    assert number_of_excel_files == 1
    assert "no_from_email_report.csv" in dir_contents
    assert actual_num_of_project_reports == expected_num_of_project_reports
        



def test_create_project_report(publication_dict, config_dict, authors_by_project_dict):
    ## Add Travis to a publication so we can test that multiple authors get reported.
    publication_dict["https://doi.org/10.1038/s41597-023-02277-x"]["authors"][1]["author_id"] = "Travis Thompson"
    
    template_string = "<author_first> <author_last>:\n<author_loop><author_first> <author_last>:\n<pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>"
    author_first = "Kelly"
    author_last = "Pennell"
    
    expected_text = read_text_from_txt(os.path.join("tests", "testing_files", "project_report.txt"))
    
    actual_text = create_project_report(publication_dict, config_dict, authors_by_project_dict, "No Authors", template_string, author_first, author_last)
    # with open(os.path.join("tests", "testing_files", "project_report_new.txt"), 'wb') as outFile:
    #     outFile.write(actual_text.encode("utf-8"))
    
    assert expected_text == actual_text



def test_create_summary_report(publication_dict, config_dict, authors_by_project_dict):
    ## Add Travis to a publication so we can test that multiple authors get reported.
    publication_dict["https://doi.org/10.1038/s41597-023-02277-x"]["authors"][1]["author_id"] = "Travis Thompson"
    
    expected_text = read_text_from_txt(os.path.join("tests", "testing_files", "athr_srch_summary_report.txt"))
    
    actual_text = create_summary_report(publication_dict, config_dict, authors_by_project_dict)
    # with open(os.path.join("tests", "testing_files", "athr_srch_summary_report_new.txt"), 'wb') as outFile:
    #     outFile.write(actual_text.encode("utf-8"))
    
    assert expected_text == actual_text



def test_build_author_loop(publication_dict, config_dict, authors_by_project_dict):
    
    template_string = read_text_from_txt(os.path.join("tests", "testing_files", "athr_srch_build_loop_template_string.txt"))
                         
    expected_text = read_text_from_txt(os.path.join("tests", "testing_files", "athr_srch_build_author_loop.txt"))
    
    actual_text = build_author_loop(publication_dict, config_dict, authors_by_project_dict, "No from_email", template_string)
    # with open(os.path.join("tests", "testing_files", "athr_srch_build_author_loop_new.txt"), 'wb') as outFile:
    #     outFile.write(actual_text.encode("utf-8"))
    
    assert expected_text == actual_text
  
        


def test_create_collaborators_reports_and_emails_tabular(publication_dict, config_dict):
    ## Add Travis and Sweta to a publication so we can test that multiple authors get reported.
    publication_dict["https://doi.org/10.1038/s41597-023-02277-x"]["authors"][1]["author_id"] = "Travis Thompson"
    publication_dict["https://doi.org/10.1038/s41597-023-02277-x"]["authors"][0]["author_id"] = "Sweta Ojha"
    ## Add an author that won't be in config_dict to test that line of code.
    publication_dict["https://doi.org/10.1038/s41597-023-02277-x"]["authors"][2]["author_id"] = "asdf"
    
    config_dict["Authors"]["Sweta Ojha"]["collaborator_report"] = {"from_email":"ptth222@uky.edu", 
                                                                    "email_body":"asdf",
                                                                    "email_subject":"asdf",
                                                                    }
    config_dict["Authors"]["Travis Thompson"]["collaborator_report"] = {"from_email":"ptth222@uky.edu",
                                                                        "to_email":"ptth222@uky.edu",
                                                                        "email_body":"asdf",
                                                                        "email_subject":"asdf",
                                                                        "columns":{"Col1":"<pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations>"},
                                                                        "separator":"\t"
                                                                      }
    config_dict["Authors"]["Hunter Moseley"]["collaborator_report"] = {"from_email":"ptth222@uky.edu",
                                                                        "to_email":"ptth222@uky.edu",
                                                                        "email_body":"asdf",
                                                                        "email_subject":"asdf",
                                                                        "columns":{"Col1":"<pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations>"},
                                                                        "sort":["Col1"]
                                                                        }
    
    expected_emails = load_json(os.path.join("tests", "testing_files", "collaborator_emails_tabular.json"))
    del expected_emails["creation_date"]
    
    actual_emails = create_collaborators_reports_and_emails(publication_dict, config_dict, TESTING_DIR)
    # with open(os.path.join("tests", "testing_files", "collaborator_emails_tabular_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_emails, indent=2, sort_keys=True))
    del actual_emails["creation_date"]
    
    dir_contents = os.listdir(TESTING_DIR)
    expected_num_of_collaborator_reports = 3
    actual_num_of_collaborator_reports = len(dir_contents)
    
    assert expected_emails == actual_emails
    assert actual_num_of_collaborator_reports == expected_num_of_collaborator_reports
    


def test_create_collaborators_reports_and_emails(publication_dict, config_dict):
    ## Add Travis, Sweta, and Kelly to a publication so we can test that multiple authors get reported.
    publication_dict["https://doi.org/10.1038/s41597-023-02277-x"]["authors"][1]["author_id"] = "Travis Thompson"
    publication_dict["https://doi.org/10.1038/s41597-023-02277-x"]["authors"][0]["author_id"] = "Sweta Ojha"
    publication_dict["https://doi.org/10.1038/s41597-023-02277-x"]["authors"][4]["author_id"] = "Kelly Pennell"
    
    config_dict["Authors"]["Travis Thompson"]["collaborator_report"] = {"template":"<pub_author_loop><pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations></pub_author_loop>",
                                                                        "from_email":"ptth222@uky.edu",
                                                                        "email_body":"asdf",
                                                                        "email_subject":"asdf"}
    
    config_dict["Authors"]["Sweta Ojha"]["collaborator_report"] = {"template":"<pub_author_loop><pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations></pub_author_loop>",
                                                                    "from_email":"ptth222@uky.edu",
                                                                    "email_body":"asdf",
                                                                    "email_subject":"asdf",
                                                                    "filename":"name_test.txt"}
    
    config_dict["Authors"]["Kelly Pennell"]["collaborator_report"] = {"from_email":"ptth222@uky.edu",
                                                                      "to_email":"ptth222@uky.edu",
                                                                      "email_body":"asdf",
                                                                      "email_subject":"asdf",
                                                                      "columns":{"Col1":"<pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations>"},
                                                                      "file_format":"xlsx"}
    
    config_dict["Authors"]["Hunter Moseley"]["collaborator_report"] = {"from_email":"ptth222@uky.edu",
                                                                        "to_email":"ptth222@uky.edu",
                                                                        "email_body":"asdf",
                                                                        "email_subject":"asdf",
                                                                        "columns":{"Col1":"<pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations>"},
                                                                        "sort":["Col1"],
                                                                        "filename":"name_test.csv"}
    
    expected_emails = load_json(os.path.join("tests", "testing_files", "collaborator_emails.json"))
    del expected_emails["creation_date"]
    del expected_emails["emails"][3]["attachment"]
    
    actual_emails = create_collaborators_reports_and_emails(publication_dict, config_dict, TESTING_DIR)
    # with open(os.path.join("tests", "testing_files", "collaborator_emails_new.json"),'w') as jsonFile:
    #     jsonFile.write(json.dumps(actual_emails, indent=2, sort_keys=True))
    del actual_emails["creation_date"]
    del actual_emails["emails"][3]["attachment"]
    
    dir_contents = os.listdir(TESTING_DIR)
    expected_num_of_collaborator_reports = 4
    actual_num_of_collaborator_reports = len(dir_contents)
    
    number_of_excel_files = len([name for name in dir_contents if ".xlsx" in name])
    
    assert expected_emails == actual_emails
    assert "name_test.txt" in dir_contents
    assert "name_test.csv" in dir_contents
    assert number_of_excel_files == 1
    assert actual_num_of_collaborator_reports == expected_num_of_collaborator_reports
    
    


@pytest.mark.parametrize("config_dict_collab, filename, file_format", [
        
        ({"Authors":{"Hunter Moseley":{"collaborator_report":{"columns":{"Col1":"<pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations>", "Col2":"asdf"},
                                                            "separator":"\t",
                                                            "sort":["Col1"],
                                                            "column_order":["Col2", "Col1"]}}}}, "test_name.csv", "csv"),
        ({"Authors":{"Hunter Moseley":{"collaborator_report":{"columns":{"Col1":"<pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations>", "Col2":"asdf"},
                                                            "column_order":["Col1", "Col2"]}}}}, "test_name.csv", "csv"),
        ])   

def test_create_tabular_collaborator_report(publication_dict, config_dict_collab, filename, file_format):
    
    if "separator" in config_dict_collab["Authors"]["Hunter Moseley"]["collaborator_report"]:
        sep = config_dict_collab["Authors"]["Hunter Moseley"]["collaborator_report"]["separator"]
    else:
        sep = ","
        
    if "sort" in config_dict_collab["Authors"]["Hunter Moseley"]["collaborator_report"]:
        column_one = 'Atta M, Nawabi, AM, Division of Transplant and Hepatobiliary, Department of Surgery, The University of Kansas Medical Center, Kansas City, Kansas, USA.'
    else:
        column_one = 'Zachary A, Kipp, ZA, Department of Pharmacology and Nutritional Sciences, University of Kentucky College of Medicine, Lexington, Kentucky, USA.'
    
    create_tabular_collaborator_report(publication_dict, config_dict_collab, "Hunter Moseley", ["https://doi.org/10.1002/hep.32467"], filename, file_format, TESTING_DIR)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert filename in dir_contents
    
    df = pandas.read_csv(os.path.join(TESTING_DIR, filename), sep=sep)
    report_text = read_text_from_txt(os.path.join(TESTING_DIR, filename))
    # df.to_csv(os.path.join("tests", "testing_files", "aaa.csv"),sep=sep, index=False, lineterminator="\n")
    assert df.to_csv(sep=sep, index=False, lineterminator="\n") == report_text
    assert list(df.columns) == config_dict_collab["Authors"]["Hunter Moseley"]["collaborator_report"]["column_order"]
    assert df.iloc[1].loc["Col1"] == column_one
    assert df.iloc[0].loc["Col2"] == "asdf"
    
    

def test_create_tabular_collaborator_report_defaults(publication_dict):
    
    config_dict = {"Authors":{"Hunter Moseley":{"collaborator_report":{}}}}
    
    create_tabular_collaborator_report(publication_dict, config_dict, "Hunter Moseley", ["https://doi.org/10.1002/hep.32467"], "test_name.csv", "csv", TESTING_DIR)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert "test_name.csv" in dir_contents
    
    df = pandas.read_csv(os.path.join(TESTING_DIR, "test_name.csv"), sep=",")
    report_text = read_text_from_txt(os.path.join(TESTING_DIR, "test_name.csv"))
    assert df.to_csv(sep=",", index=False, lineterminator="\n") == report_text
    assert list(df.columns) == ["Name", "Affiliations"]
    assert df.iloc[0].loc["Name"] == 'Alganem, Khaled'
    assert df.iloc[0].loc["Affiliations"] == 'Department of Neurosciences, University of Toledo College of Medicine and Life Sciences, Toledo, Ohio, USA.'
    

def test_create_tabular_collaborator_report_excel(publication_dict):
    
    config_dict = {"Authors":{"Hunter Moseley":{"collaborator_report":{}}}}
    
    create_tabular_collaborator_report(publication_dict, config_dict, "Hunter Moseley", ["https://doi.org/10.1002/hep.32467"], "test_name.csv", "xlsx", TESTING_DIR)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert "test_name.csv.xlsx" in dir_contents
    
    df = pandas.read_excel(os.path.join(TESTING_DIR, "test_name.csv.xlsx"))
    assert list(df.columns) == ["Name", "Affiliations"]
    assert df.iloc[0].loc["Name"] == 'Alganem, Khaled'
    assert df.iloc[0].loc["Affiliations"] == 'Department of Neurosciences, University of Toledo College of Medicine and Life Sciences, Toledo, Ohio, USA.'
    
    
def test_create_tabular_collaborator_report_empty():
    
    config_dict = {"Authors":{"Hunter Moseley":{"collaborator_report":{}}}}
    publication_dict = {"https://doi.org/10.1002/hep.32467":{"authors":[]}}
    
    report, filename = create_tabular_collaborator_report(publication_dict, config_dict, "Hunter Moseley", ["https://doi.org/10.1002/hep.32467"], "test_name.csv", "xlsx", TESTING_DIR)
    
    assert report == ""
    
    
    
def test_create_collaborator_report(publication_dict):
    
    template = "<pub_author_loop><pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations></pub_author_loop>"
    
    expected_report = read_text_from_txt(os.path.join("tests", "testing_files", "collaborator_report2.txt"))
    
    actual_report = create_collaborator_report(publication_dict, template, "Hunter Moseley", ["https://doi.org/10.1002/hep.32467"], "test_name.txt", TESTING_DIR)
    # with open(os.path.join("tests", "testing_files", "collaborator_report2_new.txt"), 'wb') as outFile:
    #     outFile.write(actual_report.encode("utf-8"))
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert "test_name.txt" in dir_contents
    assert expected_report == actual_report
    
    



def test_create_tabular_summary_report_no_pub_keywords(publication_dict, config_dict, authors_by_project_dict):
    
    config_dict["summary_report"] = {"columns":{"Col1":"<project_name>", "Col2":"<author_first>"},
                                      "filename":"test_name.csv",
                                      "file_format":"csv",
                                      "separator":"\t",
                                      "sort":["Col2"],
                                      "column_order":["Col2", "Col1"]}
    
    create_tabular_summary_report(publication_dict, config_dict, authors_by_project_dict, TESTING_DIR)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert "test_name.csv" in dir_contents
    
    df = pandas.read_csv(os.path.join(TESTING_DIR, "test_name.csv"), sep="\t")
    report_text = read_text_from_txt(os.path.join(TESTING_DIR, "test_name.csv"))
    # df.to_csv(os.path.join("tests", "testing_files", "aaa.csv"), sep="\t", index=False, lineterminator="\n")
    assert df.to_csv(sep="\t", index=False, lineterminator="\n") == report_text
    assert list(df.columns) == config_dict["summary_report"]["column_order"]
    assert df.iloc[1].loc["Col1"] == "Project 1"
    assert df.iloc[0].loc["Col2"] == "Hunter"
    
    
def test_create_tabular_summary_report_defaults(publication_dict, config_dict, authors_by_project_dict):
    
    config_dict["summary_report"] = {"columns":{"Col1":"<project_name>", "Col2":"<author_first>", "Col3":"<title>"}}
    
    create_tabular_summary_report(publication_dict, config_dict, authors_by_project_dict, TESTING_DIR)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert "summary_report.csv" in dir_contents
    
    df = pandas.read_csv(os.path.join(TESTING_DIR, "summary_report.csv"), sep=",")
    # df.to_csv(os.path.join("tests", "testing_files", "aaa.csv"), sep=",", index=False, lineterminator="\n")
    report_text = read_text_from_txt(os.path.join(TESTING_DIR, "summary_report.csv"))
    assert df.to_csv(sep=",", index=False, lineterminator="\n") == report_text
    assert list(df.columns) == list(config_dict["summary_report"]["columns"].keys())
    assert df.iloc[1].loc["Col1"] == 'Core A Administrative Core'
    assert df.iloc[0].loc["Col2"] == "Hunter"
    assert df.iloc[0].loc["Col3"] == 'Plk1 phosphorylation of PHGDH to regulate serine metabolism'
    

def test_create_tabular_summary_report_excel(publication_dict, config_dict, authors_by_project_dict):
    
    config_dict["summary_report"] = {"columns":{"Col1":"<project_name>", "Col2":"<author_first>", "Col3":"<title>", "Col4":"<pub_author_first>"},
                                      "filename":"summary_report.csv",
                                      "file_format":"xlsx"}
    
    create_tabular_summary_report(publication_dict, config_dict, authors_by_project_dict, TESTING_DIR)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert "summary_report.csv.xlsx" in dir_contents
    
    df = pandas.read_excel(os.path.join(TESTING_DIR, "summary_report.csv.xlsx"))
    # df.to_csv(os.path.join("tests", "testing_files", "aaa.csv"), sep=",", index=False, lineterminator="\n")
    assert list(df.columns) == list(config_dict["summary_report"]["columns"].keys())
    assert df.iloc[1].loc["Col1"] == 'Core A Administrative Core'
    assert df.iloc[0].loc["Col2"] == "Hunter"
    assert df.iloc[0].loc["Col3"] == 'Plk1 phosphorylation of PHGDH to regulate serine metabolism'
    assert df.iloc[0].loc["Col4"] == "Hunter"





@pytest.fixture
def pubs_by_author_dict():
    return load_json(os.path.join("tests", "testing_files", "pubs_by_author_dict_truncated.json"))


def test_build_report_rows_no_authors(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict):
    "There should never be a publication without an author, but the code is there just in case."
    publication_dict["https://doi.org/10.1002/hep.32467"]["authors"] = []
    
    row_template = {"Col1":"<project_name>", "Col2":"<author_first>", "Col3":"<title>", "Col4":"<pub_author_first>"}
    
    rows = _build_report_rows(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict, row_template, "Project 1")
    assert rows[1]["Col4"] == "None"
    

def test_build_report_rows_only_reference_keywords(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict):
    "Need to test a template with reference keywords and no author keywords."
    publication_dict["https://doi.org/10.1002/hep.32467"]["authors"] = []
    
    row_template = {"Col1":"<project_name>", "Col2":"<author_first>", "Col3":"<title>", "Col4":"<reference_citation>"}
    
    rows = _build_report_rows(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict, row_template, "Project 1")
    assert rows[0]["Col4"] == "None"
    assert len(rows) == 81
    assert rows[1]["Col4"] == "Roehlen N, Crouchet E, Baumert TF. Liver fibrosis: mechanistic concepts and therapeutic perspectives. Cells. 2020;9:875."


def test_create_tabular_project_report_no_pub_keywords(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict):
    
    report_attributes = {"columns":{"Col1":"<project_name>", "Col2":"<author_first>"},
                          "filename":"test_name.csv",
                          "file_format":"csv",
                          "separator":"\t",
                          "sort":["Col2"],
                          "column_order":["Col2", "Col1"]}
    
    project_name = "Project 1"
    
    filename = "project_report.csv"
    
    create_tabular_project_report(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict, project_name, report_attributes, TESTING_DIR, filename)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert filename in dir_contents
    
    df = pandas.read_csv(os.path.join(TESTING_DIR, filename), sep="\t")
    # df.to_csv(os.path.join("tests", "testing_files", "aaa.csv"), sep="\t", index=False, lineterminator="\n")
    report_text = read_text_from_txt(os.path.join(TESTING_DIR, filename))
    assert df.to_csv(sep="\t", index=False, lineterminator="\n") == report_text
    assert list(df.columns) == report_attributes["column_order"]
    assert df.iloc[0].loc["Col1"] == "Project 1"
    assert df.iloc[0].loc["Col2"] == "Hunter"
    
    

def test_create_tabular_project_report_defaults(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict):
    
    report_attributes = {"columns":{"Col1":"<project_name>", "Col2":"<author_first>", "Col3":"<title>"}}
    
    project_name = "Project 1"
    
    filename = "project_report.csv"
    
    create_tabular_project_report(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict, project_name, report_attributes, TESTING_DIR, filename)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert "project_report.csv" in dir_contents
    
    df = pandas.read_csv(os.path.join(TESTING_DIR, "project_report.csv"), sep=",")
    # df.to_csv(os.path.join("tests", "testing_files", "aaa.csv"), sep=",", index=False, lineterminator="\n")
    report_text = read_text_from_txt(os.path.join(TESTING_DIR, "project_report.csv"))
    assert df.to_csv(sep=",", index=False, lineterminator="\n") == report_text
    assert list(df.columns) == list(report_attributes["columns"].keys())
    assert df.iloc[1].loc["Col1"] == 'Project 1'
    assert df.iloc[0].loc["Col2"] == "Hunter"
    assert df.iloc[0].loc["Col3"] == 'Plk1 phosphorylation of PHGDH to regulate serine metabolism'
    

def test_create_tabular_project_report_excel(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict):
    
    report_attributes = {"columns":{"Col1":"<project_name>", 
                                    "Col2":"<author_first>", 
                                    "Col3":"<title>", 
                                    "Col4":"<pub_author_first>", 
                                    "Col5":"<reference_citation>"},
                          "filename":"project_report.csv",
                          "file_format":"xlsx"}
    
    project_name = "No Authors"
    
    filename = "project_report.csv"
    
    create_tabular_project_report(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict, project_name, report_attributes, TESTING_DIR, filename)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert "project_report.csv.xlsx" in dir_contents
    
    df = pandas.read_excel(os.path.join(TESTING_DIR, "project_report.csv.xlsx"), keep_default_na=False)
    # df.to_csv(os.path.join("tests", "testing_files", "aaa.csv"), sep="\t", index=False, lineterminator="\n")
    assert list(df.columns) == list(report_attributes["columns"].keys())
    assert df.iloc[1].loc["Col1"] == 'No Authors'
    assert df.iloc[0].loc["Col2"] == "Hunter"
    assert df.iloc[0].loc["Col3"] == 'Plk1 phosphorylation of PHGDH to regulate serine metabolism'
    assert df.iloc[0].loc["Col4"] == "Hunter"
    assert df.iloc[0].loc["Col5"] == "None"
    assert df.iloc[1].loc["Col3"] == 'Hepatic kinome atlas: An in-depth identification of kinase pathways in liver fibrosis of humans and rodents.'
    assert df.iloc[811].loc["Col3"] == 'Identifying and sharing per-and polyfluoroalkyl substances hot-spot areas and exposures in drinking water.'
    assert df.iloc[1].loc["Col5"] == 'Roehlen N, Crouchet E, Baumert TF. Liver fibrosis: mechanistic concepts and therapeutic perspectives. Cells. 2020;9:875.'
    assert df.iloc[46].loc["Col4"] == "Zachary A"




@pytest.fixture(autouse=True)
def test_dir_reset(request):
    def clean_test_dir():
        if os.path.exists(TESTING_DIR):
            for test_file in os.listdir(TESTING_DIR):
                os.remove(os.path.join(TESTING_DIR, test_file))
    request.addfinalizer(clean_test_dir)


@pytest.fixture(scope="module", autouse=True)
def cleanup(request):
    """Cleanup a testing directory once we are finished."""
    def remove_test_dir():
        if os.path.exists(TESTING_DIR):
            shutil.rmtree(TESTING_DIR)
    request.addfinalizer(remove_test_dir)

