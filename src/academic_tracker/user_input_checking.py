# -*- coding: utf-8 -*-
"""
User Input Checking
~~~~~~~~~~~~~~~~~~~

Functions that check the user input for errors.
"""


import sys
import re
import copy

import jsonschema

from . import tracker_schema
from . import helper_functions





def tracker_validate(instance, schema, pattern_messages={}, cls=None, *args, **kwargs):
    """Wrapper around jsonchema.validate to give better error messages.
    
    Args:
        instance (dict): JSON as a dict to validate
        schema (dict): JSON schema as a dict to validate instance against
        pattern_messages (dict): if the instance has a ValidationError of the pattern type then look up the attribute that failed the pattern in this dict and see if there is a custom message
        
    Raises:
        jsonshcema.ValidationError: If an unexpected jsonschema error happens this is raised rather than a system exit.
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
        ## In an older version of JSON Schema the keyword was "dependencies" instead of "dependentRequired".
        elif e.validator == "dependencies":
            message += "The entry " + "[%s]" % "][".join(repr(index) for index in e.relative_path) + " is missing a dependent property.\n"
            message += e.message
        elif e.validator == "dependentRequired":
            message += "The entry " + "[%s]" % "][".join(repr(index) for index in e.relative_path) + " is missing a dependent property.\n"
            message += e.message
        elif e.validator == "minLength":
            custom_message = " cannot be an empty string."
        elif e.validator == "maxLength":
            custom_message = " is too long."
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
        elif e.validator == "enum":
            custom_message = " is not one of [" + "%s" % ", ".join(repr(index) for index in e.validator_value) + "]"
        elif e.validator == "format":
            custom_message = " is not a valid " + e.validator_value + "."
        elif e.validator == "pattern" and e.relative_path[-1] in pattern_messages:
            custom_message = pattern_messages[e.relative_path[-1]]
        elif e.validator == "minimum":
            custom_message = " must be greater than or equal to " + str(e.validator_value)
        elif e.validator == "maximum":
            custom_message = " must be less than or equal to " + str(e.validator_value)
        else:
            raise e
        
        
        if custom_message:
            message = message + "The value for " + "[%s]" % "][".join(repr(index) for index in e.relative_path) + custom_message
        print(message)
        sys.exit()




def cli_inputs_check(args):
    """Run input checking on the CLI inputs.
    
    Uses jsonschema to validate the inputs.
            
    Args:
        args (dict): dict from docopt.
    """
    
#    list_args = ["--grants", "--affiliations", "--cc_email"]
#    
#    for arg in list_args:
#        if args[arg]:
#            args[arg] = args[arg].split(",")
#            
#    int_args = ["--cutoff_year"]
#    
#    for arg in int_args:
#        if args[arg]:
#            try:
#                args[arg] = int(args[arg])
#            except:
#                pass
    
    tracker_validate(instance=args, schema=tracker_schema.cli_schema, format_checker=jsonschema.FormatChecker())







def config_file_check(config_json, no_ORCID, no_GoogleScholar, no_Crossref, no_PubMed):
    """Check that the configuration JSON file is as expected.
    
    The validational jsonschema is in the tracker_schema module. 
    
    Args:
        config_json (dict): dict with the same structure as the configuration JSON file.
        no_ORCID (bool): if True delete the part of the schema that checks ORCID attributes.
        no_GoogleScholar (bool): if True and no_Crossref is True delete the part of the schema that checks Crossref attributes.
        no_Crossref (bool): if True and no_GoogleScholar is True delete the part of the schema that checks Crossref attributes.
        no_PubMed (bool): if True delete the part of the schema that checks PubMed attributes.
    """
    
    schema = copy.deepcopy(tracker_schema.config_schema)
    if no_ORCID:
        del schema["properties"]["ORCID_search"]
        schema["required"].remove("ORCID_search")
    if no_Crossref and no_GoogleScholar:
        del schema["properties"]["Crossref_search"]
        schema["required"].remove("Crossref_search")
    if no_PubMed:
        del schema["properties"]["PubMed_search"]
        schema["required"].remove("PubMed_search")
    
    pattern_messages = {"ORCID":" is not a valid ORCID. It must match the regex \\d{4}-\\d{4}-\\d{4}-\\d{3}[0,1,2,3,4,5,6,7,8,9,X]"}
    tracker_validate(instance=config_json, schema=schema, pattern_messages=pattern_messages, format_checker=jsonschema.FormatChecker())


            

def ref_config_file_check(config_json, no_Crossref, no_PubMed):
    """Check that the configuration JSON file is as expected.
    
    The validational jsonschema is in the tracker_schema module.    
    
    Args:
        config_json (dict): dict with a truncated structure of the configuration JSON file.
        no_Crossref (bool): if True delete the part of the schema that checks Crossref attributes.
        no_PubMed (bool): if True delete the part of the schema that checks PubMed attributes.
    """
    
    schema = copy.deepcopy(tracker_schema.ref_config_schema)
    if no_Crossref:
        del schema["properties"]["Crossref_search"]
        schema["required"].remove("Crossref_search")
    if no_PubMed:
        del schema["properties"]["PubMed_search"]
        schema["required"].remove("PubMed_search")
    
    tracker_validate(instance=config_json, schema=schema, format_checker=jsonschema.FormatChecker())    



def config_report_check(config_json):
    """Check that the report attributes don't have conflicts.
    
    Make sure that the values in sort and column_order are in columns, 
    and that every column is in column_order.
    
    Args:
        config_json (dict): dict with the same structure as the configuration JSON file.
    """
    ## Make sure sort and column_order only have values in columns for any report.
    attributes_to_check = ["sort", "column_order"]
    for attribute in attributes_to_check:
        if "summary_report" in config_json and "columns" in config_json["summary_report"] and attribute in config_json["summary_report"]:
            names_not_in_columns = [name for name in config_json["summary_report"][attribute] if not name in config_json["summary_report"]["columns"]]
            if names_not_in_columns:
                helper_functions.vprint("ValidationError: The \"" + attribute + "\" attribute for the summary_report has values that are not column names in \"columns\".")
                helper_functions.vprint("The following names in \"" + attribute + "\" could not be matched to a column in \"columns\":\n\n" + "\n".join(names_not_in_columns))
                sys.exit()   
                
            if attribute == "column_order":
                if len(config_json["summary_report"]["column_order"]) != len(config_json["summary_report"]["columns"]):
                    helper_functions.vprint("ValidationError: The \"column_order\" attribute for the summary_report does not have all of the column names in \"columns\". Every column in \"columns\" must be in \"column_order\".")
                    sys.exit() 
            
    
    if "project_descriptions" in config_json:        
        report_keys = ["collaborator_report", "project_report"]
        for project, project_attributes in config_json["project_descriptions"].items():
            for report_key in report_keys:
                for attribute in attributes_to_check:
                    if report_key in project_attributes and "columns" in project_attributes[report_key] and attribute in project_attributes[report_key]:
                        names_not_in_columns = [name for name in project_attributes[report_key][attribute] if not name in project_attributes[report_key]["columns"]]
                        if names_not_in_columns:
                            helper_functions.vprint("ValidationError: The \"" + attribute + "\" attribute for the " + report_key + " in project " + project + " has values that are not column names in \"columns\".")
                            helper_functions.vprint("The following names in \"" + attribute + "\" could not be matched to a column in \"columns\":\n\n" + "\n".join(names_not_in_columns))
                            sys.exit()
                            
                        if attribute == "column_order":
                            if len(project_attributes[report_key]["column_order"]) != len(project_attributes[report_key]["columns"]):
                                helper_functions.vprint("ValidationError: The \"column_order\" attribute for the " + report_key + " in project " + project + " does not have all of the column names in \"columns\". Every column in \"columns\" must be in \"column_order\".")
                                sys.exit() 
                                    
    
    if "Authors" in config_json:
        for author, author_attributes in config_json["Authors"].items():
            for report_key in report_keys:
                for attribute in attributes_to_check:
                    if report_key in author_attributes and "columns" in author_attributes[report_key] and attribute in author_attributes[report_key]:
                        names_not_in_columns = [name for name in author_attributes[report_key][attribute] if not name in author_attributes[report_key]["columns"]]
                        if names_not_in_columns:
                            helper_functions.vprint("ValidationError: The \"" + attribute + "\" attribute for the " + report_key + " for author " + author + " has values that are not column names in \"columns\".")
                            helper_functions.vprint("The following names in \"" + attribute + "\" could not be matched to a column in \"columns\":\n\n" + "\n".join(names_not_in_columns))
                            sys.exit()
                            
                        if attribute == "column_order":
                            if len(author_attributes[report_key]["column_order"]) != len(author_attributes[report_key]["columns"]):
                                helper_functions.vprint("ValidationError: The \"column_order\" attribute for the " + report_key + " for author " + author + " does not have all of the column names in \"columns\". Every column in \"columns\" must be in \"column_order\".")
                                sys.exit()     



def prev_pubs_file_check(prev_pubs):
    """Run input checking on prev_pubs dict.
    
    The validational jsonschema is in the tracker_schema module. 
    
    Args:
        prev_pubs (dict): dict with the same structure as the previous publications JSON file.
    """
    
    tracker_validate(instance=prev_pubs, schema=tracker_schema.publications_schema, format_checker=jsonschema.FormatChecker())
    


def tok_reference_check(tok_ref):
    """Run input checking on tok_ref dict.
    
    The validational jsonschema is in the tracker_schema module. 
            
    Args:
        tok_ref (dict): dict with the same structure as the tokenized reference JSON file.
    """
    
    tracker_validate(instance=tok_ref, schema=tracker_schema.tok_schema, format_checker=jsonschema.FormatChecker())

