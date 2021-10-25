# -*- coding: utf-8 -*-
"""
This module contains the functions that check the user input for errors.
"""


import sys
import re
from jsonschema import validate, FormatChecker, ValidationError
from .tracker_schema import config_schema, authors_schema, cli_schema, publications_schema





def tracker_validate(instance, schema, pattern_messages={}, cls=None, *args, **kwargs):
    """Wrapper around jsonchema.validate to give better error messages.
    
    Args:
        instance (dict): JSON as a dict to validate
        schema (dict): JSON schema as a dict to validate instance against
        pattern_messages (dict): if the instance has a ValidationError of the pattern type then look up the attribute that failed the pattern in this dict and see if there is a custom message
        
    
    """
    

    try:
        validate(instance=instance, schema=schema, cls=cls, *args, **kwargs)
    except ValidationError as e:
        ## code to easily see the contents of the error for building a better message.
#        for key, value in e._contents().items():
#            print(key, value)
#            print()
        
        message = "ValidationError: An error was found in the " + schema["title"] + ". \n"
        custom_message = ""
        
        if e.validator == "minProperties":
            message += "The " + schema["title"] + " cannot be empty."
        elif e.validator == "required":
            required_property = re.match(r"(\'.*\')", e.message).group(1)
            if len(e.relative_path) == 0:
                message += "The required property " + required_property + " is missing."
            else:
                message += "The entry " + "[%s]" % "][".join(repr(index) for index in e.relative_path) + " is missing the required property " + required_property + "."
        elif e.validator == "minLength":
            custom_message = " cannot be an empty string."
        elif e.validator == "minItems":
            custom_message = " cannot be empty."
        elif e.validator == "type":
            if type(e.validator_value) == list:
                custom_message = " is not any of the allowed types: ["
                for allowed_type in e.validator_value:
                    custom_message += "\'" + allowed_type + "\', "
                custom_message = custom_message[:-2]
                custom_message += "]."
            else:
                custom_message = " is not of type \"" + e.validator_value + "\"."
        elif e.validator == "format":
            custom_message = " is not a valid " + e.validator_value + "."
        elif e.validator == "pattern" and e.relative_path[-1] in pattern_messages:
            custom_message = pattern_messages[e.relative_path[-1]]
        else:
            raise e
        
        
        if custom_message:
            message = message + "The value for " + "[%s]" % "][".join(repr(index) for index in e.relative_path) + custom_message
        print(message)
        sys.exit()




def cli_inputs_check(args):
    """Run input checking on the CLI inputs.
    
    First converts comma separated lists as strings into lists and then uses
    jsonschema to validate the inputs.
            
    
    Args:
        args (dict): dict from docopt.
    
    
    """
    
    list_args = ["--grants", "--affiliations", "--cc_email"]
    
    for arg in list_args:
        if args[arg]:
            args[arg] = args[arg].split(",")
            
    int_args = ["--cutoff_year"]
    
    for arg in int_args:
        if args[arg]:
            try:
                args[arg] = int(args[arg])
            except:
                pass
    
    tracker_validate(instance=args, schema=cli_schema, format_checker=FormatChecker())







def config_file_check(config_json):
    """Check that the configuration JSON file is as expected.
    
    The configuration JSON file format is expected to be::
        {
             "grants" : [ "P42ES007380", "P42 ES007380" ],
             "cutoff_year" : 2019,
             "affiliations" : [ "kentucky" ],
             "from_email" : "ptth222@uky.edu",
             "cc_email" : [], # optional
             "email_template" : "<formatted-string>",
             "email_subject" : "<formatted-string>"
        }
    
    
    Args:
        config_json (dict): dict with the same structure as the configuration JSON file
        
    
    """
    
    pattern_messages = {"email_template":" does not contain <total_pubs>."}
    tracker_validate(instance=config_json, schema=config_schema, pattern_messages=pattern_messages, format_checker=FormatChecker())
    
            




def author_file_check(authors_dict):
    """Run input checking on the authors_dict.
    
    The authors_dict read in from the authors JSON file is expected to have the format::
        {
            "Author 1": {  
                           "first_name" : "<first_name>",
                           "last_name" : "<last_name>",
                           "pubmed_name_search" : "<search-str>",
                           "email": "email@uky.edu",
                           "ORCID": "<orcid>" # optional      
                           "affiliations" : ["<affiliation1>", "<affiliation2>"] #optional
                        },
            
            "Author 2": {  
                           "first_name" : "<first_name>",
                           "last_name" : "<last_name>",
                           "pubmed_name_search" : "<search-str>",
                           "email": "email@uky.edu",       
                           "ORCID": "<orcid>" # optional 
                           "affiliations" : ["<affiliation1>", "<affiliation2>"] #optional
                        },
        }
            
    
    Args:
        authors_dict (dict): dict with the same structure as the authors JSON file.
    
    
    """
    
    pattern_messages = {"ORCID":" is not a valid ORCID. It must match the regex \d{4}-\d{4}-\d{4}-\d{3}[0,1,2,3,4,5,6,7,8,9,X]"}
    tracker_validate(instance=authors_dict, schema=authors_schema, pattern_messages=pattern_messages, format_checker=FormatChecker())





def prev_pubs_file_check(prev_pubs):
    """Run input checking on prev_pubs dict.
    
    The prev_pubs read in from the previous publications JSON file is expected to have the format::
        {
           "pub_id1": 
              {
                "abstract": "<publication abstract>",
                "authors": [
                   {
                      "affiliation": "<comma separated list of affiliations>",
                      "firstname": "<author first name>",
                      "initials": "<author initials>",
                      "lastname": "<author last name>",
                      "author_id": "<author_id>"        ## Optional, only added if author is detected and validated
                   },
                ],
                "conclusions": "<publication conclusions>",
                "copyrights": "<copyrights>",
                "doi": "DOI string",
                "journal": "<journal name>",
                "keywords": ["keyword 1", "keyword 2"],
                "methods": "<publication methods>",
                "publication_date": "yyyy-mm-dd",
                "pubmed_id": "<pubmed id>",
                "results": "<publication results>",
                "title": "<publication title>"
              },
        }
            
    
    Args:
        prev_pubs (dict): dict with the same structure as the previous publications JSON file.
    
    """
    
    tracker_validate(instance=prev_pubs, schema=publications_schema, format_checker=FormatChecker())
    











