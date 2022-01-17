# -*- coding: utf-8 -*-
"""
This module contains the functions that check the user input for errors.
"""


import sys
import re
import jsonschema
from . import tracker_schema





def tracker_validate(instance, schema, pattern_messages={}, cls=None, *args, **kwargs):
    """Wrapper around jsonchema.validate to give better error messages.
    
    Args:
        instance (dict): JSON as a dict to validate
        schema (dict): JSON schema as a dict to validate instance against
        pattern_messages (dict): if the instance has a ValidationError of the pattern type then look up the attribute that failed the pattern in this dict and see if there is a custom message
    """
    

    try:
        jsonschema.validate(instance=instance, schema=schema, cls=cls, *args, **kwargs)
    except jsonschema.ValidationError as e:
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
    
    tracker_validate(instance=args, schema=tracker_schema.cli_schema, format_checker=jsonschema.FormatChecker())







def config_file_check(config_json, args):
    """Check that the configuration JSON file is as expected.
    
    The configuration JSON file format is expected to be:
    {
           "project_descriptions" : {
               "<project-name>" : {
                  "grants" : [ "P42ES007380", "P42 ES007380" ],
                  "cutoff_year" : 2019, # optional
                  "affiliations" : [ "kentucky" ],
                  "project_report" : { # optional 
                          "template": "<formatted_string>",
                          "to_email": [],    #optional
                          "cc_email": []    #optional
                          "from_email": "<email>",  #optional
                          "email_body": "<body>",    #optional
                          "email_subject": "<subject>",   #optional              
                      },
                  "authors" : [], # optional
                  },...
           },
               "ORCID_search" : {
                  "ORCID_key": "<ORCID_key>",
                  "ORCID_secret": "<ORCID_secret>"
           },
               "PubMed_search": {
                  "PubMed_email": "<PubMed_email>" 
           },
               "Crossref_search": {
                  "mailto_email": "<mailto_email>" 
           },
               "summary_report" : { # optional 
                   "template": "<formatted_string>",
                   "to_email": [],    #optional
                   "cc_email": []    #optional
                   "from_email": "<email>",  #optional
                   "email_body": "<body>",    #optional
                   "email_subject": "<subject>",   #optional              
           },
               "Authors" : {
                  "Author 1": {  
                           "first_name" : "<first-name>",
                           "last_name" : "<last-name>",
                           "pubmed_name_search" : "<search-str>",
                           "email": "email@uky.edu",
                           "ORCID": "<orcid>" # optional       
                           "affiliations" : ["<affiliation1>", "<affiliation2>"] #optional    
                        },
            
                  "Author 2": {  
                           "first_name" : "<first-name>",
                           "last_name" : "<last-name>",
                           "pubmed_name_search" : "<search-str>", # optional
                           "email": "email@uky.edu",
                           "ORCID": "<orcid>" # optional 
                           "affiliations" : ["<affiliation1>", "<affiliation2>"] #optional
                        },
           }
         }
    
    
    Args:
        config_json (dict): dict with the same structure as the configuration JSON file
        args (dict): dict of the input args to the program
    """
    
    schema = tracker_schema.config_schema
    if args["--no_ORCID"]:
        del schema["properties"]["ORCID_search"]
    if args["--no_Crossref"] and args["--no_GoogleScholar"]:
        del schema["properties"]["Crossref_search"]
    
    pattern_messages = {"ORCID":" is not a valid ORCID. It must match the regex \d{4}-\d{4}-\d{4}-\d{3}[0,1,2,3,4,5,6,7,8,9,X]"}
    tracker_validate(instance=config_json, schema=schema, pattern_messages=pattern_messages, format_checker=jsonschema.FormatChecker())
    
    for project, project_attributes in config_json["project_descriptions"].items():
        if not "cc_email" in project_attributes:
            project_attributes["cc_email"] = []
            
    if "summary_report" in config_json and not "cc_email" in config_json["summary_report"]:
            config_json["summary_report"]["cc_email"] = []
    
            

def ref_config_file_check(config_json, args):
    """Check that the configuration JSON file is as expected.
    
    The configuration JSON file format is expected to be:
    {
       "project_descriptions" : {
           "<project-name> : {
              "from_email" : "ptth222@uky.edu", #optional
              "to_email" : [], # optional
              "cc_email" : [], # optional
              "email_template" : "<formatted-string>", #optional
              "email_subject" : "<formatted-string>", #optional
              "report_ref_template" : <formatted-string>, #optional
              },...
             },
           "PubMed_search": {
              "PubMed_email": "<PubMed_email>"
            },
           "Crossref_search": {
              "mailto_email": "<mailto_email>"
            },
    }
    
    
    Args:
        config_json (dict): dict with a truncated structure of the configuration JSON file
        args (dict): dict of the input args to the program
    """
    
    schema = tracker_schema.ref_config_schema
    if args["--no_Crossref"]:
        del schema["properties"]["Crossref_search"]
    
    tracker_validate(instance=config_json, schema=schema, format_checker=jsonschema.FormatChecker())
    
    if "summary_report" in config_json and not "cc_email" in config_json["summary_report"]:
            config_json["summary_report"]["cc_email"] = []
            
        
 



# def author_file_check(authors_json):
#     """Run input checking on the authors_json.
#
#     The authors_json read in from the authors JSON file is expected to have the format::
#         {
#             "Author 1": {
#                            "first_name" : "<first_name>",
#                            "last_name" : "<last_name>",
#                            "pubmed_name_search" : "<search-str>",
#                            "email": "email@uky.edu",
#                            "ORCID": "<orcid>" # optional
#                            "affiliations" : ["<affiliation1>", "<affiliation2>"] #optional
#                         },
#
#             "Author 2": {
#                            "first_name" : "<first_name>",
#                            "last_name" : "<last_name>",
#                            "pubmed_name_search" : "<search-str>",
#                            "email": "email@uky.edu",
#                            "ORCID": "<orcid>" # optional
#                            "affiliations" : ["<affiliation1>", "<affiliation2>"] #optional
#                         },
#         }
#
#
#     Args:
#         authors_json (dict): dict with the same structure as the authors JSON file.
#     """
#
#     pattern_messages = {"ORCID":" is not a valid ORCID. It must match the regex \d{4}-\d{4}-\d{4}-\d{3}[0,1,2,3,4,5,6,7,8,9,X]"}
#     tracker_validate(instance=authors_json, schema=tracker_schema.authors_schema, pattern_messages=pattern_messages, format_checker=jsonschema.FormatChecker())





def prev_pubs_file_check(prev_pubs):
    """Run input checking on prev_pubs dict.
    
    The prev_pubs read in from the previous publications JSON file is expected to have the format:
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
                "grants : ["grant1", "grant2"],
                "PMCID" : "<PMCID>"
              },
        }
            
    
    Args:
        prev_pubs (dict): dict with the same structure as the previous publications JSON file.
    """
    
    tracker_validate(instance=prev_pubs, schema=tracker_schema.publications_schema, format_checker=jsonschema.FormatChecker())
    


def tok_reference_check(tok_ref):
    """Run input checking on tok_ref dict.
    
    The tok_ref read in from JSON is expected to have the format:
        {
           "authors": {"last": "<last>", "initials": "<initials>", "first": "<first>", "middle": "<middle>"},
           "title": "<title>",
           "PMID": "<PMID>",
           "DOI": "<DOI>"
        }
            
    Args:
        tok_ref (dict): dict with the same structure as the tokenized reference JSON file.
    """
    
    tracker_validate(instance=tok_ref, schema=tracker_schema.tok_schema, format_checker=jsonschema.FormatChecker())









