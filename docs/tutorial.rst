Tutorial
========
Academic Tracker is intended to be used solely as a command line program. This 
tutorial describes each command and its options.

Configuration JSON File
~~~~~~~~~~~~~~~~~~~~~~~
Details about the configuration JSON file can be found in the :doc:`jsonschema` 
section, but in general the sections of the configuration JSON file that aren't 
needed for a particular command are not required. For instance, the ORCID_search 
section is not required for reference_search since it does not search ORCID. The 
same is true if the --no_ORCID option is used.

Outputs
~~~~~~~
The specific files output by Academic Tracker vary by the command used and some 
options, but each command always creates a new timestamped directory in the working 
directory. If the --test option is not used then the directory will be named 
tracker-YYMMDDHHMM. If the --test option is used then the directory will be named 
tracker-test-YYMMDDHHMM.



Search For Publications By Author
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Command Line Signature
----------------------
.. code-block:: console

    academic_tracker author_search <config_json_file> [--test --prev_pub=<file-path> --no_GoogleScholar --no_ORCID --no_Crossref --verbose --silent]


Description
-----------
For each author in the Authors section of the configuration JSON file search 
PubMed, ORCID, Crossref, and Google Scholar for publications they are an author 
on. The cutoff_year attribute for either the projects or the authors can be used 
to filter the publications to only those in that year or after. 

Similarly, a previous publications JSON file can be used to filter out publications 
that are already in the file. This file can be specified manually with the --prev_pub 
option. If not specified manually author_search will automatically look for a 
publications.json file in the most recent tracker directories and if it finds 
one it will be used as the previous publications. To stop this automatic lookup 
enter "ignore" for the --prev_pub option. The output publications.json file will 
be a combination of the previous publications and any new publications found. To 
be clear the new publications.json file will be the previous publications.json 
file with any new entries added in. 

The description of everything author_search does with the previous publications 
may seem arbitrary and confusing. The idea is that users will make an initial 
list of authors to keep track of and then run author_search every so often to 
look for new publications for them. To make this as easy as possible it is 
neceessary to both have author_search look for previous publications automatically 
and for the output to be cumulative so that the same publications are not reported 
multiple times.

Although the configuration JSON file contains projects, they are mostly there for 
organizational convenience and reporting. author_search queries every author in 
the Authors section of the configuration JSON, but the information in the projects 
section can affect the search. One of the first things author_search does is that 
it goes through each author and reconciles the information given for them with 
that given for any projects they are associated with. Specifically, the minimum 
cutoff_year is found, and affiliations and grants are concatenated. These reconciled 
values are then what is used when querying.


Options
-------
--test: 

The test option changes the name of the output directory from tracker-YYMMDDHHMM 
to tracker-test-YYMMDDHHMM and prevents any emails from being sent.

--prev_pub: 

Specifies a publications.json file to use as a list of publications to ignore 
when searching for new publications. Set to "ignore" to prevent author_search 
from automatically looking for a publications.json file in tracker directories. 
If a publication is in prev_pub but the information has updated then it will not 
be ignored.
            
--no_GoogleScholar: 

If used author_search will not search Google Scholar for publications.

--no_ORCID: 

If used author_search will not search ORCID for publications. This option is assumed 
if the ORCID_search section of the configuration JSON file is missing.

--no_Crossref: 

If used author_search will not search Crossref for publications. This option is 
assumed if the Crossref_search section of the configuration JSON file is missing.

--verbose: 

If used HTML errors and other warnings will be printed to the screen.

--silent:

If used nothing will be printed to the screen.


Outputs
-------
Outputs depend on the configuration JSON file and options. 

A publications.json file will always be output. 

An emails.json file is only created if the from_email attribute is given in either 
the summary_report or project_report sections of the configuration JSON file. 

A summary_report.txt file is only created if the summary_report attribute is in 
the configuration JSON file. 

Similarly, project_report.txt files are created for projects that have the 
project_report attribute. Project reports will either be for the whole project 
or individual authors and the name of the project report file will indicate this. 
If from_email is given in project_report then a report for the whole project is 
created. If the authors attribute is given in the project and from_email is not 
then a file for each author in the project is created. If neither authors nor 
from_email is given then a file is created for every author that had new publications. 

Details about reports can be found in the :doc:`reporting` section.

publications.json
emails.json
summary_report.txt
projectname_project_report.txt
projectname_authorname_project_report.txt


Examples
--------
Typical run.

config_file.json:

.. code-block:: console

    {
      "project_descriptions": {
        "Project 1": {
          "affiliations": [
            "affiliaton1"
          ],
          "authors": [
            "Author1",
            "Author2"
          ],
          "cutoff_year": 2020,
          "grants": [
            "grant1",
            "grant2"
          ]
        }
      },
      "summary_report": {},
      "ORCID_search": {
        "ORCID_key": "orcid key",
        "ORCID_secret": "orcid secret"
      },
      "PubMed_search": {
        "PubMed_email": "email@email.com"
      },
      "Crossref_search": {
        "mailto_email": "email@email.com"
      },
      "Authors": {
        "Author1": {
          "ORCID": "Author1's ORCID ID",
          "email": "email@email.com",
          "first_name": "First",
          "last_name": "Last",
          "pubmed_name_search": "First Last"
        },
        "Author2": {
          "ORCID": "Author2's ORCID ID",
          "email": "email@email.com",
          "first_name": "Second",
          "last_name": "Last",
          "pubmed_name_search": "Second Last"
        }
      }
    }

Console:

.. code-block:: console
    
    >academic_tracker author_search config_file.json
    Finding author's publications. This could take a while.
    Searching PubMed.
    Searching ORCID.
    Searching Google Scholar.
    Searching Crossref.
    Success. Publications and reports saved in tracker-2202020140


Create a collaborator report for an author.

config_file.json:

.. code-block:: console

    {
      "project_descriptions": {
        "Project 1": {
          "affiliations": [
            "affiliaton1"
          ],
          "authors": [
            "Author1",
            "Author2"
          ],
          "cutoff_year": 2020,
          "grants": [
            "grant1",
            "grant2"
          ]
        }
      },
      "ORCID_search": {
        "ORCID_key": "orcid key",
        "ORCID_secret": "orcid secret"
      },
      "PubMed_search": {
        "PubMed_email": "email@email.com"
      },
      "Crossref_search": {
        "mailto_email": "email@email.com"
      },
      "Authors": {
        "Author1": {
          "ORCID": "Author1's ORCID ID",
          "email": "email@email.com",
          "first_name": "First",
          "last_name": "Last",
          "pubmed_name_search": "First Last"
          "collaborator_report": {}
        },
        "Author2": {
          "ORCID": "Author2's ORCID ID",
          "email": "email@email.com",
          "first_name": "Second",
          "last_name": "Last",
          "pubmed_name_search": "Second Last"
        }
      }
    }

Console:

.. code-block:: console
    
    >academic_tracker author_search config_file.json
    Finding author's publications. This could take a while.
    Searching PubMed.
    Searching ORCID.
    Searching Google Scholar.
    Searching Crossref.
    Success. Publications and reports saved in tracker-2202020140


Run in test mode so emails aren't sent.

.. code-block:: console
    
    >academic_tracker author_search config_file.json --test
    Finding author's publications. This could take a while.
    Searching PubMed.
    Searching ORCID.
    Searching Google Scholar.
    Searching Crossref.
    Success. Publications and reports saved in tracker-test-2202020140


Designating a previous publications filepath instead of letting Academic Tracker find the most recent.

.. code-block:: console
    
    >academic_tracker author_search config_file.json --prev_pub prev_pub_file_path.json
    Finding author's publications. This could take a while.
    Searching PubMed.
    Searching ORCID.
    Searching Google Scholar.
    Searching Crossref.
    Success. Publications and reports saved in tracker-2202020140
    
    
Specifying that Academic Tracker shouldn't use ORCID.

config_file.json:

.. code-block:: console

    {
      "project_descriptions": {
        "Project 1": {
          "affiliations": [
            "affiliaton1"
          ],
          "authors": [
            "Author1",
            "Author2"
          ],
          "cutoff_year": 2020,
          "grants": [
            "grant1",
            "grant2"
          ]
        }
      },
      "summary_report": {},
      "PubMed_search": {
        "PubMed_email": "email@email.com"
      },
      "Crossref_search": {
        "mailto_email": "email@email.com"
      },
      "Authors": {
        "Author1": {
          "email": "email@email.com",
          "first_name": "First",
          "last_name": "Last",
          "pubmed_name_search": "First Last"
        },
        "Author2": {
          "email": "email@email.com",
          "first_name": "Second",
          "last_name": "Last",
          "pubmed_name_search": "Second Last"
        }
      }
    }
    
.. note::

    A minimal example is shown, but the config can have other sections and run without error.

Console:

.. code-block:: console
    
    >academic_tracker author_search config_file.json --no_ORCID
    Finding author's publications. This could take a while.
    Searching PubMed.
    Searching Google Scholar.
    Searching Crossref.
    Success. Publications and reports saved in tracker-2202020140




Search For Publications By Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Command Line Signature
----------------------
.. code-block:: console

    academic_tracker reference_search <config_json_file> <references_file_or_URL> [--test --prev_pub=<file-path> --PMID_reference --MEDLINE_reference --no_Crossref --verbose --silent]


Description
-----------
Parse and tokenize the reference file or URL and then search PubMed and Crossref 
for the publications found. ORCID is not searched because it is a database of 
authors and does not support searching for publications directly. Google Scholar 
is not searched because it does not like bots, so cannot be easily searched without 
using a 3rd party paid service or proxies.

The reference_file_or_URL can be several different things. If it is a file then 
it can be a JSON file of already tokenized data, a docx file, or a txt file. If 
not a JSON file then each reference is expected to be on a single line. If it is 
a URL then it can be either a MyNCBI URL or not. If it is a MyNCBI URL then it 
is expected to be the first page of a bibliography and will be tokenized in a 
specific way. All other URLs are simply read as a text file and tokenized like 
one.

The --PMID_reference and --MEDLINE_reference options change how the reference file 
is interpreted. If the --PMID_reference option is used then it indicates that the 
given reference file is a list of PMIDs (PubMed's unique IDs). Instead of tokenizing 
this file it is assumed that each line is a PMID so PubMed will be queried for 
each PMID and Crossref will not be queried. The idea for this option was to be 
able to quickly grab information from PubMed. 

The --MEDLINE_reference option indicates that given reference file is a MEDLINE_ 
formatted file. This will be tokenized in a unique way since the publication 
information is spread out over multiple lines in this format. This format is 
supported because it is a dounload option on MyNCBI bibliography pages.

Details about tokenization are in the :doc:`tokenization` section.

The --prev_pub option is different for reference_search than it is for author_search. 
First, reference_search does not automatically look for a publicaitons.json file 
to use since the same assumptions as described for author_search do not hold here. 
Second, publications in the prev_pub file are not used to ignore publications. 
Publications in the prev_pub file will still be in the newly created publications.json 
file. What this option does do is set the <is_in_comparison_file> keyword to True 
for matching publications in the summary report.


Options
-------
--test: 

The test option changes the name of the output directory from tracker-YYMMDDHHMM 
to tracker-test-YYMMDDHHMM and prevents any emails from being sent.

--prev_pub: 

Specifies a publications.json file to use as a list of publications to compare 
with when generating the summary report.
            
--PMID_reference: 

Specifies that the reference file is a list of PMIDs and to only return 
information from PubMed.
                  
--MEDLINE_reference: 

Specifies that the reference file is a MEDLINE_ formatted file.
            
--no_Crossref: 

If used reference_search will not search Crossref for publications. This option 
is assumed if the Crossref_search section of the configuration JSON file is missing.

--verbose: 

If used HTML errors and other warnings will be printed to the screen.

--silent:

If used nothing will be printed to the screen.


Outputs
-------
Outputs depend on the configuration JSON file and options. 

A publications.json file will always be output. 

A tokenized_reference.json file will always be output.

An emails.json file is only created if the from_email attribute is given in 
the summary_report section of the configuration JSON file. 

A summary_report.txt file is only created if the summary_report attribute is in 
the configuration JSON file. 

If --PMID_reference is used no reports or emails are generated.

Details about reports can be found in the :doc:`reporting` section.

publications.json
tokenized_reference.json
emails.json
summary_report.txt


Examples
--------
Typical run.

config_file.json:

.. code-block:: console

    {
      "summary_report": {},
      "PubMed_search": {
        "PubMed_email": "email@email.com"
      },
      "Crossref_search": {
        "mailto_email": "email@email.com"
      }
    }
    
.. note::

    A minimal example is shown, but the config can have other sections and run without error.

Console:

.. code-block:: console
    
    >academic_tracker reference_search config_file.json reference_file.txt
    Finding publications. This could take a while.
    Searching PubMed.
    Searching Crossref.
    Success. Publications and reports saved in tracker-2202020140


Run in test mode so emails aren't sent.

.. code-block:: console
    
    >academic_tracker reference_search config_file.json reference_file.txt --test
    Finding publications. This could take a while.
    Searching PubMed.
    Searching Crossref.
    Success. Publications and reports saved in tracker-test-2202020140


Designating a previous publications filepath.

.. code-block:: console
    
    >academic_tracker reference_search config_file.json reference_file.txt --prev_pub prev_pub_file_path.json
    Finding publications. This could take a while. 
    Searching PubMed.
    Searching Crossref.
    Success. Publications and reports saved in tracker-2202020140
    
    
Specifying that Academic Tracker shouldn't use Crossref.

config_file.json:

.. code-block:: console

    {
      "summary_report": {},
      "PubMed_search": {
        "PubMed_email": "email@email.com"
      }
    }
    
.. note::

    A minimal example is shown, but the config can have other sections and run without error.

Console:

.. code-block:: console
    
    >academic_tracker reference_search config_file.json reference_file.txt --no_Crossref
    Finding publications. This could take a while. 
    Searching PubMed.
    Success. Publications and reports saved in tracker-2202020140




Find ORCID IDs for Authors
~~~~~~~~~~~~~~~~~~~~~~~~~~
Command Line Signature
----------------------
.. code-block:: console

    academic_tracker find_ORCID <config_json_file> [--verbose --silent]


Description
-----------
For each author in the Authors section of the configuration JSON file with a 
missing or blank ORCID attribute search ORCID for a match to get an ID. Matching 
is done using first and last names and the affiliations attribute.


Options
-------
--verbose: 

If used HTML errors and other warnings will be printed to the screen.

--silent:

If used nothing will be printed to the screen.


Outputs
-------
If any authors are found then a new configuration.json file is created with the 
ORCID information updated in the Authors. If no authors are matched then there 
are no outputs.

configuration.json


Examples
--------

Typical run.

config_file.json:

.. code-block:: console

    {
      "ORCID_search": {
        "ORCID_key": "orcid key",
        "ORCID_secret": "orcid secret"
      },
      "Authors": {
        "Author1": {
          "email": "email@email.com",
          "first_name": "First",
          "last_name": "Last",
          "pubmed_name_search": "First Last"
        },
        "Author2": {
          "email": "email@email.com",
          "first_name": "Second",
          "last_name": "Last",
          "pubmed_name_search": "Second Last"
        }
      }
    }
    
.. note::

    A minimal example is shown, but the config can have other sections and run without error.

Console:

.. code-block:: console
    
    >academic_tracker find_ORCID config_file.json
    Searching ORCID for author's ORCID ids.
    Success! configuration.json saved in tracker-2202020140
    
    
No authors found.

.. code-block:: console
    
    >academic_tracker find_ORCID config_file.json
    Searching ORCID for author's ORCID ids.
    No authors were matched from the ORCID results. No new file saved.




Find Scholar IDs for Authors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Command Line Signature
----------------------
.. code-block:: console

    academic_tracker find_Google_Scholar <config_json_file> [--verbose --silent]


Description
-----------
For each author in the Authors section of the configuration JSON file with a 
missing or blank scholar_id attribute search Google Scholar for a match to get 
an ID. Matching is done using first and last names and the affiliations attribute.


Options
-------
--verbose: 

If used HTML errors and other warnings will be printed to the screen.

--silent:

If used nothing will be printed to the screen.


Outputs
-------
If any authors are found then a new configuration.json file is created with the 
scholar_id information updated in the Authors. If no authors are matched then there 
are no outputs.

configuration.json


Examples
--------
Typical run.

config_file.json:

.. code-block:: console

    {
      "Authors": {
        "Author1": {
          "ORCID": "Author1's ORCID ID",
          "email": "email@email.com",
          "first_name": "First",
          "last_name": "Last",
          "pubmed_name_search": "First Last"
        },
        "Author2": {
          "ORCID": "Author2's ORCID ID",
          "email": "email@email.com",
          "first_name": "Second",
          "last_name": "Last",
          "pubmed_name_search": "Second Last"
        }
      }
    }
    
.. note::

    A minimal example is shown, but the config can have other sections and run without error.

Console:

.. code-block:: console
    
    >academic_tracker find_Google_Scholar config_file.json
    Searching Google Scholar for author's scholar ids.
    Success! configuration.json saved in tracker-2202020140
    
    
No authors found.

.. code-block:: console
    
    >academic_tracker find_Google_Scholar config_file.json
    Searching Google Scholar for author's scholar ids.
    No authors were matched from the Google Scholar results. No new file saved.
    



Add Or Update Authors In Configuration JSON
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Command Line Signature
----------------------
.. code-block:: console

    academic_tracker add_authors <config_json_file> <authors_file> [--verbose --silent]


Description
-----------
Read in the authors_file and update the Authors section of the configuration JSON 
file with the information in it. 

The authors_file must be a csv file. The columns are the attributes for each author 
and each row is one author. Including columns for each required author attribute 
there must also be a column named "author_id" which contains the key for the author. 
In all the required columns are "author_id", "first_name", "last_name", "pubmed_name_search", 
and "email". 

Example csv:
.. code-block:: console

    author_id      first_name   last_name    pubmed_name_search    email             ORCID
    Name McName    Name         McName       Name McName           email@email.com   0000-00001-1234-1234


Options
-------
--verbose: 

If used HTML errors and other warnings will be printed to the screen.

--silent:

If used nothing will be printed to the screen.


Outputs
-------
configuration.json


Examples
--------
Typical run.

config_file.json:

.. code-block:: console

    {
      "Authors": {
        "Author1": {
          "ORCID": "Author1's ORCID ID",
          "email": "email@email.com",
          "first_name": "First",
          "last_name": "Last",
          "pubmed_name_search": "First Last"
        },
        "Author2": {
          "ORCID": "Author2's ORCID ID",
          "email": "email@email.com",
          "first_name": "Second",
          "last_name": "Last",
          "pubmed_name_search": "Second Last"
        }
      }
    }
    
.. note::

    A minimal example is shown, but the config can have other sections and run without error.

Console:

.. code-block:: console
    
    >academic_tracker add_authors config_file.json
    Success! configuration.json saved in tracker-2202020140
    



Tokenize A Reference
~~~~~~~~~~~~~~~~~~~~
Command Line Signature
----------------------
.. code-block:: console

    academic_tracker tokenize_reference <references_file_or_URL> [--MEDLINE_reference --verbose --silent]


Description
-----------
Tokenize the input reference and output a tokenization report and JSON file.


Options
-------
--MEDLINE_reference: 

Specifies that the reference file is a MEDLINE_ formatted file.

--verbose: 

If used HTML errors and other warnings will be printed to the screen.

--silent:

If used nothing will be printed to the screen.


Outputs
-------
The information in the text report and JSON file are essentially the same, but 
the text report is presented in a more human readable way. They both have every 
publication that could be identified in the reference and tokenized, so if one 
does not appear that should be then there is a problem during tokenization. More 
detailed information about tokenization is in the :doc:`tokenization` section.

tokenization_report.txt
tokenized_reference.json


Examples
--------
Typical run.

.. code-block:: console
    
    >academic_tracker tokenize_reference reference_file.txt
    Searching Google Scholar for author's scholar ids.
    Success! Tokenization files saved in tracker-2202020140
    



Generate Reports And Emails Like Author Search
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Command Line Signature
----------------------
.. code-block:: console

    academic_tracker gen_reports_and_emails_auth <config_json_file> <publication_json_file> [--test --verbose --silent]


Description
-----------
Create reports and emails and send emails just like author_search would if it 
had found the publications in the given publications JSON file. The idea behind 
this command is to give the user the ability to play with the reporting system 
without having to query for publications. This command will also send emails if 
the --test option is not used, so don't forget to use it lest you send a bunch 
of test emails to the wrong people, or make sure the emails are all going to you. 

Details about reporting can be found in the :doc:`reporting` section.


Options
-------
--test: 

The test option changes the name of the output directory from tracker-YYMMDDHHMM 
to tracker-test-YYMMDDHHMM and prevents any emails from being sent.
        
--verbose: 

If used HTML errors and other warnings will be printed to the screen.

--silent:

If used nothing will be printed to the screen.


Outputs
-------
Outputs depend on the configuration JSON file and options. 

An emails.json file is only created if the from_email attribute is given in either 
the summary_report or project_report sections of the configuration JSON file. 

A summary_report.txt file is only created if the summary_report attribute is in 
the configuration JSON file. 

Similarly, project_report.txt files are created for projects that have the 
project_report attribute. Project reports will either be for the whole project 
or individual authors and the name of the project report file will indicate this. 
If from_email is given in project_report then a report for the whole project is 
created. If the authors attribute is given in the project and from_email is not 
then a file for each author in the project is created. If neither authors nor 
from_email is given then a file is created for every author that had new publications. 

Details about reports can be found in the :doc:`reporting` section.

emails.json
summary_report.txt
projectname_project_report.txt
projectname_authorname_project_report.txt


Examples
--------
Typical run.

config_file.json:

.. code-block:: console

    {
      "project_descriptions": {
        "Project 1": {
          "affiliations": [
            "affiliaton1"
          ],
          "project_report": {},
          "authors": [
            "Author1",
            "Author2"
          ],
          "cutoff_year": 2020,
          "grants": [
            "grant1",
            "grant2"
          ]
        }
      },
      "summary_report": {},
      "Authors": {
        "Author1": {
          "ORCID": "Author1's ORCID ID",
          "email": "email@email.com",
          "first_name": "First",
          "last_name": "Last",
          "pubmed_name_search": "First Last"
        },
        "Author2": {
          "ORCID": "Author2's ORCID ID",
          "email": "email@email.com",
          "first_name": "Second",
          "last_name": "Last",
          "pubmed_name_search": "Second Last"
        }
      }
    }

.. note::

    A minimal example is shown, but the config can have other sections and run without error.
    
Console:

.. code-block:: console
    
    >academic_tracker gen_reports_and_emails_auth config_file.json publications.json
    Success! Reports and emails saved in tracker-2202020140
    
    


Generate Reports And Emails Like Reference Search
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Command Line Signature
----------------------
.. code-block:: console

    academic_tracker gen_reports_and_emails_ref <config_json_file> <references_file_or_URL> <publication_json_file> [--test --prev_pub=<file-path> --MEDLINE_reference --verbose --silent]


Description
-----------
Create reports and emails and send emails just like reference_search would if it 
had found the publications in the given publications JSON file. The idea behind 
this command is to give the user the ability to play with the reporting system 
without having to query for publications. This command will also send emails if 
the --test option is not used, so don't forget to use it lest you send a bunch 
of test emails to the wrong people, or make sure the emails are all going to you. 

This command differs a little from the author_search version due to the nature 
of reference_search. Each reference must be linked to a publication in the 
given publications JSON file. During reference_search this is done and the 
matching publication key is stored in the pub_dict_key attribute of the tokenized 
reference file. If the tokenized reference is generated on the fly or was not 
generated in tandem with the given publications JSON file then this will not be 
the case. To resolve this the gen_reports_and_emails_ref command does its best 
to match each tokenized reference with the publications in the given publications 
JSON file by comparing DOI, PMID, and title. 

The point is that if the given reference and publications were not generated in 
tandem then results may be different from expectations. A new tokenized_reference.json 
file is output with this command so the user can see which publications were matched 
with each reference by looking at the pub_dict_key attribute.

Details about reporting can be found in the :doc:`reporting` section.


Options
-------
--test: 

The test option changes the name of the output directory from tracker-YYMMDDHHMM 
to tracker-test-YYMMDDHHMM and prevents any emails from being sent.
        
--prev_pub: 

Specifies a publications.json file to use as a list of publications to compare 
with when generating the summary report.
            
--MEDLINE_reference: 

Specifies that the reference file is a MEDLINE_ formatted file.
        
--verbose: 

If used HTML errors and other warnings will be printed to the screen.

--silent:

If used nothing will be printed to the screen.


Outputs
-------
Outputs depend on the configuration JSON file and options. 

A tokenized_reference.json is always generated.

An emails.json file is only created if the from_email attribute is given in either 
the summary_report or project_report sections of the configuration JSON file. 

A summary_report.txt file is only created if the summary_report attribute is in 
the configuration JSON file. 

Details about reports can be found in the :doc:`reporting` section.

tokenized_reference.json
emails.json
summary_report.txt


Examples
--------
Typical run.

config_file.json:

.. code-block:: console

    {
      "summary_report": {},
    }
    
.. note::

    A minimal example is shown, but the config can have other sections and run without error.

Console:

.. code-block:: console
    
    >academic_tracker gen_reports_and_emails_ref config_file.json reference_file.txt publications.json
    Success! Reports and emails saved in tracker-2202020140    
    
    
    




.. _MEDLINE: https://www.nlm.nih.gov/bsd/mms/medlineelements.html