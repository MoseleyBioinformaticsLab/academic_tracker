# -*- coding: utf-8 -*-


import os
import time

import pytest
import shutil
import pandas

from academic_tracker.athr_srch_emails_and_reports import create_pubs_by_author_dict, create_project_reports_and_emails, create_project_report
from academic_tracker.athr_srch_emails_and_reports import create_summary_report, build_author_loop, create_collaborators_reports_and_emails
from academic_tracker.athr_srch_emails_and_reports import create_tabular_collaborator_report, create_collaborator_report, create_tabular_summary_report
from academic_tracker.athr_srch_emails_and_reports import create_tabular_project_report, replace_keywords
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
    
    expected_emails = load_json(os.path.join("tests", "testing_files", "athr_project_emails.json"))
    del expected_emails["creation_date"]
    
    actual_emails = create_project_reports_and_emails(authors_by_project_dict, publication_dict, config_dict, TESTING_DIR)
    del actual_emails["creation_date"]
    
    dir_contents = os.listdir(TESTING_DIR)
    expected_num_of_project_reports = 13
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
            
    expected_emails = load_json(os.path.join("tests", "testing_files", "athr_project_emails_tabular.json"))
    del expected_emails["creation_date"]
    
    actual_emails = create_project_reports_and_emails(authors_by_project_dict_tabular, publication_dict, config_dict_tabular, TESTING_DIR)
    del actual_emails["creation_date"]
    
    dir_contents = os.listdir(TESTING_DIR)
    expected_num_of_project_reports = 13
    actual_num_of_project_reports = len(dir_contents)
    
    number_of_excel_files = len([name for name in dir_contents if ".xlsx" in name])
    
    assert expected_emails == actual_emails
    assert number_of_excel_files == 1
    assert "no_from_email_report.csv" in dir_contents
    assert actual_num_of_project_reports == expected_num_of_project_reports
        



def test_create_project_report(publication_dict, config_dict, authors_by_project_dict):
    
    template_string = "<author_loop><author_first> <author_last>:\n<pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>"
    author_first = "Kelly"
    author_last = "Pennell"
    
    expected_text = read_text_from_txt(os.path.join("tests", "testing_files", "project_report.txt"))
    
    actual_text = create_project_report(publication_dict, config_dict, authors_by_project_dict, "Core A Administrative Core", template_string, author_first, author_last)
    
    assert expected_text == actual_text



def test_create_summary_report(publication_dict, config_dict, authors_by_project_dict):
    
    expected_text = read_text_from_txt(os.path.join("tests", "testing_files", "athr_srch_summary_report.txt"))
    
    actual_text = create_summary_report(publication_dict, config_dict, authors_by_project_dict)
    
    assert expected_text == actual_text



def test_build_author_loop(publication_dict, config_dict, authors_by_project_dict):
    
    template_string = read_text_from_txt(os.path.join("tests", "testing_files", "athr_srch_build_loop_template_string.txt"))
                         
    expected_text = read_text_from_txt(os.path.join("tests", "testing_files", "athr_srch_build_author_loop.txt"))
    
    actual_text = build_author_loop(publication_dict, config_dict, authors_by_project_dict, "No from_email", template_string)
    
    assert expected_text == actual_text
    
    


def test_create_collaborators_reports_and_emails_tabular(publication_dict, config_dict):
    
    del config_dict["Authors"]["Ann Koempel"]
    
    config_dict["Authors"]["Anna Hoover"]["collaborator_report"] = {"from_email":"ptth222@uky.edu", 
                                                                    "email_body":"asdf",
                                                                    "email_subject":"asdf",
                                                                    }
    config_dict["Authors"]["Kelly Pennell"]["collaborator_report"] = {"from_email":"ptth222@uky.edu",
                                                                      "to_email":"ptth222@uky.edu",
                                                                      "email_body":"asdf",
                                                                      "email_subject":"asdf",
                                                                      "columns":{"Col1":"<pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations>"},
                                                                      "separator":"\t"
                                                                      }
    config_dict["Authors"]["Lindell Ormsbee"]["collaborator_report"] = {"from_email":"ptth222@uky.edu",
                                                                        "to_email":"ptth222@uky.edu",
                                                                        "email_body":"asdf",
                                                                        "email_subject":"asdf",
                                                                        "columns":{"Col1":"<pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations>"},
                                                                        "sort":["Col1"]
                                                                        }
    
    expected_emails = load_json(os.path.join("tests", "testing_files", "collaborator_emails_tabular.json"))
    del expected_emails["creation_date"]
    
    actual_emails = create_collaborators_reports_and_emails(publication_dict, config_dict, TESTING_DIR)
    del actual_emails["creation_date"]
    
    dir_contents = os.listdir(TESTING_DIR)
    expected_num_of_collaborator_reports = 3
    actual_num_of_collaborator_reports = len(dir_contents)
    
    assert expected_emails == actual_emails
    assert actual_num_of_collaborator_reports == expected_num_of_collaborator_reports
    


def test_create_collaborators_reports_and_emails(publication_dict, config_dict):
    
    config_dict["Authors"]["Ann Koempel"]["collaborator_report"] = {"template":"<pub_author_loop><pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations></pub_author_loop>",
                                                                    "from_email":"ptth222@uky.edu",
                                                                    "email_body":"asdf",
                                                                    "email_subject":"asdf"}
    
    config_dict["Authors"]["Anna Hoover"]["collaborator_report"] = {"template":"<pub_author_loop><pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations></pub_author_loop>",
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
    
    config_dict["Authors"]["Lindell Ormsbee"]["collaborator_report"] = {"from_email":"ptth222@uky.edu",
                                                                        "to_email":"ptth222@uky.edu",
                                                                        "email_body":"asdf",
                                                                        "email_subject":"asdf",
                                                                        "columns":{"Col1":"<pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations>"},
                                                                        "sort":["Col1"],
                                                                        "filename":"name_test.csv"}
    
    expected_emails = load_json(os.path.join("testing_files", "collaborator_emails.json"))
    del expected_emails["creation_date"]
    
    actual_emails = create_collaborators_reports_and_emails(publication_dict, config_dict, TESTING_DIR)
    del actual_emails["creation_date"]
    
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
        
        ({"Authors":{"Anna Hoover":{"collaborator_report":{"columns":{"Col1":"<pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations>", "Col2":"asdf"},
                                                           "separator":"\t",
                                                           "sort":["Col1"],
                                                           "column_order":["Col2", "Col1"]}}}}, "test_name.csv", "csv"),
        ({"Authors":{"Anna Hoover":{"collaborator_report":{"columns":{"Col1":"<pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations>", "Col2":"asdf"},
                                                           "column_order":["Col1", "Col2"]}}}}, "test_name.csv", "csv"),
        ])   

def test_create_tabular_collaborator_report(publication_dict, config_dict_collab, filename, file_format):
    
    if "separator" in config_dict_collab["Authors"]["Anna Hoover"]["collaborator_report"]:
        sep = config_dict_collab["Authors"]["Anna Hoover"]["collaborator_report"]["separator"]
    else:
        sep = ","
        
    if "sort" in config_dict_collab["Authors"]["Anna Hoover"]["collaborator_report"]:
        column_one = 'Dawn, Brewer, D, University of Kentucky Department of Dietetics and Human Nutrition.'
    else:
        column_one = 'W Jay, Christian, WJ, University of Kentucky College of Public Health.'
    
    create_tabular_collaborator_report(publication_dict, config_dict_collab, "Anna Hoover", ["32095784"], filename, file_format, TESTING_DIR)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert filename in dir_contents
    
    df = pandas.read_csv(os.path.join(TESTING_DIR, filename), sep=sep)
    report_text = read_text_from_txt(os.path.join(TESTING_DIR, filename))
    assert df.to_csv(sep=sep, index=False, line_terminator="\n") == report_text
    assert list(df.columns) == config_dict_collab["Authors"]["Anna Hoover"]["collaborator_report"]["column_order"]
    assert df.iloc[1].loc["Col1"] == column_one
    assert df.iloc[0].loc["Col2"] == "asdf"
    
    

def test_create_tabular_collaborator_report_defaults(publication_dict):
    
    config_dict = {"Authors":{"Anna Hoover":{"collaborator_report":{}}}}
    
    create_tabular_collaborator_report(publication_dict, config_dict, "Anna Hoover", ["32095784"], "test_name.csv", "csv", TESTING_DIR)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert "test_name.csv" in dir_contents
    
    df = pandas.read_csv(os.path.join(TESTING_DIR, "test_name.csv"), sep=",")
    report_text = read_text_from_txt(os.path.join(TESTING_DIR, "test_name.csv"))
    assert df.to_csv(sep=",", index=False, line_terminator="\n") == report_text
    assert list(df.columns) == ["Name", "Affiliations"]
    assert df.iloc[0].loc["Name"] == 'Brewer, Dawn'
    assert df.iloc[0].loc["Affiliations"] == 'University of Kentucky Department of Dietetics and Human Nutrition.'
    

def test_create_tabular_collaborator_report_excel(publication_dict):
    
    config_dict = {"Authors":{"Anna Hoover":{"collaborator_report":{}}}}
    
    create_tabular_collaborator_report(publication_dict, config_dict, "Anna Hoover", ["32095784"], "test_name.csv", "xlsx", TESTING_DIR)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert "test_name.csv.xlsx" in dir_contents
    
    df = pandas.read_excel(os.path.join(TESTING_DIR, "test_name.csv.xlsx"))
    assert list(df.columns) == ["Name", "Affiliations"]
    assert df.iloc[0].loc["Name"] == 'Brewer, Dawn'
    assert df.iloc[0].loc["Affiliations"] == 'University of Kentucky Department of Dietetics and Human Nutrition.'
    
    
def test_create_tabular_collaborator_report_empty():
    
    config_dict = {"Authors":{"Anna Hoover":{"collaborator_report":{}}}}
    publication_dict = {"32095784":{"authors":[]}}
    
    report, filename = create_tabular_collaborator_report(publication_dict, config_dict, "Anna Hoover", ["32095784"], "test_name.csv", "xlsx", TESTING_DIR)
    
    assert report == ""
    
    
    
def test_create_collaborator_report(publication_dict):
    
    template = "<pub_author_loop><pub_author_first>, <pub_author_last>, <pub_author_initials>, <pub_author_affiliations></pub_author_loop>"
    
    expected_report = 'Annie, Koempel, A, University of Kentucky Department of Dietetics and Human Nutrition.W Jay, Christian, WJ, University of Kentucky College of Public Health.Kimberly I, Tumlin, KI, University of Kentucky College of Public Health.Kelly G, Pennell, KG, University of Kentucky College of Engineering.Steven, Evans, S, Kentucky Water Resources Research Institute.Malissa, McAlister, M, Kentucky Water Resources Research Institute.Lindell E, Ormsbee, LE, University of Kentucky College of Engineering.Dawn, Brewer, D, University of Kentucky Department of Dietetics and Human Nutrition.'
    
    actual_report = create_collaborator_report(publication_dict, template, "Anna Hoover", ["32095784"], "test_name.txt", TESTING_DIR)
    
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
    assert df.to_csv(sep="\t", index=False, line_terminator="\n") == report_text
    assert list(df.columns) == config_dict["summary_report"]["column_order"]
    assert df.iloc[1].loc["Col1"] == "Project 1"
    assert df.iloc[0].loc["Col2"] == "Angela"
    
    

def test_create_tabular_summary_report_defaults(publication_dict, config_dict, authors_by_project_dict):
    
    config_dict["summary_report"] = {"columns":{"Col1":"<project_name>", "Col2":"<author_first>", "Col3":"<title>"}}
    
    create_tabular_summary_report(publication_dict, config_dict, authors_by_project_dict, TESTING_DIR)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert "summary_report.csv" in dir_contents
    
    df = pandas.read_csv(os.path.join(TESTING_DIR, "summary_report.csv"), sep=",")
    report_text = read_text_from_txt(os.path.join(TESTING_DIR, "summary_report.csv"))
    assert df.to_csv(sep=",", index=False, line_terminator="\n") == report_text
    assert list(df.columns) == list(config_dict["summary_report"]["columns"].keys())
    assert df.iloc[1].loc["Col1"] == 'Core A Administrative Core'
    assert df.iloc[0].loc["Col2"] == "Kelly"
    assert df.iloc[0].loc["Col3"] == 'Appalachian Environmental Health Literacy: Building Knowledge and Skills to Protect Health.'
    

def test_create_tabular_summary_report_excel(publication_dict, config_dict, authors_by_project_dict):
    
    config_dict["summary_report"] = {"columns":{"Col1":"<project_name>", "Col2":"<author_first>", "Col3":"<title>", "Col4":"<pub_author_first>"},
                                     "filename":"summary_report.csv",
                                     "file_format":"xlsx"}
    
    create_tabular_summary_report(publication_dict, config_dict, authors_by_project_dict, TESTING_DIR)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert "summary_report.csv.xlsx" in dir_contents
    
    df = pandas.read_excel(os.path.join(TESTING_DIR, "summary_report.csv.xlsx"))
    assert list(df.columns) == list(config_dict["summary_report"]["columns"].keys())
    assert df.iloc[1].loc["Col1"] == 'Core A Administrative Core'
    assert df.iloc[0].loc["Col2"] == "Kelly"
    assert df.iloc[0].loc["Col3"] == 'Appalachian Environmental Health Literacy: Building Knowledge and Skills to Protect Health.'
    assert df.iloc[0].loc["Col4"] == "Anna G"
    
    




@pytest.fixture
def pubs_by_author_dict():
    return load_json(os.path.join("tests", "testing_files", "pubs_by_author_dict_truncated.json"))

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
    report_text = read_text_from_txt(os.path.join(TESTING_DIR, filename))
    assert df.to_csv(sep="\t", index=False, line_terminator="\n") == report_text
    assert list(df.columns) == report_attributes["column_order"]
    assert df.iloc[1].loc["Col1"] == "Project 1"
    assert df.iloc[0].loc["Col2"] == "Angela"
    
    

def test_create_tabular_project_report_defaults(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict):
    
    report_attributes = {"columns":{"Col1":"<project_name>", "Col2":"<author_first>", "Col3":"<title>"}}
    
    project_name = "Project 1"
    
    filename = "project_report.csv"
    
    create_tabular_project_report(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict, project_name, report_attributes, TESTING_DIR, filename)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert "project_report.csv" in dir_contents
    
    df = pandas.read_csv(os.path.join(TESTING_DIR, "project_report.csv"), sep=",")
    report_text = read_text_from_txt(os.path.join(TESTING_DIR, "project_report.csv"))
    assert df.to_csv(sep=",", index=False, line_terminator="\n") == report_text
    assert list(df.columns) == list(report_attributes["columns"].keys())
    assert df.iloc[1].loc["Col1"] == 'Project 1'
    assert df.iloc[0].loc["Col2"] == "Kelly"
    assert df.iloc[0].loc["Col3"] == 'Appalachian Environmental Health Literacy: Building Knowledge and Skills to Protect Health.'
    

def test_create_tabular_project_report_excel(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict):
    
    report_attributes = {"columns":{"Col1":"<project_name>", "Col2":"<author_first>", "Col3":"<title>", "Col4":"<pub_author_first>"},
                         "filename":"project_report.csv",
                         "file_format":"xlsx"}
    
    project_name = "Project 1"
    
    filename = "project_report.csv"
    
    create_tabular_project_report(publication_dict, config_dict, authors_by_project_dict, pubs_by_author_dict, project_name, report_attributes, TESTING_DIR, filename)
    
    dir_contents = os.listdir(TESTING_DIR)
    
    assert "project_report.csv.xlsx" in dir_contents
    
    df = pandas.read_excel(os.path.join(TESTING_DIR, "project_report.csv.xlsx"))
    assert list(df.columns) == list(report_attributes["columns"].keys())
    assert df.iloc[1].loc["Col1"] == 'Project 1'
    assert df.iloc[0].loc["Col2"] == "Kelly"
    assert df.iloc[0].loc["Col3"] == 'Appalachian Environmental Health Literacy: Building Knowledge and Skills to Protect Health.'
    assert df.iloc[0].loc["Col4"] == "Anna G"
    
    


def test_replace_keywords(publication_dict, config_dict):
    
    template = {"Col1":"<project_name>", "Col2":"<author_first>", "Col3":"<title>", "Col4":"<pub_author_first>"}
    
    expected_template = {"Col1":"Project 1", "Col2":"Anna", "Col3":"Appalachian Environmental Health Literacy: Building Knowledge and Skills to Protect Health.", "Col4":"Travis"}
    
    pub_author = {"firstname":"Travis",
                  "lastname":"Thompson",
                  "initials":"P.T.T.",
                  "affiliation":"University of Kentucky"}
    
    actual_template = replace_keywords(template, publication_dict, config_dict, project_name="Project 1", author="Anna Hoover", pub="32095784", pub_author=pub_author)
    
    assert expected_template == actual_template
    

def test_replace_keywords_more_keywords(publication_dict, config_dict):
    
    template = {"Col1":"<first_author>", "Col2":"<last_author>", "Col3":"<authors>", "Col4":"<grants>", "Col5":"<publication_year>"}
    
    expected_template = {"Col1":'Hoover, Anna G', "Col2":'Brewer, Dawn', "Col3":'Anna G Hoover, Annie Koempel, W Jay Christian, Kimberly I Tumlin, Kelly G Pennell, Steven Evans, Malissa McAlister, Lindell E Ormsbee, Dawn Brewer', "Col4":'G08 LM013185, P30 ES026529, P42 ES007380, R01 ES032396', "Col5":"2020"}
    
    pub_author = {"firstname":"Travis",
                  "lastname":"Thompson",
                  "initials":"P.T.T.",
                  "affiliation":"University of Kentucky"}
    
    actual_template = replace_keywords(template, publication_dict, config_dict, project_name="Project 1", author="Anna Hoover", pub="32095784", pub_author=pub_author)
    
    assert expected_template == actual_template
    
    
    
def test_replace_keywords_no_change(publication_dict, config_dict):
    
    template = {"Col1":"<project_name>", "Col2":"<author_first>", "Col3":"<title>", "Col4":"<pub_author_first>"}
    
    expected_template = template
    
    actual_template = replace_keywords(template, publication_dict, config_dict)
    
    assert expected_template == actual_template
    
    



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

