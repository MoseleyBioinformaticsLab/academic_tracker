# -*- coding: utf-8 -*-


import pytest
from jsonschema import FormatChecker, ValidationError
from contextlib import nullcontext as does_not_raise

from academic_tracker.user_input_checking import tracker_validate, cli_inputs_check, config_file_check, config_report_check
from academic_tracker.user_input_checking import prev_pubs_file_check, ref_config_file_check, tok_reference_check
from fixtures import passing_config


@pytest.fixture
def empty_args():
    return {"--verbose":False,
            "--test":False,
            "--prev_pub":None,
            '--MEDLINE_reference': False,
            '--PMID_reference': False,
            '--no_Crossref': False,
            '--no_GoogleScholar': False,
            '--no_ORCID': False,}


## Commenting $schema out because the jsonschema package produces warnings if left in. It is a known issue in their package. 10-18-2021
@pytest.fixture
def test_schema():
    schema = {
#     "$schema": "https://json-schema.org/draft/2020-12/schema",
     "title": "Test Schema",
     "description": "Schema to test tracker_validate",
     
     "type": "object",
     "minProperties":1,
     "properties": {
             "required_test":{"type": "object",
                              "properties": {"required_test": {"type": "string"}},
                              "required": ["required_test"]},
             "empty_string_test": {"type": "string", "minLength": 1},
             "empty_list_test": {"type": "array", "minItems":1},
             "wrong_type_test": {"type": "string"}, 
             "wrong_format_test": {"type": "string", "format": "email"},
             "wrong_pattern_test": {"type": "string", "pattern": "^asdf$"},
             "other_error_type": {"type": "number", "exclusiveMaximum":100}
             },
     "dependentRequired":{"dependency":["dependent_field"]},
     "required": ["required_test"]
             
    }
     
    return schema
 


@pytest.mark.parametrize("instance, error_message", [
        
        ({}, "ValidationError: An error was found in the Test Schema. \nThe Test Schema cannot be empty."),
        ({"asdf":"asdf"}, "ValidationError: An error was found in the Test Schema. \nThe required property \'required_test\' is missing."),
        ({"required_test":{"asdf":"asdf"}}, "ValidationError: An error was found in the Test Schema. \nThe entry [\'required_test\'] is missing the required property \'required_test\'."),
        ({"required_test":{"required_test":""}, "empty_string_test":""}, "ValidationError: An error was found in the Test Schema. \nThe value for ['empty_string_test'] cannot be an empty string."),
        ({"required_test":{"required_test":""}, "empty_list_test":[]}, "ValidationError: An error was found in the Test Schema. \nThe value for ['empty_list_test'] cannot be empty."),
        ({"required_test":{"required_test":""}, "wrong_type_test":123}, "ValidationError: An error was found in the Test Schema. \nThe value for ['wrong_type_test'] is not of type \"string\"."),
        ({"required_test":{"required_test":""}, "wrong_format_test":"asdf"}, "ValidationError: An error was found in the Test Schema. \nThe value for ['wrong_format_test'] is not a valid email."),
        ({"required_test":{"required_test":""}, "wrong_pattern_test":"qwer"}, "ValidationError: An error was found in the Test Schema. \nThe value for ['wrong_pattern_test'] did not fit the pattern."),
        ({"required_test":{"required_test":""}, "dependency":""}, "ValidationError: An error was found in the Test Schema. \nThe entry [] is missing a dependent property.\n'dependent_field' is a dependency of 'dependency'"),
        ])


def test_tracker_validate_custom_messages(instance, test_schema, error_message, capsys):
    
    pattern_messages = {"wrong_pattern_test": " did not fit the pattern."}
    
    with pytest.raises(SystemExit):
        tracker_validate(instance, test_schema, pattern_messages, format_checker=FormatChecker())
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"



def test_tracker_validate_other_errors(test_schema, capsys):
    
    instance = {"required_test":{"required_test":""}, "other_error_type":1000}
    
    with pytest.raises(ValidationError):
        tracker_validate(instance, test_schema)
        

def test_tracker_validate_no_error(test_schema):
    with does_not_raise():
        tracker_validate({"required_test":{"required_test":""}}, test_schema)



@pytest.mark.parametrize("args", [
        ({"--prev_pub":""}),
        ])


def test_cli_inputs_check_errors(empty_args, args):
    
    empty_args.update(args)
    
    with pytest.raises(SystemExit):
        cli_inputs_check(empty_args)
        

def test_cli_inputs_check_no_error(empty_args):
    with does_not_raise():
        cli_inputs_check(empty_args)
        
        

#######################
## Author Config
#######################   
@pytest.mark.parametrize("config_project_errors", [
        ({"grants":""}),        ##type
        ({"grants":[]}),        ##minItems
        ({"grants":[123]}),     ##item type
        ({"grants":[""]}),      ##item minLength
        ({"cutoff_year":"123"}),
        ({"cutoff_year":1}),
        ({"cutoff_year":99999}),
        ({"affiliations":""}),        ##type
        ({"affiliations":[]}),        ##minItems
        ({"affiliations":[123]}),     ##item type
        ({"affiliations":[""]}),      ##item minLength
        ({"project_report":123}),
        ({"project_report":{"template":"asdf", ## dependency No email_subject
                            "from_email":"email@email.com", 
                            "cc_email":["email@email.com"],
                            "email_body":"asdf"}}),
        ({"project_report":{"template":"asdf",  ## dependency No email_body
                            "from_email":"email@email.com", 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",}}),
        ({"project_report":{"template":"asdf",   ## dependency No from_email
                            "to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",
                            "email_body":"asdf"}}),
        ({"project_report":{"template":"asdf",  ## dependency No email_subject
                            "from_email":"email@email.com", 
                            "to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_body":"asdf"}}),
        ({"project_report":{"template":"asdf",  ## dependency No email_body
                            "from_email":"email@email.com", 
                            "to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",}}),
        ({"collaborator_report":123}),
        ({"collaborator_report":{"from_email":"email@email.com", 
                            "cc_email":["email@email.com"],
                            "email_body":"asdf"}}),
        ({"collaborator_report":{"from_email":"email@email.com", 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",}}),
        ({"collaborator_report":{"to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",
                            "email_body":"asdf"}}),
        ({"collaborator_report":{"from_email":"email@email.com", 
                            "to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_body":"asdf"}}),
        ({"collaborator_report":{"from_email":"email@email.com", 
                            "to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",}}),
        ({"authors":""}),        ##type
        ({"authors":[]}),        ##minItems
        ({"authors":[123]}),     ##item type
        ({"authors":[""]}),      ##item minLength
        ])
 
 
def test_config_file_project_check_errors(passing_config, config_project_errors):
    passing_config["project_descriptions"]["project 1"].update(config_project_errors)
    with pytest.raises(SystemExit):
        config_file_check(passing_config, False, False, False, False)
        



@pytest.mark.parametrize("project_report_errors", [
        ({"from_email":123}),
        ({"from_email":"asdf"}),    ## format
        ({"cc_email":"asdf"}),
        ({"cc_email":["asdf", "email@email.com"]}),
        ({"to_email":"asdf"}),
        ({"to_email":["asdf", "email@email.com"]}),
        ({"columns":123}),
        ({"columns":{}}),
        ({"columns":{"asdf":""}}),
        ({"sort":123}),
        ({"sort":[]}),
        ({"separator":123}),
        ({"separator":""}),
        ({"separator":"asdf"}),
        ({"column_order":123}),
        ({"column_order":[]}),
        ({"file_format":123}),
        ({"file_format":"asdf"}),
        ({"filename":123}),
        ({"filename":""}),
        ({"template":123}),
        ({"template":""}),
        ({"email_subject":123}),
        ({"email_subject":""}),
        ({"email_body":123}),
        ({"email_body":""}),
        ])
 
 
def test_config_file_project_report_attributes_check_errors(passing_config, project_report_errors):
    passing_config["project_descriptions"]["project 1"]["project_report"].update(project_report_errors)
    with pytest.raises(SystemExit):
        config_file_check(passing_config, False, False, False, False)
        

def test_config_file_project_report_sort_error_project(passing_config, capsys):
    passing_config["project_descriptions"]["project 1"]["project_report"] = {"columns":{"Name":"asdf"},
                                                                                  "sort":["asdf"]}
    error_message = "ValidationError: The \"sort\" attribute for the project_report in project project 1 " +\
                      "has values that are not column names in \"columns\".\nThe following names in \"sort\" " +\
                      "could not be matched to a column in \"columns\":\n\nasdf"
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
    

def test_config_file_project_report_column_order_error_project(passing_config, capsys):
    passing_config["project_descriptions"]["project 1"]["project_report"] = {"columns":{"Name":"asdf"},
                                                                                  "column_order":["asdf"]}
    error_message = "ValidationError: The \"column_order\" attribute for the project_report in project project 1 " +\
                      "has values that are not column names in \"columns\".\nThe following names in \"column_order\" " +\
                      "could not be matched to a column in \"columns\":\n\nasdf"
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
    

def test_config_file_project_report_column_order_error_not_all_names_project(passing_config, capsys):
    passing_config["project_descriptions"]["project 1"]["project_report"] = {"columns":{"Name":"asdf",
                                                                                        "Title":"asdf"},
                                                                                  "column_order":["Name"]}
    error_message = "ValidationError: The \"column_order\" attribute for the project_report in project project 1 " +\
                      "does not have all of the column names in \"columns\". Every column in \"columns\" must be in \"column_order\"."
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
    
    
def test_config_file_project_report_sort_error_author(passing_config, capsys):
    passing_config["Authors"]["Andrew Morris"]["project_report"] = {"columns":{"Name":"asdf"},
                                                                          "sort":["asdf"]}
    error_message = "ValidationError: The \"sort\" attribute for the project_report for author Andrew Morris " +\
                      "has values that are not column names in \"columns\".\nThe following names in \"sort\" " +\
                      "could not be matched to a column in \"columns\":\n\nasdf"
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
    

def test_config_file_project_report_column_order_error_author(passing_config, capsys):
    passing_config["Authors"]["Andrew Morris"]["project_report"] = {"columns":{"Name":"asdf"},
                                                                          "column_order":["asdf"]}
    error_message = "ValidationError: The \"column_order\" attribute for the project_report for author Andrew Morris " +\
                      "has values that are not column names in \"columns\".\nThe following names in \"column_order\" " +\
                      "could not be matched to a column in \"columns\":\n\nasdf"
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
    

def test_config_file_project_report_column_order_error_not_all_names_author(passing_config, capsys):
    passing_config["Authors"]["Andrew Morris"]["project_report"] = {"columns":{"Name":"asdf",
                                                                                "Title":"asdf"},
                                                                                  "column_order":["Name"]}
    error_message = "ValidationError: The \"column_order\" attribute for the project_report for author Andrew Morris " +\
                      "does not have all of the column names in \"columns\". Every column in \"columns\" must be in \"column_order\"."
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
        


@pytest.mark.parametrize("collaborator_report_errors", [
        ({"from_email":123}),
        ({"from_email":"asdf"}),    ## format
        ({"cc_email":"asdf"}),
        ({"cc_email":["asdf", "email@email.com"]}),
        ({"to_email":"asdf"}),
        ({"to_email":["asdf", "email@email.com"]}),
        ({"columns":123}),
        ({"columns":{}}),
        ({"columns":{"asdf":""}}),
        ({"sort":123}),
        ({"sort":[]}),
        ({"separator":123}),
        ({"separator":""}),
        ({"separator":"asdf"}),
        ({"column_order":123}),
        ({"column_order":[]}),
        ({"file_format":123}),
        ({"file_format":"asdf"}),
        ({"filename":123}),
        ({"filename":""}),
        ({"template":123}),
        ({"template":""}),
        ({"email_subject":123}),
        ({"email_subject":""}),
        ({"email_body":123}),
        ({"email_body":""}),
        ])
 
 
def test_config_file_collaborator_report_attributes_check_errors(passing_config, collaborator_report_errors):
    passing_config["project_descriptions"]["project 1"]["collaborator_report"].update(collaborator_report_errors)
    with pytest.raises(SystemExit):
        config_file_check(passing_config, False, False, False, False)
        
        
def test_config_file_collaborator_report_sort_error_project(passing_config, capsys):
    passing_config["project_descriptions"]["project 1"]["collaborator_report"] = {"columns":{"Name":"asdf"},
                                                                                  "sort":["asdf"]}
    error_message = "ValidationError: The \"sort\" attribute for the collaborator_report in project project 1 " +\
                      "has values that are not column names in \"columns\".\nThe following names in \"sort\" " +\
                      "could not be matched to a column in \"columns\":\n\nasdf"
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
    

def test_config_file_collaborator_report_column_order_error_project(passing_config, capsys):
    passing_config["project_descriptions"]["project 1"]["collaborator_report"] = {"columns":{"Name":"asdf"},
                                                                                  "column_order":["asdf"]}
    error_message = "ValidationError: The \"column_order\" attribute for the collaborator_report in project project 1 " +\
                      "has values that are not column names in \"columns\".\nThe following names in \"column_order\" " +\
                      "could not be matched to a column in \"columns\":\n\nasdf"
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
    

def test_config_file_collaborator_report_column_order_error_not_all_names_project(passing_config, capsys):
    passing_config["project_descriptions"]["project 1"]["collaborator_report"] = {"columns":{"Name":"asdf",
                                                                                        "Title":"asdf"},
                                                                                  "column_order":["Name"]}
    error_message = "ValidationError: The \"column_order\" attribute for the collaborator_report in project project 1 " +\
                      "does not have all of the column names in \"columns\". Every column in \"columns\" must be in \"column_order\"."
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
    
    
def test_config_file_collaborator_report_sort_error_author(passing_config, capsys):
    passing_config["Authors"]["Andrew Morris"]["collaborator_report"] = {"columns":{"Name":"asdf"},
                                                                          "sort":["asdf"]}
    error_message = "ValidationError: The \"sort\" attribute for the collaborator_report for author Andrew Morris " +\
                      "has values that are not column names in \"columns\".\nThe following names in \"sort\" " +\
                      "could not be matched to a column in \"columns\":\n\nasdf"
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
    

def test_config_file_collaborator_report_column_order_error_author(passing_config, capsys):
    passing_config["Authors"]["Andrew Morris"]["collaborator_report"] = {"columns":{"Name":"asdf"},
                                                                          "column_order":["asdf"]}
    error_message = "ValidationError: The \"column_order\" attribute for the collaborator_report for author Andrew Morris " +\
                      "has values that are not column names in \"columns\".\nThe following names in \"column_order\" " +\
                      "could not be matched to a column in \"columns\":\n\nasdf"
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
    

def test_config_file_collaborator_report_column_order_error_not_all_names_author(passing_config, capsys):
    passing_config["Authors"]["Andrew Morris"]["collaborator_report"] = {"columns":{"Name":"asdf",
                                                                                "Title":"asdf"},
                                                                                  "column_order":["Name"]}
    error_message = "ValidationError: The \"column_order\" attribute for the collaborator_report for author Andrew Morris " +\
                      "does not have all of the column names in \"columns\". Every column in \"columns\" must be in \"column_order\"."
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
        


@pytest.mark.parametrize("summary_report_errors", [
        ({"from_email":123}),
        ({"from_email":"asdf"}),    ## format
        ({"cc_email":"asdf"}),
        ({"cc_email":["asdf", "email@email.com"]}),
        ({"to_email":"asdf"}),
        ({"to_email":["asdf", "email@email.com"]}),
        ({"columns":123}),
        ({"columns":{}}),
        ({"columns":{"asdf":""}}),
        ({"sort":123}),
        ({"sort":[]}),
        ({"separator":123}),
        ({"separator":""}),
        ({"separator":"asdf"}),
        ({"column_order":123}),
        ({"column_order":[]}),
        ({"file_format":123}),
        ({"file_format":"asdf"}),
        ({"filename":123}),
        ({"filename":""}),
        ({"template":123}),
        ({"template":""}),
        ({"email_subject":123}),
        ({"email_subject":""}),
        ({"email_body":123}),
        ({"email_body":""}),
        ])
    
def test_config_file_summary_report_attributes_check_errors(passing_config, summary_report_errors):
    passing_config["summary_report"].update(summary_report_errors)
    with pytest.raises(SystemExit):
        config_file_check(passing_config, False, False, False, False)
        

def test_config_file_summary_report_sort_error_project(passing_config, capsys):
    passing_config["summary_report"] = {"columns":{"Name":"asdf"},
                                        "sort":["asdf"]}
    error_message = "ValidationError: The \"sort\" attribute for the summary_report " +\
                      "has values that are not column names in \"columns\".\nThe following names in \"sort\" " +\
                      "could not be matched to a column in \"columns\":\n\nasdf"
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
    

def test_config_file_summary_report_column_order_error_project(passing_config, capsys):
    passing_config["summary_report"] = {"columns":{"Name":"asdf"},
                                        "column_order":["asdf"]}
    error_message = "ValidationError: The \"column_order\" attribute for the summary_report " +\
                      "has values that are not column names in \"columns\".\nThe following names in \"column_order\" " +\
                      "could not be matched to a column in \"columns\":\n\nasdf"
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
    

def test_config_file_summary_report_column_order_error_not_all_names_project(passing_config, capsys):
    passing_config["summary_report"] = {"columns":{"Name":"asdf",
                                                    "Title":"asdf"},
                                                    "column_order":["Name"]}
    error_message = "ValidationError: The \"column_order\" attribute for the summary_report " +\
                      "does not have all of the column names in \"columns\". Every column in \"columns\" must be in \"column_order\"."
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"



@pytest.mark.parametrize("summary_report_errors", [
        ({"summary_report":123}),
        ({"summary_report":{"template":"asdf",  ## dependency No to_email
                            "from_email":"email@email.com", 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",
                            "email_body":"asdf"}}),
        ({"summary_report":{"template":"asdf",  ## dependency No email_subject
                            "from_email":"email@email.com", 
                            "to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_body":"asdf"}}),
        ({"summary_report":{"template":"asdf",  ## dependency No email_body
                            "from_email":"email@email.com", 
                            "to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",}}),
        ])
    
def test_config_file_summary_report_check_errors(passing_config, summary_report_errors):
    passing_config.update(summary_report_errors)
    with pytest.raises(SystemExit):
        config_file_check(passing_config, False, False, False, False)



@pytest.mark.parametrize("config_ORCID_errors", [
        ({"ORCID_key":123}),
        ({"ORCID_key":""}),
        ({"ORCID_secret":123}),
        ({"ORCID_secret":""}),
        ])
 
 
def test_config_file_ORCID_check_errors(passing_config, config_ORCID_errors):
    passing_config["ORCID_search"].update(config_ORCID_errors)
    with pytest.raises(SystemExit):
        config_file_check(passing_config, False, False, False, False)



@pytest.mark.parametrize("config_PubMed_errors", [
        ({"PubMed_email":123}),
        ({"PubMed_email":"asdf"}),
        ])
 
 
def test_config_file_PubMed_check_errors(passing_config, config_PubMed_errors):
    passing_config["PubMed_search"].update(config_PubMed_errors)
    with pytest.raises(SystemExit):
        config_file_check(passing_config, False, False, False, False)
        

@pytest.mark.parametrize("config_Crossref_errors", [
        ({"mailto_email":123}),
        ({"mailto_email":"asdf"}),
        ])
 
 
def test_config_file_Crossref_check_errors(passing_config, config_Crossref_errors):
    passing_config["Crossref_search"].update(config_Crossref_errors)
    with pytest.raises(SystemExit):
        config_file_check(passing_config, False, False, False, False)


def test_config_file_check_no_error(passing_config):
    with does_not_raise():
        config_file_check(passing_config, False, False, False, False)


def test_config_file_check_empty_file_error():
    with pytest.raises(SystemExit):
        config_file_check({}, False, False, False, False)

def test_config_file_check_missing_required_error(passing_config):
    del passing_config["project_descriptions"]
    with pytest.raises(SystemExit):
        config_file_check(passing_config, False, False, False, False)
        
        
    
@pytest.mark.parametrize("author_errors", [
        ({"grants":""}),        ##type
        ({"grants":[]}),        ##minItems
        ({"grants":[123]}),     ##item type
        ({"grants":[""]}),      ##item minLength
        ({"cutoff_year":"123"}),
        ({"cutoff_year":1}),
        ({"cutoff_year":99999}),
        ({"affiliations":""}),        ##type
        ({"affiliations":[]}),        ##minItems
        ({"affiliations":[123]}),     ##item type
        ({"affiliations":[""]}),      ##item minLength
        ({"project_report":123}),
        ({"project_report":{"template":"asdf", ## dependency No email_subject
                            "from_email":"email@email.com", 
                            "cc_email":["email@email.com"],
                            "email_body":"asdf"}}),
        ({"project_report":{"template":"asdf",  ## dependency No email_body
                            "from_email":"email@email.com", 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",}}),
        ({"project_report":{"template":"asdf",   ## dependency No from_email
                            "to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",
                            "email_body":"asdf"}}),
        ({"project_report":{"template":"asdf",  ## dependency No email_subject
                            "from_email":"email@email.com", 
                            "to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_body":"asdf"}}),
        ({"project_report":{"template":"asdf",  ## dependency No email_body
                            "from_email":"email@email.com", 
                            "to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",}}),
        ({"collaborator_report":123}),
        ({"collaborator_report":{"from_email":"email@email.com", 
                            "cc_email":["email@email.com"],
                            "email_body":"asdf"}}),
        ({"collaborator_report":{"from_email":"email@email.com", 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",}}),
        ({"collaborator_report":{"to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",
                            "email_body":"asdf"}}),
        ({"collaborator_report":{"from_email":"email@email.com", 
                            "to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_body":"asdf"}}),
        ({"collaborator_report":{"from_email":"email@email.com", 
                            "to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",}}),
        ({"first_name":123}),
        ({"first_name":""}),
        ({"last_name":123}),
        ({"last_name":""}),
        ({"pubmed_name_search":123}),
        ({"pubmed_name_search":""}),
        ({"email":123}),
        ({"email":"asdf"}),
        ({"ORCID":123}),
        ({"ORCID":"asdf"}),    ##pattern
        ])
 
 
def test_author_file_check_errors(passing_config, author_errors):
    passing_config["Authors"]["Andrew Morris"].update(author_errors)
    with pytest.raises(SystemExit):
        config_file_check(passing_config, False, False, False, False)
        


def test_config_file_check_schema_reduction(passing_config):
    del passing_config["ORCID_search"]["ORCID_key"]
    del passing_config["Crossref_search"]
    del passing_config["PubMed_search"]
    with does_not_raise():
        config_file_check(passing_config, True, True, True, True)




#######################
## Reference Config
#######################
@pytest.mark.parametrize("summary_report_errors", [
        ({"from_email":123}),
        ({"from_email":"asdf"}),    ## format
        ({"cc_email":"asdf"}),
        ({"cc_email":["asdf", "email@email.com"]}),
        ({"to_email":"asdf"}),
        ({"to_email":["asdf", "email@email.com"]}),
        ({"template":123}),
        ({"template":""}),
        ({"email_subject":123}),
        ({"email_subject":""}),
        ({"email_body":123}),
        ({"email_body":""}),
        ])
    
def test_ref_config_file_summary_report_attributes_check_errors(passing_config, summary_report_errors):
    passing_config["summary_report"].update(summary_report_errors)
    with pytest.raises(SystemExit):
        ref_config_file_check(passing_config, False, False)
        

def test_ref_config_file_summary_report_sort_error_project(passing_config, capsys):
    passing_config["summary_report"] = {"columns":{"Name":"asdf"},
                                        "sort":["asdf"]}
    error_message = "ValidationError: The \"sort\" attribute for the summary_report " +\
                      "has values that are not column names in \"columns\".\nThe following names in \"sort\" " +\
                      "could not be matched to a column in \"columns\":\n\nasdf"
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"
    

def test_ref_config_file_summary_report_column_order_error_project(passing_config, capsys):
    passing_config["summary_report"] = {"columns":{"Name":"asdf"},
                                        "column_order":["asdf"]}
    error_message = "ValidationError: The \"column_order\" attribute for the summary_report " +\
                      "has values that are not column names in \"columns\".\nThe following names in \"column_order\" " +\
                      "could not be matched to a column in \"columns\":\n\nasdf"
    with pytest.raises(SystemExit):
        config_report_check(passing_config)
    captured = capsys.readouterr()
    assert captured.out == error_message + "\n"



@pytest.mark.parametrize("summary_report_errors", [
        ({"summary_report":123}),
        ({"summary_report":{"template":"asdf",  ## dependency No to_email
                            "from_email":"email@email.com", 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",
                            "email_body":"asdf"}}),
        ({"summary_report":{"template":"asdf",  ## dependency No email_subject
                            "from_email":"email@email.com", 
                            "to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_body":"asdf"}}),
        ({"summary_report":{"template":"asdf",  ## dependency No email_body
                            "from_email":"email@email.com", 
                            "to_email":["email@email.com"], 
                            "cc_email":["email@email.com"],
                            "email_subject":"asdf",}}),
        ])
    
def test_ref_config_file_summary_report_check_errors(passing_config, summary_report_errors):
    passing_config.update(summary_report_errors)
    with pytest.raises(SystemExit):
        ref_config_file_check(passing_config, False, False)



@pytest.mark.parametrize("config_PubMed_errors", [
        ({"PubMed_email":123}),
        ({"PubMed_email":"asdf"}),
        ])
 
 
def test_ref_config_file_PubMed_check_errors(passing_config, config_PubMed_errors):
    passing_config["PubMed_search"].update(config_PubMed_errors)
    with pytest.raises(SystemExit):
        ref_config_file_check(passing_config, False, False)
        

@pytest.mark.parametrize("config_Crossref_errors", [
        ({"mailto_email":123}),
        ({"mailto_email":"asdf"}),
        ])
 
 
def test_ref_config_file_Crossref_check_errors(passing_config, config_Crossref_errors):
    passing_config["Crossref_search"].update(config_Crossref_errors)
    with pytest.raises(SystemExit):
        ref_config_file_check(passing_config, False, False)


def test_ref_config_file_check_no_error(passing_config):
    with does_not_raise():
        ref_config_file_check(passing_config, False, False)


def test_ref_config_file_check_empty_file_error():
    with pytest.raises(SystemExit):
        ref_config_file_check({}, False, False)

def test_ref_config_file_check_missing_required_error(passing_config):
    del passing_config["PubMed_search"]
    with pytest.raises(SystemExit):
        ref_config_file_check(passing_config, False, False)


def test_ref_config_file_check_schema_reduction(passing_config):
    del passing_config["Crossref_search"]
    del passing_config["PubMed_search"]
    with does_not_raise():
        ref_config_file_check(passing_config, True, True)




@pytest.fixture
def passing_pubs():
    return {"30602735" : {
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
              'title': 'Correction: Synaptic phospholipids as a new target for cortical hyperexcitability and E/I balance in psychiatric disorders.',
              'grants':['P42 ES007380', 'P42 ES007381'],
              'PMCID':'PMC7933073'}
  }
    
@pytest.mark.parametrize("pub_errors", [
        ({"abstract":123}),
        ({"authors":123}),
        ({"authors":[]}),
        ({"authors":[{"affiliation":"asdf", "firstname":"asdf", "initials":"asdf", "lastname":123}]}),
        ({"authors":[{"affiliation":"asdf", "firstname":"asdf", "initials":123, "lastname":"asdf"}]}),
        ({"authors":[{"affiliation":"asdf", "firstname":123, "initials":"asdf", "lastname":"asdf"}]}),
        ({"authors":[{"affiliation":123, "firstname":"asdf", "initials":"asdf", "lastname":"asdf"}]}),
        ({"authors":[{"firstname":"asdf", "initials":"asdf", "lastname":"asdf"}]}),
        ({"authors":[{"affiliation":"asdf", "initials":"asdf", "lastname":"asdf"}]}),
        ({"authors":[{"affiliation":"asdf", "firstname":"adf", "lastname":"asdf"}]}),
        ({"authors":[{"affiliation":"asdf", "firstname":"asdf", "initials":"asdf"}]}),
        ({"conclusions":123}),
        ({"copyrights":123}),
        ({"doi":123}),
        ({"journal":123}),
        ({"keywords":123}),
        ({"keywords":[123]}),
        ({"methods":123}),
        ({"publication_date":123}),
        ({"publication_date":{"year":"asdf", "month":1, "day":1}}),
        ({"publication_date":{"year":1, "month":"asdf", "day":1}}),
        ({"publication_date":{"year":1, "month":1, "day":"asdf"}}),
        ({"publication_date":{"year":1, "month":1, }}),
        ({"publication_date":{"year":1, "day":1}}),
        ({"publication_date":{"month":1, "day":1}}),
        ({"pubmed_id":123}),
        ({"results":123}),
        ({"title":123}),
        ({"grants":123}),
        ({"grants":[123]}),
        ({"PMCID":123}),
        ])
 
 
def test_prev_pubs_file_check_errors(passing_pubs, pub_errors):
    passing_pubs.update(pub_errors)
    with pytest.raises(SystemExit):
        prev_pubs_file_check(passing_pubs)


def test_prev_pubs_file_check_no_error(passing_pubs):
    with does_not_raise():
        prev_pubs_file_check(passing_pubs)


def test_prev_pubs_file_check_missing_required_error(passing_pubs):
    del passing_pubs["30602735"]["abstract"]
    with pytest.raises(SystemExit):
        prev_pubs_file_check(passing_pubs)




@pytest.fixture
def passing_tok():
    return [{"authors": [{"last": "Last", "initials": "", "first": "First", "middle": ""}],
            "title": "Pub Title",
            "PMID": "",
            "DOI": "",
            "reference_line": "", 
            "pub_dict_key": ""}]

@pytest.mark.parametrize("tok_errors", [
        ({"authors":123}),
        ({"authors":[{"last":"asdf", "first":"asdf", "initials":"asdf", "middle":123}]}),
        ({"authors":[{"last":"asdf", "first":"asdf", "initials":123, "middle":"asdf"}]}),
        ({"authors":[{"last":"asdf", "first":123, "initials":"asdf", "middle":"asdf"}]}),
        ({"authors":[{"last":123, "first":"asdf", "initials":"asdf", "middle":"asdf"}]}),
        ({"authors":[{"first":"asdf", "initials":"asdf", "middle":"asdf"}]}),
        ({"title":123}),
        ({"PMID":123}),
        ({"DOI":123}),
        ({"reference_line":123}),
        ({"pub_dict_key":123}),
        ])


def test_tok_reference_check_errors(passing_tok, tok_errors):
    passing_tok[0].update(tok_errors)
    with pytest.raises(SystemExit):
        tok_reference_check(passing_tok)
    
    
def test_tok_reference_check_no_error(passing_tok):
    with does_not_raise():
        tok_reference_check(passing_tok)
    
    
def test_tok_reference_check_missing_required_error(passing_tok):
    del passing_tok[0]["title"]
    with pytest.raises(SystemExit):
        tok_reference_check(passing_tok)








