# -*- coding: utf-8 -*-
"""
Tracker Schema
~~~~~~~~~~~~~~

JSON Schema for the input JSON files.
"""

import copy

## TODO add the file inputs and look into adding file existence checking in jsonschema format checker.
cli_schema = {
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "title": "Command Line Inputs",
 "description": "Schema to check that program arguments are valid.",
 
 "type": "object",
 "properties": {
         "--prev_pub": {"type":["string", "null"], "minLength":1},
         },
         
}


config_schema = \
    {
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "title": "Configuration JSON",
 "description": "Input file that contains information for how the program should run.",

 "type": "object",
 "properties": {
         "project_descriptions" : {
             "type": "object",
             "minProperties": 1,
             "additionalProperties": {
                     "type":"object",
                     "properties":{
                             "grants": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}},
                             "cutoff_year": {"type": "integer", "minimum":1000, "maximum":9999},
                             "affiliations": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}},
                             "project_report": {"type": "object",
                                                "properties":{
                                                        "columns": {"type": "object",
                                                                    "minProperties":1,
                                                                    "additionalProperties": {"type": "string", "minLength":1}},
                                                        "sort": {"type": "array", "uniqueItems":True, "items": {"type": "string", "minLength":1}, "minItems":1},
                                                        "separator":{"type":"string", "maxLength":1, "minLength":1},
                                                        "column_order":{"type":"array", "uniqueItems":True, "items": {"type": "string", "minLength":1}, "minItems":1},
                                                        "file_format":{"type":"string", "enum":["csv", "xlsx"]},
                                                        "filename":{"type":"string", "minLength":1},
                                                        "template": {"type": "string", "minLength":1},
                                                        "from_email": {"type": "string", "format": "email"},
                                                        "cc_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
                                                        "to_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
                                                        "email_body": {"type": "string", "minLength":1},
                                                        "email_subject": {"type": "string", "minLength":1},},
                                                "dependentRequired":{
                                                        "from_email": ["email_body", "email_subject"],
                                                        "to_email": ["from_email", "email_body", "email_subject"]}},
                             "collaborator_report": {"type": "object",
                                                     "properties":{
                                                             "columns": {"type": "object",
                                                                         "minProperties":1,
                                                                         "additionalProperties": {"type": "string", "minLength":1}},
                                                             "sort": {"type": "array", "uniqueItems":True, "items": {"type": "string", "minLength":1}, "minItems":1},
                                                             "separator":{"type":"string", "maxLength":1, "minLength":1},
                                                             "column_order":{"type":"array", "uniqueItems":True, "items": {"type": "string", "minLength":1}, "minItems":1},
                                                             "file_format":{"type":"string", "enum":["csv", "xlsx"]},
                                                             "filename":{"type":"string", "minLength":1},
                                                             "template": {"type": "string", "minLength":1},
                                                             "from_email": {"type": "string", "format": "email"},
                                                             "cc_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
                                                             "to_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
                                                             "email_body": {"type": "string", "minLength":1},
                                                             "email_subject": {"type": "string", "minLength":1},},
                                                     "dependentRequired":{
                                                             "from_email": ["email_body", "email_subject"],
                                                             "to_email": ["from_email", "email_body", "email_subject"]},},
                             "authors": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}},
                             },
                             
                     "required": ["grants", "affiliations"]
                     }
            },
             
        "ORCID_search" : {"type":"object",
                          "properties": {
                                  "ORCID_key": {"type": "string", "minLength":1},
                                  "ORCID_secret": {"type": "string", "minLength":1}},
                          "required": ["ORCID_key", "ORCID_secret"]},
        "PubMed_search" : {"type":"object",
                          "properties": {
                                  "PubMed_email": {"type": "string", "format":"email"}},
                          "required":["PubMed_email"]},
        "Crossref_search" : {"type":"object",
                          "properties": {
                                  "mailto_email": {"type": "string", "format":"email"}},
                          "required":["mailto_email"]},
        "summary_report" : {"type": "object",
                          "properties":{
                                  "columns": {"type": "object",
                                              "minProperties":1,
                                              "additionalProperties": {"type": "string", "minLength":1}},
                                  "sort": {"type": "array", "uniqueItems":True, "items": {"type": "string", "minLength":1}, "minItems":1},
                                  "separator":{"type":"string", "maxLength":1, "minLength":1},
                                  "column_order":{"type":"array", "uniqueItems":True, "items": {"type": "string", "minLength":1}, "minItems":1},
                                  "file_format":{"type":"string", "enum":["csv", "xlsx"]},
                                  "filename":{"type":"string", "minLength":1},
                                  "template": {"type": "string", "minLength":1},
                                  "from_email": {"type": "string", "format": "email"},
                                  "cc_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
                                  "to_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
                                  "email_body": {"type": "string", "minLength":1},
                                  "email_subject": {"type": "string", "minLength":1},},
                          "dependentRequired":{
                                  "from_email": ["email_body", "email_subject", "to_email"]}},
        "Authors" :  { "type": "object",
                     "minProperties": 1,
                     "additionalProperties": {
                             "type": "object",
                             "properties":{
                                     "pubmed_name_search": {"type": "string", "minLength":1},
                                     "email":{"type": "string", "format":"email"},
                                     "ORCID":{"type": "string", "pattern":r"^\d{4}-\d{4}-\d{4}-\d{3}[0,1,2,3,4,5,6,7,8,9,X]$"},
                                     "grants": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}},
                                     "cutoff_year": {"type": "integer", "minimum":1000, "maximum":9999},
                                     "scholar_id": {"type": "string", "minLength":1},
                                     "project_report": {"type": "object",
                                                "properties":{
                                                        "columns": {"type": "object",
                                                                    "minProperties":1,
                                                                    "additionalProperties": {"type": "string", "minLength":1}},
                                                        "sort": {"type": "array", "uniqueItems":True, "items": {"type": "string", "minLength":1}, "minItems":1},
                                                        "separator":{"type":"string", "maxLength":1, "minLength":1},
                                                        "column_order":{"type":"array", "uniqueItems":True, "items": {"type": "string", "minLength":1}, "minItems":1},
                                                        "file_format":{"type":"string", "enum":["csv", "xlsx"]},
                                                        "filename":{"type":"string", "minLength":1},
                                                        "template": {"type": "string", "minLength":1},
                                                        "from_email": {"type": "string", "format": "email"},
                                                        "cc_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
                                                        "to_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
                                                        "email_body": {"type": "string", "minLength":1},
                                                        "email_subject": {"type": "string", "minLength":1},},
                                                "dependentRequired":{
                                                        "from_email": ["email_body", "email_subject"],
                                                        "to_email": ["from_email", "email_body", "email_subject"]}},
                                    "collaborator_report": {"type": "object",
                                                     "properties":{
                                                             "columns": {"type": "object",
                                                                         "minProperties":1,
                                                                         "additionalProperties": {"type": "string", "minLength":1}},
                                                             "sort": {"type": "array", "uniqueItems":True, "items": {"type": "string", "minLength":1}, "minItems":1},
                                                             "separator":{"type":"string", "maxLength":1, "minLength":1},
                                                             "column_order":{"type":"array", "uniqueItems":True, "items": {"type": "string", "minLength":1}, "minItems":1},
                                                             "file_format":{"type":"string", "enum":["csv", "xlsx"]},
                                                             "filename":{"type":"string", "minLength":1},
                                                             "template": {"type": "string", "minLength":1},
                                                             "from_email": {"type": "string", "format": "email"},
                                                             "cc_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
                                                             "to_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
                                                             "email_body": {"type": "string", "minLength":1},
                                                             "email_subject": {"type": "string", "minLength":1},},
                                                     "dependentRequired":{
                                                             "from_email": ["email_body", "email_subject"],
                                                             "to_email": ["from_email", "email_body", "email_subject"]},},
                                     },
                             "if": {
                                 "properties":{"collective_name":{"type": "string", "minLength":1}},
                                 "required":["collective_name"]
                                 },
                             "then":{
                                 "properties":{"collective_name":{"type": "string", "minLength":1}},
                                 "required":["collective_name"]
                                 },
                             "else":{
                                 "properties": {
                                         "affiliations": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}},
                                         "first_name": {"type": "string", "minLength":1},
                                         "last_name":{"type": "string", "minLength":1},
                                      },
                                   "required": ["first_name", "last_name"]},
                             "required" : ["pubmed_name_search"]
                             }
                       }
                                  
     },
 "required": ["project_descriptions", "ORCID_search", "PubMed_search", "Crossref_search", "Authors"]
}
## config_end Marker to denote the end of the schema for documentation.



ORCID_schema = copy.deepcopy(config_schema)
new_properties = {}
new_properties["ORCID_search"] = ORCID_schema["properties"]["ORCID_search"]
new_properties["Authors"] = ORCID_schema["properties"]["Authors"]
ORCID_schema["properties"] = new_properties
ORCID_schema["required"] = ["ORCID_search", "Authors"]


Authors_schema = copy.deepcopy(config_schema)
new_properties = {}
new_properties["Authors"] = Authors_schema["properties"]["Authors"]
Authors_schema["properties"] = new_properties
Authors_schema["required"] = ["Authors"]


ref_config_schema = copy.deepcopy(config_schema)
del ref_config_schema["properties"]["ORCID_search"]
del ref_config_schema["properties"]["Authors"]
del ref_config_schema["properties"]["project_descriptions"]
ref_config_schema["required"] = ["PubMed_search", "Crossref_search"]

gen_reports_auth_schema = copy.deepcopy(config_schema)
del gen_reports_auth_schema["properties"]["PubMed_search"]
del gen_reports_auth_schema["properties"]["ORCID_search"]
del gen_reports_auth_schema["properties"]["Crossref_search"]
gen_reports_auth_schema["required"] = ["project_descriptions", "Authors"]

gen_reports_ref_schema = copy.deepcopy(ref_config_schema)
del gen_reports_ref_schema["properties"]["PubMed_search"]
del gen_reports_ref_schema["properties"]["Crossref_search"]
del gen_reports_ref_schema["required"]




publications_schema={
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "title": "Publications JSON",
 "description": "Input file that contains information about publications previously found by Academic Tracker.",
 
 "type": "object",
 "additionalProperties": {
         "type": "object",
         "properties": {
                "abstract": {"type":["string", "null"]},
                "authors": {"type":"array", 
                            "minItems":1, 
                            "items": {"type": "object", 
                                      "properties": {"ORCID": {"type": ["string", "null"], "pattern":r"^\d{4}-\d{4}-\d{4}-\d{3}[0,1,2,3,4,5,6,7,8,9,X]$"}},
                                      "if": {
                                          "properties":{"collectivename":{"type":["string", "null"]}},
                                          "required":["collectivename"]
                                          },
                                      "then":{
                                          "properties":{"collectivename":{"type":["string", "null"]}},
                                          "required":["collectivename"]
                                          },
                                      "else":{
                                          "properties": {
                                                  "affiliation": {"type": ["string", "null"]},
                                                  "firstname": {"type": ["string", "null"]},
                                                  "initials": {"type": ["string", "null"]},
                                                  "lastname": {"type": ["string", "null"]},
                                                  "author_id" : {"type": ["string", "null"]}  # optional, only put in if author detected and validated
                                               },
                                            "required": ["affiliation", "firstname", "lastname", "initials"]}
                                        }
                            },
                "conclusions": {"type": ["string", "null"]},
                "copyrights": {"type": ["string", "null"]},
                "doi": {"type": ["string", "null"]},
                "journal": {"type": ["string", "null"]},
                "keywords": {"type": ["array", "null"], "items":{"type": ["string", "null"]}},
                "methods": {"type": ["string", "null"]},
                "publication_date": {"type": "object", 
                                     "properties":{"year": {"type": ["integer", "null"]},
                                                   "month": {"type": ["integer", "null"]},
                                                   "day": {"type": ["integer", "null"]}},
                                     "required":["year", "month", "day"]},
                "pubmed_id": {"type": ["string", "null"]},
                "results": {"type": ["string", "null"]},
                "title": {"type": ["string", "null"]},
                "grants": {"type": ["array", "null"], "items":{"type": ["string", "null"]}},
                "PMCID": {"type": ["string", "null"]},
                },
         "required" : ["abstract", "authors", "conclusions", "copyrights", "doi", "journal", "keywords", "methods", "publication_date", "pubmed_id", "results", "title"]
         }
}



tok_schema = {
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "title": "Tokenized Citations JSON",
 "description": "Input file that contains the tokenized data of a reference file.",
 
 "type": "array",
 "items": {"type": "object",
           "minItems":1,
           "properties": {"authors": {"type": "array",
                                      "items": {"type": "object",
                                                "properties": {"ORCID": {"type": ["string", "null"], "pattern":r"^\d{4}-\d{4}-\d{4}-\d{3}[0,1,2,3,4,5,6,7,8,9,X]$"}},
                                                "if": {
                                                    "properties":{"collective_name":{"type":["string", "null"]}},
                                                    "required":["collective_name"]
                                                    },
                                                "then":{
                                                    "properties":{"collective_name":{"type":["string", "null"]}},
                                                    "required":["collective_name"]
                                                    },
                                                "else":{
                                                    "properties": {"last": {"type":["string", "null"]},
                                                                   "initials": {"type":["string", "null"]},
                                                                   "first": {"type":["string", "null"]},
                                                                   "middle": {"type":["string", "null"]}},
                                                    "required": ["last"]}
                                                }},
                          "title": {"type":["string", "null"]},
                          "PMID": {"type":["string", "null"]},
                          "DOI": {"type":["string", "null"]},
                          "reference_line": {"type":["string", "null"]},
                          "pub_dict_key": {"type":["string", "null"]}},
           "required": ["authors", "title", "PMID", "DOI", "reference_line", "pub_dict_key"]}
}




PMID_reference_schema = {
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "title": "PMID Reference JSON",
 "description": "Input file that contains a list of PMIDs.",
 
 "type": "array",
 "items": {"type": "string",
           "minItems":1,
           }
}



