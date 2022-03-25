User Guide
==========

Description
~~~~~~~~~~~

Academic Tracker was created to automate the process of making sure that federally 
funded publications get listed on PubMed and that the grant funding source for 
them is cited. 

Academic Tracker searches PubMed, ORCID, Crossref, and Google Scholar to look 
for publications. The 2 main use cases allows users to search by author names or 
a publication citation/reference. The output is customizable by the user, but in 
general will be a JSON file of publication information, a JSON file of email 
information if emails were sent, and text files of summary information.

A secondary use case of searching by author names is to create a report of the 
collaborators they have worked with. This can be done by specifying the creation 
of that report in the configuration file. Details on reports are in the `documentation <https://moseleybioinformaticslab.github.io/academic_tracker/reporting.html>`__.


Installation
~~~~~~~~~~~~

The Academic Tracker package runs under Python 3.7+. Use pip_ to install.
Starting with Python 3.4, pip_ is included by default.


Install on Linux, Mac OS X
--------------------------

.. code:: bash

   python3 -m pip install academic_tracker


Install on Windows
------------------

.. code:: bash

   py -3 -m pip install academic_tracker


Upgrade on Linux, Mac OS X
--------------------------

.. code:: bash

   python3 -m pip install academic_tracker --upgrade


Upgrade on Windows
------------------

.. code:: bash

   py -3 -m pip install academic_tracker --upgrade



Install inside virtualenv
-------------------------

For an isolated install, you can run the same inside a virtualenv_.

.. code:: bash

   $ virtualenv -p /usr/bin/python3 venv            # create virtual environment, use python3 interpreter

   $ source venv/bin/activate                       # activate virtual environment

   $ python3 -m pip install academic_tracker        # install academic_tracker as usual

   $ deactivate                                     # if you are done working in the virtual environment

Get the source code
~~~~~~~~~~~~~~~~~~~

Code is available on GitHub: https://github.com/MoseleyBioinformaticsLab/academic_tracker

You can either clone the public repository:

.. code:: bash

   $ https://github.com/MoseleyBioinformaticsLab/academic_tracker.git

Or, download the tarball and/or zipball:

.. code:: bash

   $ curl -OL https://github.com/MoseleyBioinformaticsLab/academic_tracker/tarball/master

   $ curl -OL https://github.com/MoseleyBioinformaticsLab/academic_tracker/zipball/master

Once you have a copy of the source, you can embed it in your own Python package,
or install it into your system site-packages easily:

.. code:: bash

   $ python3 setup.py install

Dependencies
~~~~~~~~~~~~

The Academic Tracker package depends on several Python libraries. The ``pip`` command
will install all dependencies automatically, but if you wish to install them manually,
run the following commands:

   * docopt_ for creating the command-line interface.
      * To install docopt_ run the following:

        .. code:: bash

           python3 -m pip install docopt  # On Linux, Mac OS X
           py -3 -m pip install docopt    # On Windows

   * pymed_ for querying PubMed.
      * To install the pymed_ Python library run the following:

        .. code:: bash

           python3 -m pip install pymed  # On Linux, Mac OS X
           py -3 -m pip install pymed    # On Windows
           
   * jsonschema_ for validating JSON.
      * To install the jsonschema_ Python library run the following:

        .. code:: bash

           python3 -m pip install jsonschema  # On Linux, Mac OS X
           py -3 -m pip install jsonschema    # On Windows
           
   * habanero_ for querying Crossref.
      * To install the habanero_ Python library run the following:

        .. code:: bash

           python3 -m pip install habanero  # On Linux, Mac OS X
           py -3 -m pip install habanero    # On Windows
           
   * orcid_ for quering ORCID.
      * To install the orcid_ Python library run the following:

        .. code:: bash

           python3 -m pip install orcid  # On Linux, Mac OS X
           py -3 -m pip install orcid    # On Windows
           
   * scholarly_ for querying Google Scholar.
      * To install the scholarly_ Python library run the following:

        .. code:: bash

           python3 -m pip install scholarly  # On Linux, Mac OS X
           py -3 -m pip install scholarly    # On Windows
           
   * beautifulsoup4_ for parsing webpages.
      * To install the beautifulsoup4_ Python library run the following:

        .. code:: bash

           python3 -m pip install beautifulsoup4  # On Linux, Mac OS X
           py -3 -m pip install beautifulsoup4    # On Windows
           
   * fuzzywuzzy_ for fuzzy matching publication titles.
      * To install the fuzzywuzzy_ Python library run the following:

        .. code:: bash

           python3 -m pip install fuzzywuzzy  # On Linux, Mac OS X
           py -3 -m pip install fuzzywuzzy    # On Windows
           
   * python-docx_ for reading docx files.
      * To install the python-docx_ Python library run the following:

        .. code:: bash

           python3 -m pip install python-docx  # On Linux, Mac OS X
           py -3 -m pip install python-docx    # On Windows
           
   * pandas_ for easy data manipulation.
      * To install the pandas_ Python library run the following:

        .. code:: bash

           python3 -m pip install pandas  # On Linux, Mac OS X
           py -3 -m pip install pandas    # On Windows
           
   * openpyxl_ for saving Excel files in pandas.
      * To install the openpyxl_ Python library run the following:

        .. code:: bash

           python3 -m pip install openpyxl  # On Linux, Mac OS X
           py -3 -m pip install openpyxl    # On Windows
           
   * requests_ for making internet requests.
      * To install the requests_ Python library run the following:

        .. code:: bash

           python3 -m pip install requests  # On Linux, Mac OS X
           py -3 -m pip install requests    # On Windows
           
   * deepdiff_ for comparing publication data.
      * To install the deepdiff_ Python library run the following:

        .. code:: bash

           python3 -m pip install deepdiff  # On Linux, Mac OS X
           py -3 -m pip install deepdiff    # On Windows
           

Basic usage
~~~~~~~~~~~

Academic Tracker expects at least a configuration JSON file, and possibly more 
depending on the usage. The 2 main use cases are author_search and reference_search,
with the other usages mostly included to support those. author_search searches 
by the authors given in the configuration JSON file while reference_search searches
by the publication references given in the reference file or URL. Details about 
the JSON files are in the :doc:`jsonschema` section, and more information about 
the use cases with examples are in the :doc:`tutorial` section.

.. code-block:: console

    Usage:
        academic_tracker author_search <config_json_file> [--test --prev_pub=<file-path> --no_GoogleScholar --no_ORCID --no_Crossref --verbose --silent]
        academic_tracker reference_search <config_json_file> <references_file_or_URL> [--test --prev_pub=<file-path> --PMID_reference --MEDLINE_reference --no_Crossref --verbose --silent]
        academic_tracker find_ORCID <config_json_file> [--verbose --silent]
        academic_tracker find_Google_Scholar <config_json_file> [--verbose --silent]
        academic_tracker add_authors <config_json_file> <authors_file> [--verbose --silent]
        academic_tracker tokenize_reference <references_file_or_URL> [--MEDLINE_reference --verbose --silent]
        academic_tracker gen_reports_and_emails_auth <config_json_file> <publication_json_file> [--test --verbose --silent]
        academic_tracker gen_reports_and_emails_ref <config_json_file> <references_file_or_URL> <publication_json_file> [--test --prev_pub=<file-path> --MEDLINE_reference --verbose --silent]
        
    Options:
        -h --help                         Show this screen.
        --version                         Show version.
        --verbose                         Print hidden error messages.
        --silent                          Do not print anything to the screen.
        --test                            Generate pubs and email texts, but do not send emails.
        --prev_pub=<file-path>            Filepath to json or csv with publication ids to ignore. Enter "ignore" for the <file_path> to not look for previous publications.json files in tracker directories.
        
    Reference Type Options:    
        --PMID_reference                  Indicates that the reference_file is a PMID file and only PubMed info will be returned.
        --MEDLINE_reference               Indicates that the reference_file is a MEDLINE file.
    
    Search Options:
        --no_GoogleScholar                Don't search Google Scholar.
        --no_ORCID                        Don't search ORCID.
        --no_Crossref                     Don't search Crossref.




.. _pip: https://pip.pypa.io/
.. _virtualenv: https://virtualenv.pypa.io/
.. _docopt: https://pypi.org/project/docopt/
.. _pymed: https://pypi.org/project/pymed/
.. _jsonschema: https://pypi.org/project/jsonschema/
.. _habanero: https://pypi.org/project/habanero/
.. _orcid: https://pypi.org/project/orcid/
.. _scholarly: https://pypi.org/project/scholarly/
.. _beautifulsoup4: https://pypi.org/project/beautifulsoup4/
.. _fuzzywuzzy: https://pypi.org/project/fuzzywuzzy/
.. _python-docx: https://pypi.org/project/python-docx/
.. _pandas: https://pypi.org/project/pandas/
.. _openpyxl: https://pypi.org/project/openpyxl/
.. _requests: https://pypi.org/project/requests/
.. _deepdiff: https://pypi.org/project/deepdiff/