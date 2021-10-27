# -*- coding: utf-8 -*-
"""
JSON Schema for the cli, authors, and config JSON.
"""

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
         "--prev_pub": {"type":["string", "null"], "minLength":1}
         },
         
}



config_schema = {
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "title": "Configuration JSON",
 "description": "Input file that contains information for how the program should run.",
 
 "type": "object",
 "minProperties": 1,
 "properties": {
         "grants": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}},
         "cutoff_year": {"type": "integer"},
         "affiliations": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}}, 
         "from_email": {"type": "string", "format": "email"},
         "cc_email": {"type": "array",  "items": {"type": "string", "format": "email"}},
         "email_template": {"type": "string", "minLength":1, "pattern": "(?s)^.*<total_pubs>.*$"},
         "email_subject": {"type": "string", "minLength":1}},
         
 "required": ["grants", "cutoff_year", "affiliations", "from_email", "email_template", "email_subject"]
 
}





authors_schema = {
 "$schema": "https://json-schema.org/draft/2020-12/schema",
 "title": "Authors JSON",
 "description": "Input file that contains information about the authors'.",
 
 "type": "object",
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
                 },
         "required" : ["first_name", "last_name", "pubmed_name_search", "email"]
         
         }
        
}
         
         


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
                "publication_date": {"type": ["string", "null"]},
                "pubmed_id": {"type": ["string", "null"]},
                "results": {"type": ["string", "null"]},
                "title": {"type": ["string", "null"]},
                },
         "required" : ["abstract", "authors", "conclusions", "copyrights", "doi", "journal", "keywords", "methods", "publication_date", "pubmed_id", "results", "title"]
         }
}














