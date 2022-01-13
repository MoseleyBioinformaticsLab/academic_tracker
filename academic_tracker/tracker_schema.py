# -*- coding: utf-8 -*-
"""
JSON Schema for the cli, authors, and config JSON.
"""

import copy


cli_schema = {
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "title": "Command Line Inputs",
 "description": "Input file that contains information for how the program should run.",
 
 "type": "object",
 "properties": {
         "--grants": {"type": ["array", "null"], "minItems":1, "items": {"type": "string", "minLength": 1}},
         "--cutoff_year": {"type": ["integer", "null"]},
         "--affiliations": {"type": ["array", "null"], "minItems":1, "items": {"type": "string", "minLength": 1}},
         "--from_email": {"type": ["string", "null"], "format": "email"},
         "--cc_email": {"type": ["array", "null"],  "items": {"type": "string", "format": "email"}},
         "--prev_pub": {"type":["string", "null"], "minLength":1},
         "<to_email>": {"type": ["string", "null"], "format": "email"},
         "<from_email>": {"type": ["string", "null"], "format": "email"},
         },
         
}


config_schema = {
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
                             "cutoff_year": {"type": "integer"},
                             "affiliations": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}}, 
                             "from_email": {"type": "string", "format": "email"},
                             "cc_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
                             "to_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
                             "email_template": {"type": "string", "minLength":1},
                             "email_subject": {"type": "string", "minLength":1},
                             "report_ref_template": {"type": "string", "minLength":1},
                             "authors": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}},
                             },
                             
                     "required": ["grants", "cutoff_year", "affiliations", "from_email", "email_template", "email_subject"]
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
        "Authors" :  { "type": "object",
                     "minProperties": 1,
                     "additionalProperties": {
                             "type": "object",
                             "properties":{
                                     "first_name": {"type": "string", "minLength":1},
                                     "last_name":{"type": "string", "minLength":1},
                                     "pubmed_name_search": {"type": "string", "minLength":1},
                                     "email":{"type": "string", "format":"email"},
                                     "ORCID":{"type": "string", "pattern":"^\d{4}-\d{4}-\d{4}-\d{3}[0,1,2,3,4,5,6,7,8,9,X]$"},
                                     "grants": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}},
                                     "cutoff_year": {"type": "integer"},
                                     "affiliations": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}},
                                     "from_email": {"type": "string", "format": "email"},
                                     "cc_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
                                     "email_template": {"type": "string", "minLength":1, "pattern": "(?s)^.*<total_pubs>.*$"},
                                     "email_subject": {"type": "string", "minLength":1},
                                     "scholar_id": {"type": "string", "minLength":1},
                                     },
                             "required" : ["first_name", "last_name", "pubmed_name_search", "email"]

                             }
                       }
                                  
     },
 "required": ["project_descriptions", "ORCID_search", "PubMed_search", "Crossref_search", "Authors"]
}




ORCID_schema = copy.deepcopy(config_schema)
ORCID_schema["properties"] = ORCID_schema["properties"]["ORCID_search"]
ORCID_schema["required"] = ["ORCID_search"]


PubMed_schema = copy.deepcopy(config_schema)
PubMed_schema["properties"] = PubMed_schema["properties"]["PubMed_search"]
PubMed_schema["required"] = ["PubMed_search"]


ref_config_schema = copy.deepcopy(config_schema)
del ref_config_schema["properties"]["ORCID_search"]
del ref_config_schema["properties"]["Authors"]
ref_config_schema["required"] = ["PubMed_search", "Crossref_search"]
ref_config_schema["properties"]["project_descriptions"]["additionalProperties"]["required"] = []


# authors_schema = {
#  "$schema": "https://json-schema.org/draft/2020-12/schema",
#  "title": "Authors JSON",
#  "description": "Input file that contains information about the authors'.",
#
#  "type": "object",
#  "minProperties": 1,
#  "additionalProperties": {
#          "type": "object",
#          "properties":{
#                  "first_name": {"type": "string", "minLength":1},
#                  "last_name":{"type": "string", "minLength":1},
#                  "pubmed_name_search": {"type": "string", "minLength":1},
#                  "email":{"type": "string", "format":"email"},
#                  "ORCID":{"type": "string", "pattern":"^\d{4}-\d{4}-\d{4}-\d{3}[0,1,2,3,4,5,6,7,8,9,X]$"},
#                  "grants": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}},
#                  "cutoff_year": {"type": "integer"},
#                  "affiliations": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}},
#                  "from_email": {"type": "string", "format": "email"},
#                  "cc_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
#                  "email_template": {"type": "string", "minLength":1, "pattern": "(?s)^.*<total_pubs>.*$"},
#                  "email_subject": {"type": "string", "minLength":1},
#                  "scholar_id": {"type": "string", "minLength":1},
#                  },
#          "required" : ["first_name", "last_name", "pubmed_name_search", "email"]
#
#          }
#
# }
         
         


publications_schema={
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "title": "Publications JSON",
 "description": "Input file that contains information about publications previously found by Academic Tracker.",
 
 "type": "object",
 "additionalProperties": {
         "type": "object",
         "properties": {
                "abstract": {"type":"string"},
                "authors": {"type":"array", 
                            "minItems":1, 
                            "items": {"type": "object", 
                                      "properties": {
                                              "affiliation": {"type": ["string", "null"]},
                                              "firstname": {"type": ["string", "null"]},
                                              "initials": {"type": ["string", "null"]},
                                              "lastname": {"type": ["string", "null"]},
                                              "author_id" : {"type": "string"}  # optional, only put in if author detected and validated
                                           },
                                        "required": ["affiliation", "firstname", "lastname", "initials"]
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















