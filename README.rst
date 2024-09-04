Academic Tracker
================

.. image:: https://img.shields.io/pypi/v/academic_tracker.svg
   :target: https://pypi.org/project/academic_tracker
   :alt: Current library version

.. image:: https://img.shields.io/pypi/pyversions/academic_tracker.svg
   :target: https://pypi.org/project/academic_tracker
   :alt: Supported Python versions

..
    .. image:: https://github.com/MoseleyBioinformaticsLab/academic_tracker/actions/workflows/build.yml/badge.svg
       :target: https://github.com/MoseleyBioinformaticsLab/academic_tracker/actions/workflows/build.yml
       :alt: Build status

.. image:: https://codecov.io/gh/MoseleyBioinformaticsLab/academic_tracker/branch/main/graphs/badge.svg?branch=main
   :target: https://codecov.io/gh/MoseleyBioinformaticsLab/academic_tracker
   :alt: Code coverage information

.. image:: https://img.shields.io/badge/DOI-10.1371%2Fjournal.pone.0277834-blue.svg
   :target: https://doi.org/10.1371/journal.pone.0277834
   :alt: Citation link

.. image:: https://img.shields.io/github/stars/MoseleyBioinformaticsLab/academic_tracker.svg?style=social&label=Star
    :target: https://github.com/MoseleyBioinformaticsLab/academic_tracker
    :alt: GitHub project

|

Academic Tracker was created to automate the process of making sure that federally 
funded publications get listed on PubMed and that the grant funding source for 
them is cited. 

Academic Tracker is a command line tool to search PubMed, ORCID, Google Scholar, 
and Crossref for publications. The program can either be given a list of authors 
to look for publications for, or references/citations to publications themselves. 
The program will then will look for publications on the aforementioned sources 
and return what relevant information is available from those sources.

The primary use case is to give the program a list of authors to find publications 
for. From this list of publications it can then be determined which ones need 
further action to be in compliance.

A secondary use case for finding author's publications is to create a report of 
the collaborators they have worked with, and can be done by specifying the creation 
of that report in the configuration file. Details on reports are in the `documentation <https://moseleybioinformaticslab.github.io/academic_tracker/reporting.html>`__.

The other primary use case is to give the program a list of publication references 
to find information for.

Links
~~~~~

   * Academic Tracker @ GitHub_
   * Academic Tracker @ PyPI_
   * Documentation @ Pages_


Installation
~~~~~~~~~~~~
The Academic Tracker package runs under Python 3.8+. Use pip_ to install.
Starting with Python 3.4, pip_ is included by default. Be sure to use the latest 
version of pip as older versions are known to have issues grabbing all dependencies. 
Academic Tracker relies on sendmail to send emails, so if you need to use that 
feature be sure sendmail is installed and in PATH.


Install on Linux, Mac OS X
--------------------------

.. code:: bash

   python3 -m pip install academic-tracker


Install on Windows
------------------

.. code:: bash

   py -3 -m pip install academic-tracker
   

Upgrade on Linux, Mac OS X
--------------------------

.. code:: bash

   python3 -m pip install academic-tracker --upgrade
   

Upgrade on Windows
------------------

.. code:: bash

   py -3 -m pip install academic-tracker --upgrade



Quickstart
~~~~~~~~~~
Academic Tracker has several commands and options. The simplest most common use 
case is simply:

.. code:: bash
    
    academic_tracker author_search config_file.json
    
Example config files can be downloaded from the `example_configs <https://github.com/MoseleyBioinformaticsLab/academic_tracker>`_ 
directory of the GitHub_.

Academic Tracker's behavior can be quite complex though, so it is highly encouraged 
to read the `guide <https://moseleybioinformaticslab.github.io/academic_tracker/guide.html>`_ 
and `tutorial <https://moseleybioinformaticslab.github.io/academic_tracker/tutorial.html>`_.


Creating The Configuration JSON
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A configuration JSON file is required to run Academic Tracker, but initially creating 
it the first time can be burdensome. Unfortunately, there is no easy solution for 
this. It is encouraged to read the configuration JSON section in `jsonschema <https://moseleybioinformaticslab.github.io/academic_tracker/jsonschema.html>`_ 
and use the example there to create it initially. The add_authors command can help 
with building the Authors section if you already have a csv file with author 
information. A good tool to help track down pesky JSON syntax errors is `here <https://csvjson.com/json_validator>`__. 
There are also examples in the `example_configs <https://github.com/MoseleyBioinformaticsLab/academic_tracker/tree/main/example_configs>`__ 
directory of the GitHub repo. There are also more examples in the supplemental 
material of the paper https://doi.org/10.6084/m9.figshare.19412165.


Registering With ORCID
~~~~~~~~~~~~~~~~~~~~~~
In order to have this program search ORCID you must register with ORCID and obtain 
a key and secret. Details on how to do that are `here <https://info.orcid.org/documentation/integration-guide/registering-a-public-api-client/>`__. 
If you do not want to do that then the --no_ORCID option can be used to skip searching 
ORCID, or don't include the ORCID_search section in the config file.

          
Mac OS Note
~~~~~~~~~~~
When you try to run the program on Mac OS you may get an SSL error.

    certificate verify failed: unable to get local issuer certificate
    
This is due to a change in Mac OS and Python. To fix it go to to your Python 
folder in Applications and run the Install Certificates.command shell command 
in the /Applications/Python 3.x folder. This should fix the issue.


Email Sending Note
~~~~~~~~~~~~~~~~~~
Academic Tracker uses sendmail to send emails, so any system it is going to be 
used on needs to have sendmail installed and the path in PATH. If you try to 
send emails without this the program will display a warning. This can be avoided 
by using the --test option though. The --test option blocks email sending. Email 
sending can also be avoided by leaving the from_email attribute out of the report 
sections of the configuration JSON file.


How Authors Are Identified
~~~~~~~~~~~~~~~~~~~~~~~~~~
When searching by authors it is necessary to confirm that the author given to 
Academic Tracker matches the author returned in the query. In general this matching 
is done by matching the first and last names and at least one affiliation given 
for the author in the configuration JSON file. Note that affiliations can change 
over time as authors move, so they may need many affiliations to accurately match 
them to their publications depending on how far back you want to search in time.


How Publications Are Matched
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When searching by publications it is necessary to confirm that the publication 
in the given reference matches the publication returned in the query. This is done 
by either matching the DOIs, PMIDs, or the title and at least one author. Titles 
are fuzzy matched using fuzzywuzzy which is why at least one author must also be 
matched. Author's are matched using last name and at least one affiliation.


Troubleshooting Errors
~~~~~~~~~~~~~~~~~~~~~~
If you experience errors when running Academic Tracker the first thing to do is 
simply try again. Since Academic Tracker is communicating with multiple web sources 
it is not uncommon for a problem to occur with one of these sources. It might also 
be a good idea to wait several hours or the next day to try again if there is a communication 
issue with a particular source. You can also use the various "--no_Source" options 
for whatever source is causing an error. For example, if Crossref keeps having 504 
HTTP errors you can run with the --no_Crossref option. If the issue persists across 
multiple runs then try upgrading Academic Tracker's dependencies with 
"pip install --upgrade dependency_name". The list of dependencies is in the `guide <https://moseleybioinformaticslab.github.io/academic_tracker/guide.html>`_.


License
~~~~~~~
This package is distributed under the BSD `license <https://moseleybioinformaticslab.github.io/academic_tracker/license.html>`__.


.. _GitHub: https://github.com/MoseleyBioinformaticsLab/academic_tracker
.. _Pages: https://moseleybioinformaticslab.github.io/academic_tracker/
.. _PyPI: https://pypi.org/project/academic_tracker
.. _pip: https://pip.pypa.io