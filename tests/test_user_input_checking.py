# -*- coding: utf-8 -*-


import pytest
from jsonschema import FormatChecker, ValidationError
from contextlib import nullcontext as does_not_raise
from academic_tracker.user_input_checking import tracker_validate, cli_inputs_check, config_file_check, author_file_check, prev_pubs_file_check
from fixtures import passing_config


@pytest.fixture
def empty_args():
    return {"--help":None,
            "--version":None,
            "--verbose":None,
            "--test":None,
            "--grants":None,
            "--cutoff_year":None,
            "--from_email":None,
            "--cc_email":None,
            "--prev_pub":None,
            "--affiliations":None,}


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
             "other_error_type": {"type": "number", "maximum":100}
             },
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
        ({"--grants":""}),                  ##minItems
        ({"--grants":"asdf,"}),             ##minLength  type inside array is not possible to check
        ({"--cutoff_year":"asdf"}),
        ({"--affiliations":""}),                 
        ({"--affiliations":"asdf,"}),
        ({"--from_email":""}),
        ({"--cc_email":""}),                 
        ({"--cc_email":"asdf,"}), 
        ({"--cc_email":"asdf"}),            ##format
        ({"--prev_pub":""}),
        ])


def test_cli_inputs_check_errors(empty_args, args):
    
    empty_args.update(args)
    
    with pytest.raises(SystemExit):
        cli_inputs_check(empty_args)
        

def test_cli_inputs_check_no_error(empty_args):
    with does_not_raise():
        cli_inputs_check(empty_args)
        
        

    
@pytest.mark.parametrize("config_errors", [
        ({"grants":""}),        ##type
        ({"grants":[]}),        ##minItems
        ({"grants":[123]}),     ##item type
        ({"grants":[""]}),      ##item minLength
        ({"cutoff_year":"123"}),
        ({"affiliations":""}),        ##type
        ({"affiliations":[]}),        ##minItems
        ({"affiliations":[123]}),     ##item type
        ({"affiliations":[""]}),      ##item minLength
        ({"from_email":123}),
        ({"from_email":"asdf"}),    ## format
        ({"cc_email":"asdf"}),
        ({"cc_email":["asdf", "email@email.com"]}),
        ({"email_template":123}),
        ({"email_template":""}),
        ({"email_template":"asdf"}),
        ({"email_subject":123}),
        ({"email_subject":""}),
        ])
 
 
def test_config_file_check_errors(passing_config, config_errors):
    passing_config.update(config_errors)
    with pytest.raises(SystemExit):
        config_file_check(passing_config)


def test_config_file_check_no_error(passing_config):
    with does_not_raise():
        config_file_check(passing_config)


def test_config_file_check_empty_file_error():
    with pytest.raises(SystemExit):
        config_file_check({})

def test_config_file_check_missing_required_error(passing_config):
    del passing_config["grants"]
    with pytest.raises(SystemExit):
        config_file_check(passing_config)
        
        


@pytest.fixture
def passing_author():
    return {
              "Andrew Morris": {
                "email": "a.j.morris@uky.edu",
                "first_name": "Andrew",
                "last_name": "Morris",
                "pubmed_name_search": "Andrew Morris"
              }
            }
    
@pytest.mark.parametrize("author_errors", [
        ({"grants":""}),        ##type
        ({"grants":[]}),        ##minItems
        ({"grants":[123]}),     ##item type
        ({"grants":[""]}),      ##item minLength
        ({"cutoff_year":"123"}),
        ({"affiliations":""}),        ##type
        ({"affiliations":[]}),        ##minItems
        ({"affiliations":[123]}),     ##item type
        ({"affiliations":[""]}),      ##item minLength
        ({"from_email":123}),
        ({"from_email":"asdf"}),    ## format
        ({"cc_email":"asdf"}),
        ({"cc_email":["asdf", "email@email.com"]}),
        ({"email_template":123}),
        ({"email_template":""}),
        ({"email_template":"asdf"}),
        ({"email_subject":123}),
        ({"email_subject":""}),
        
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
 
 
def test_author_file_check_errors(passing_author, author_errors):
    passing_author.update(author_errors)
    with pytest.raises(SystemExit):
        author_file_check(passing_author)


def test_author_file_check_no_error(passing_author):
    with does_not_raise():
        author_file_check(passing_author)


def test_author_file_check_empty():
    with pytest.raises(SystemExit):
        author_file_check({})

def test_author_file_check_missing_required_error(passing_author):
    del passing_author["Andrew Morris"]["first_name"]
    with pytest.raises(SystemExit):
        author_file_check(passing_author)






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
             'publication_date': '2019-01-04',
             'pubmed_id': '30602735',
             'results': None,
             'title': 'Correction: Synaptic phospholipids as a new target for cortical hyperexcitability and E/I balance in psychiatric disorders.'}
 }
    
@pytest.mark.parametrize("pub_errors", [
        ({"abstract":123}),
        ({"authors":123}),
        ({"authors":[]}),
        ({"authors":[{"affiliation":"asdf", "firstname":"asdf", "initials":"asdf", "lastname":123}]}),
        ({"authors":[{"affiliation":"asdf", "firstname":"asdf", "initials":123, "lastname":"asdf"}]}),
        ({"authors":[{"affiliation":"asdf", "firstname":123, "initials":"asdf", "lastname":"asdf"}]}),
        ({"authors":[{"affiliation":123, "firstname":"asdf", "initials":"asdf", "lastname":"asdf"}]}),
        ({"conclusions":123}),
        ({"copyrights":123}),
        ({"doi":123}),
        ({"journal":123}),
        ({"keywords":123}),
        ({"keywords":[123]}),
        ({"methods":123}),
        ({"publication_date":123}),
        ({"pubmed_id":123}),
        ({"results":123}),
        ({"title":123}),
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
































