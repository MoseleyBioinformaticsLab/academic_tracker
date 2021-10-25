Academic Tracker
================
..
    .. image:: https://img.shields.io/pypi/l/mwtab.svg
       :target: https://choosealicense.com/licenses/bsd-3-clause-clear/
       :alt: License information
    
    .. image:: https://img.shields.io/pypi/v/mwtab.svg
       :target: https://pypi.org/project/mwtab
       :alt: Current library version
    
    .. image:: https://img.shields.io/pypi/pyversions/mwtab.svg
       :target: https://pypi.org/project/mwtab
       :alt: Supported Python versions
    
    .. image:: https://readthedocs.org/projects/nmrstarlib/badge/?version=latest
       :target: http://mwtab.readthedocs.io/en/latest/?badge=latest
       :alt: Documentation status
    
    .. image:: https://api.travis-ci.org/MoseleyBioinformaticsLab/mwtab.svg?branch=master
       :target: https://travis-ci.org/MoseleyBioinformaticsLab/mwtab
       :alt: Travis CI status
    
    .. image:: https://codecov.io/gh/MoseleyBioinformaticsLab/mwtab/branch/master/graphs/badge.svg?branch=master
       :target: https://codecov.io/gh/MoseleyBioinformaticsLab/mwtab
       :alt: Code coverage information
    
    .. image:: https://img.shields.io/badge/DOI-10.3390%2Fmetabo11030163-blue.svg
       :target: https://doi.org/10.3390/metabo11030163
       :alt: Citation link
    
    .. image:: https://img.shields.io/github/stars/MoseleyBioinformaticsLab/mwtab.svg?style=social&label=Star
        :target: https://github.com/MoseleyBioinformaticsLab/mwtab
        :alt: GitHub project

|


Academic Tracker was created to automate the process of making sure that NIH 
funded publications get listed on PubMed and that the grant funding source for 
them is cited. 

The Academic Tracker package is a simple program to search PubMed for a given 
list of authors and find their publications. Each publication is checked to see 
if it has a citation for any of the given grants. An email is then sent to each 
author with the given email message and a list of the publications found. 




Links
~~~~~

   * Academic Tracker @ GitHub_
   * Academic Tracker @ PyPI_
   * Documentation @ ReadTheDocs_


Installation
~~~~~~~~~~~~

The Academic Tracker package runs under Python 3.7+. Use pip_ to install.
Starting with Python 3.4, pip_ is included by default. Academic Tracker relies 
on sendmail which is built into Linux to send emails, so it is only available for 
use there.


Install on Linux, Mac OS X
--------------------------

.. code:: bash

   python3 -m pip install academic_tracker




Upgrade on Linux, Mac OS X
--------------------------

.. code:: bash

   python3 -m pip install academic_tracker --upgrade





Quickstart
~~~~~~~~~~

Academic Tracker expects 2 JSON files as input and has several options. The 
simplest most common use case is simply:
.. code:: bash
    
    academic_tracker config_file.json authors.json

There are some things to know about Academic Tracker's default behavior though. 
Academic Tracker will search the current directory for directories with the 
name "tracker-yymmddhhmm", where yymmddhhmm is a timestamp. It will find the latest 
timestamp and look for a "publications.json" file in  the tracker-yymmddhhmm directory. 
If one is not present Academic Tracker will exit with an error. If one is found then 
it will read the file in and use it as a list of publications to ignore in the current 
run since they were found last time. To start fresh simply run Academic Tracker in 
a directory with no tracker directories. The path to the publications.json file can 
be overwritten with the --prev_pub option. 

The default output behavior of Academic Tracker is to create a new directory 
in the current directory named "tracker-yymmddhhmm", where yymmddhhmm is a timestamp. 
Inside this directory is where the "emails.json" and "publications.json" output files will be saved. 
By default if a previous publications.json was given or detected it will be merged 
with the newly found publications, so that each new publications.json file is cummulative 
between runs. If the --test option is used then a "tracker-test-yymmddhhmm" directory 
will be created instead. Note that test directories are ignored when looking for publications.json files.

Options take precedent over what is in the configuration JSON file, so if the --cutoff_year 
option is used for instance, whatever is entered on the command line will be used 
and the value in the configuration file will be ignored.


.. note:: Read the User Guide and the Academic Tracker Tutorial on ReadTheDocs_
          to learn more and to see examples on using Academic Tracker as a command-line tool.
          
          
JSON Schema
~~~~~~~~~~~

Configuration JSON
------------------
The configuration JSON contains information about what grants publications could 
have citations for, what year to go back to when looking for publications, and 
how to format the emails to the authors.
    
    {
     "grants" : [ "grant1", "grant2" ],
     "cutoff_year" : YYYY,
     "affiliations" : [ "affiliation1", "affiliation2" ],
     "from_email" : "email@email.com",
     "cc_email" : ["email1@wmail.com", "email2@email.com"], # optional
     "email_template" : "<formatted-string>",
     "email_subject" : "<formatted-string>"
    }
    
email_template and email_subject have special reserved words that can be used 
which will be replaced by the program before creating the emails.

Special Words:
    
    <total_pubs> (Required, template only) Where in the email_template you want the list of publications placed.
    <author_first_name> (Optional) Will be replaced with author's first name.
    <author_last_name> (Optional) Will be replaced with author's last name.
    
Example JSON:
    
    {
     "grants" : [ "P42ES007380", "P42 ES007380" ],
     "cutoff_year" : 2019,
     "affiliations" : [ "kentucky" ],
     "from_email" : "ptth222@uky.edu",
     "cc_email" : [], 
     "email_template" : "Dear <author_first_name>,

                        The following are the publications I was able to find on PubMed. Please look through the list and determine if any new publications are absent from the list. Also check the list of cited grants under each publication and determine if any citations are missing.
                        
                        <total pubs>
                        
                        Kind Regards,
                        This email was sent by an automated service. For questions or concerns contact Travis Thompson (ptth222@uky.edu).",
     "email_subject" : "Newest PubMed Publications"
    }


Authors JSON
------------
The authors JSON contains information specific to each author, and gives the 
program the best chance of confirming the author listed for the publication is 
indeed the one you looking for. Any of the attributes in the config JSON can 
optionally be added for an author as well, so that settings can be customized 
per author.
    
    {
        "Author 1": {  
                       "first_name" : "<first-name>",
                       "last_name" : "<last-name>",
                       "pubmed_name_search" : "<search-str>",
                       "email": "email@email.com",
                       "ORCID": "<orcid>" # optional           
                    },
        
        "Author 2": {  
                       "first_name" : "<first-name>",
                       "last_name" : "<last-name>",
                       "pubmed_name_search" : "<search-str>",
                       "email": "email@email.com",
                       "ORCID": "<orcid>" # optional 
                    },
    }
    
Example JSON:
    
    {
        "Travis Thompson": {  
                       "first_name" : "Travis",
                       "last_name" : "Thompson",
                       "pubmed_name_search" : "Patrick T Thompson", # optional
                       "email": "ptth222@uky.edu",
                       "ORCID": "0000-0002-8198-1327" # optional           
                    },
        
    }


Publications JSON
-----------------
The publications JSON is one of the outputs of the program and is not intended 
to be created or modified by users. The schema is shown here, but an example entry 
would be overly large.
    
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
                  "author_id": "<author-id>"  # optional, only put in if author detected and validated
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


Email JSON
----------
The email JSON is the other output of the program and is given as a record and 
so that additional programs can use it later if needed. Academic Tracker does 
not use it in later runs.
    
    {
    "creation_date" : "<date-time-stamp>",
    "emails" : [
                   {  
                   "body" : "<email body>",
                   "cc" : "<comma separated list of email addresses>",
                   "from" : "<from email address>",
                   "subject": "<email subject>",
                   "to": "<author email address>",
                   "author" : "<author name>"
                   },
    
               {  
                   "body" : "<email body>",
                   "cc" : "<comma separated list of email addresses>",
                   "from" : "<from email address>",
                   "subject": "<email subject>",
                   "to": "<author email address>",
                   "author" : "<author name>"
                },
                
               ]

    }



How Authors Are Identified
~~~~~~~~~~~~~~~~~~~~~~~~~~

PubMed is queried with the pubmed_name_search. For each publication returned by 
PubMed, Academic Tracker looks for a matching author on the publication by matching 
thier first and last name and at least one affiliation.

License
~~~~~~~

This package is distributed under the BSD_ `license`.


.. _GitHub: https://github.com/MoseleyBioinformaticsLab/academic_tracker
.. _ReadTheDocs: http://academic_tracker.readthedocs.io
.. _PyPI: https://pypi.org/project/academic_tracker
.. _pip: https://pip.pypa.io
.. _BSD: https://choosealicense.com/licenses/bsd-3-clause-clear/