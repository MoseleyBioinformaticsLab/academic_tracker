JSON Schema
===========

Academic Tracker uses and produces several JSON files in its execution. This 
document describes their structure and gives examples. `JSON Schema <https://json-schema.org/>`_ is used 
here to describe the structure and used in the program to validate inputs.

Configuration JSON
~~~~~~~~~~~~~~~~~~
The configuration JSON is required for any command used in Academic Tracker. It 
contains all the information necessary to run a command. Not every command will 
use every section of the configuration JSON, and those sections are not required 
for those commands.

Sections
--------
project_descriptions
++++++++++++++++++++
This section contains information about the funding projects your authors are 
apart of. Some of the information in this section is used during search and some 
is only used when constructing reports. 

The grants, cutoff_year, and affiliatons attributes are all used during search. 
grants is used to specifically look for the given grant strings to see if the 
queried publication is associated with them. cutoff_year is used to filter out 
publications that were published before the given year. affiliations is used 
when matching the author under search with the queried author. Each of these can 
be set for authors individually, but are presented here for convenience.

The authors attribute is used to specify which authors belong to the project. If 
the attribute is not present then it assumes that all authors are associated with 
the project. Entries for this attribute must match an entry in the Authors section 
of the configuration JSON.

project_report is used to specify that creating a project report is desired and 
how to construct and email it. If project_report is missing then no report is 
created for that project. Additional attributes within the project_report attribute 
specify how to construct the report and whether to email it. 
Details about reporting are in the :doc:`reporting` section. 

The from_email attribute within project_report is used to specify what email 
address the email with the report attached should be sent from. If this attribute 
is missing then no email will be sent. The to_email attribute is used to specify 
which emails to send the report to. If it is missing, but from_email is not then 
reports are made for each author associated with the project rather than one 
report for the whole project. Similarly, cc_email is used to specify which emails 
to cc the report to. email_body is used to specify what should be in the body of 
the email, and email_subject is used to specify what should be in the subject of 
the email.

collaborator_report is used to specify that creating a collaborator report is 
desired and how to construct and email it. If collaborator_report is missing 
then no report is created for the authors of that project. Additional attributes 
within the collaborator_report attribute specify how to construct the report 
and whether to email it.
Details about reporting are in the :doc:`reporting` section. 

The from_email attribute within collaborator_report is used to specify what email 
address the email with the report attached should be sent from. If this attribute 
is missing then no email will be sent. The to_email attribute is used to specify 
which emails to send the report to. If it is missing, but from_email is not then 
the author's email attribute is used instead. Similarly, cc_email is used to 
specify which emails to cc the report to. email_body is used to specify what should 
be in the body of the email, and email_subject is used to specify what should be 
in the subject of the email.

Commands Requiring This Section:

author_search

gen_reports_and_emails_auth


ORCID_search
++++++++++++
This section contains information necessary to use ORCID's API. The ORCID_key and 
ORCID_secret correspond to a key and secret you can get from ORCID after `registering <https://info.orcid.org/documentation/integration-guide/registering-a-public-api-client/>`_
for their public API.

Commands Requiring This Section:

author_search    # Unless the --no_ORCID option is used

find_ORCID


PubMed_search
+++++++++++++
This section simply contains an email address that is necessary to use when using 
PubMed's API. This allows PubMed to inform you if you are using their API in a 
way they don't like, and allows you to change the behavior before they blacklist 
you.

Commands Requiring This Section:

author_search

reference_search


Crossref_search
+++++++++++++++
Similar to PubMed_search this section simply contains an email address to use 
with Crossref's API. It serves a similar function as PubMed's in that they can 
contact you about unwanted behavior and also allows you into a better request 
pool that has faster response times.

Commands Requiring This Section:

author_search        # Unless the --no_Crossref and --no_GoogleScholar options are used

reference_search     # Unless the --no_Crossref option is used


summary_report
++++++++++++++
summary_report is used to specify that creating a summary report is desired and 
how to construct and email it. If summary_report is missing then no report is 
created for that run. Additional attributes within the summary_report attribute 
specify how to construct the report and whether to email it. 
Details about reporting are in the :doc:`reporting` section. 

The from_email attribute within summary_report is used to specify what email 
address the email with the report attached should be sent from. If this attribute 
is missing then no email will be sent. The to_email attribute is used to specify 
which emails to send the report to. Similarly, cc_email is used to specify which emails 
to cc the report to. email_body is used to specify what should be in the body of 
the email, and email_subject is used to specify what should be in the subject of 
the email.


Authors
+++++++
The Authors section is where all of the information about the authors you want 
to search for goes. Every author in this section will be queried during author_search. 

The first_name and last_name attributes are for the author's first and last names 
respectively, and are used to validate that the author under search is the same 
as the queried author.

pubmed_name_search is used as the query string when querying sources. This is so 
the user can specify exactly what to query rather than simply querying the first 
and last name. 

email is used to send individual project reports and collaborator reports to 
authors about their publications if the user chooses to do so.

ORCID is the ORCID ID of the author and is required to search an author's publications 
in ORCID's database. If this is not present then the author will be skipped when 
searching ORCID.

The grants, cutoff_year, affiliations, project_report, and collaborator_report 
attributes from the project_description section can also be included individually 
for an author. They are in the project_description section so it is easier to 
specify these fields en masse, but it can be done on an individual level as well.

Commands Requiring This Section:

author_search

find_ORCID

find_GoogleScholar

add_authors

gen_reports_and_emails_auth



Validating Schema
-----------------
.. code-block:: console

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
                                 "cutoff_year": {"type": "integer"},
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
                                         "first_name": {"type": "string", "minLength":1},
                                         "last_name":{"type": "string", "minLength":1},
                                         "pubmed_name_search": {"type": "string", "minLength":1},
                                         "email":{"type": "string", "format":"email"},
                                         "ORCID":{"type": "string", "pattern":"^\d{4}-\d{4}-\d{4}-\d{3}[0,1,2,3,4,5,6,7,8,9,X]$"},
                                         "grants": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}},
                                         "cutoff_year": {"type": "integer"},
                                         "affiliations": {"type": "array", "minItems":1, "items": {"type": "string", "minLength": 1}},
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
                                 "required" : ["first_name", "last_name", "pubmed_name_search"]
    
                                 }
                           }
                                      
         },
     "required": ["project_descriptions", "ORCID_search", "PubMed_search", "Crossref_search", "Authors"]
    }


Example
-------
.. code-block:: console

     {
       "project_descriptions" : {
           "<project-name>" : {
              "grants" : [ "P42ES007380", "P42 ES007380" ],
              "cutoff_year" : 2019, # optional
              "affiliations" : [ "kentucky" ],
              "project_report" : { # optional 
                      "template": "<formatted_string>", #optional
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
               "template": "<formatted_string>", #optional
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
                       "email": "email@uky.edu", #optional
                       "ORCID": "<orcid>" #optional       
                       "affiliations" : ["<affiliation1>", "<affiliation2>"] #optional    
                    },
        
              "Author 2": {  
                       "first_name" : "<first-name>",
                       "last_name" : "<last-name>",
                       "pubmed_name_search" : "<search-str>",
                       "email": "email@uky.edu", #optional
                       "ORCID": "<orcid>" #optional 
                       "affiliations" : ["<affiliation1>", "<affiliation2>"] #optional
                    },
       }
     }




Publications JSON
~~~~~~~~~~~~~~~~~
The publications JSON is one of the outputs of the program. It is based on the 
default JSON created by the pymed package from the PubMed XML. PubMed is the most 
data rich source that is queried so publications from other sources have their 
information conformed to this. Therefore publications from other sources will 
have mostly empty fields.

The keys for each publication will either be a DOI web address, a PMID, or an 
external URL to the publication. When deciding which type of key to use for a 
publication when querying the preference is DOI, PMID, then URL. So if the DOI 
is unavailable then the PMID is used, and if the DOI and PMID are unavailable the 
URL is used. 


Validating Schema
-----------------
.. code-block:: console

    {
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


Example
-------   
.. code-block:: console

    {
       "<DOI, URL, or PMID>": {
            "abstract": "<publication abstract>",
            "authors": [
               {
                  "affiliation": "<comma separated list of affiliations>",
                  "firstname": "<author first name>",
                  "initials": "<author initials>",
                  "lastname": "<author last name>",
                  "author_id" : "<author-id>"  # optional, only put it if author detected and validated
               },
            ],
            "conclusions": "<publication conclusions>",
            "copyrights": "<copyrights>",
            "doi": "DOI string",
            "journal": "<journal name>",
            "keywords": ["keyword 1", "keyword 2"],
            "methods": "<publication methods>",
            "publication_date": {"year":yyyy, "month":mm, "day":dd},
            "pubmed_id": "<pubmed id>",
            "results": "<publication results>",
            "title": "<publication title>",
            "grants": ["grant1", "grant2"],
            "PMCID": "<PMCID>"
       },
    }


Email JSON
~~~~~~~~~~
The email JSON is an output of the program. It is provided purely as a record 
and is not used as input for any commands. Since it is not an input there is 
no associated JSON schema to validate it. The top level has 2 keys "creation_date" 
and "emails". creation_date is a simple timestamp for when the JSON was created. 
emails is a list of emails broken into thier parts. Each part is a string. 


Example
-------
.. code-block:: console

    {
    "creation_date" : "<date-time-stamp>",
    "emails" : [
                  {  
                   "body" : "<email body>",
                   "cc" : "<comma separated list of email addresses>",
                   "from" : "<from email address>",
                   "subject": "<email subject>",
                   "to": "<author email address>",
                   "author" : "<author name>"        #only present if email is for a specific author from author_search
                  },
    
                  {  
                   "body" : "<email body>",
                   "cc" : "<comma separated list of email addresses>",
                   "from" : "<from email address>",
                   "subject": "<email subject>",
                   "to": "<author email address>",
                   "author" : "<author name>"        #only present if email is for a specific author from author_search
                  },
               ]
    }


Tokenized References JSON
~~~~~~~~~~~~~~~~~~~~~~~~~
The tokenized references JSON is an output of the program when working with references. 
It can also be an input, so a schema is needed for validation. It is simply a list 
of references where each reference is an object with attributes for its tokens 
and other properties. It is largely an output for the purpose of troubleshooting. 
The most important thing to understand about the information in this JSON is that 
the information in it is Academic Tracker's best attempt at parsing and tokenizing 
the references, so some information may be incorrect.

The "authors" property is a list of authors where each author is an object that 
has attributes for thier first, middle, and last names as well as initials. Only 
the last name is required though since common citation styles vary on how to name 
authors.

The "title" property is what was tokenized as the title of the publication in the 
reference line.

The "PMID" property is what was tokenized as the PMID of the publication in the 
reference line. To pull a PMID out Academic Tracker looks for "pmid: <pmid>" in 
the tail end of the reference line. Where case is not sensitive.

The "DOI" property is what was tokenized as the DOI of the publication in the 
reference line. To pull a DOI out Academic Tracker looks for "doi: <doi>" in 
the tail end of the reference line. Where case is not sensitive.

The "reference_line" property is the raw string that was tokenized into the other 
properties.

The "pub_dict_key" property is the key to the matching publication in the publication 
JSON that was found during reference_search queries. This can be empty if there 
was no matching publication found or if the tokenized reference JSON was generated 
on its own.


Validating Schema
-----------------
.. code-block:: console

    {
     "$schema": "https://json-schema.org/draft/2020-12/schema",
     "title": "Tokenized Citations JSON",
     "description": "Input file that contains the tokenized data of a reference file.",
     
     "type": "array",
     "items": {"type": "object",
               "minItems":1,
               "properties": {"authors": {"type": "array",
                                          "items": {"type": "object",
                                                    "properties": {"last": {"type":["string", "null"]},
                                                                   "initials": {"type":["string", "null"]},
                                                                   "first": {"type":["string", "null"]},
                                                                   "middle": {"type":["string", "null"]}},
                                                    "required": ["last"]}},
                              "title": {"type":["string", "null"]},
                              "PMID": {"type":["string", "null"]},
                              "DOI": {"type":["string", "null"]},
                              "reference_line": {"type":["string", "null"]},
                              "pub_dict_key": {"type":["string", "null"]}},
               "required": ["authors", "title", "PMID", "DOI", "reference_line", "pub_dict_key"]}
    }


Example
-------
.. code-block:: console

    [
      {
        "DOI": "10.3390/metabo11030163",
        "PMID": "",
        "authors": [
          {
            "initials": "C",
            "last": "Powell"
          },
          {
            "initials": "H",
            "last": "Moseley"
          }
        ],
        "pub_dict_key": "https://doi.org/10.3390/metabo11030163",
        "reference_line": "Powell C, Moseley H. The mwtab Python Library for RESTful Access and Enhanced Quality Control, Deposition, and Curation of the Metabolomics Workbench Data Repository. Metabolites. 2021 March; 11(3):163-. doi: 10.3390/metabo11030163.",
        "title": "The mwtab Python Library for RESTful Access and Enhanced Quality Control, Deposition, and Curation of the Metabolomics Workbench Data Repository."
      },
      {
        "DOI": "10.3390/metabo10090368",
        "PMID": "",
        "authors": [
          {
            "initials": "H",
            "last": "Jin"
          },
          {
            "initials": "J",
            "last": "Mitchell"
          },
          {
            "initials": "H",
            "last": "Moseley"
          }
        ],
        "pub_dict_key": "https://doi.org/10.3390/metabo10090368",
        "reference_line": "Jin H, Mitchell J, Moseley H. Atom Identifiers Generated by a Neighborhood-Specific Graph Coloring Method Enable Compound Harmonization across Metabolic Databases. Metabolites. 2020 September; 10(9):368-. doi: 10.3390/metabo10090368.",
        "title": "Atom Identifiers Generated by a Neighborhood-Specific Graph Coloring Method Enable Compound Harmonization across Metabolic Databases."
      }
    ]







.. _jsonschema: https://json-schema.org/