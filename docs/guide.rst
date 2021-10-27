User Guide
==========

Description
~~~~~~~~~~~

Academic Tracker was created to automate the process of making sure that NIH 
funded publications get listed on PubMed and that the grant funding source for 
them is cited. 

The Academic Tracker package is a simple program to search PubMed for a given 
list of authors and find their publications. Each publication is checked to see 
if it has a citation for any of the given grants. An email is then sent to each 
author with the given email message and a list of the publications founds.

Installation
~~~~~~~~~~~~

The Academic Tracker package runs under Python 3.7+. Use pip_ to install.
Starting with Python 3.4, pip_ is included by default.


Install on Linux, Mac OS X
--------------------------

.. code:: bash

   python3 -m pip install academic_tracker




Upgrade on Linux, Mac OS X
--------------------------

.. code:: bash

   python3 -m pip install academic_tracker --upgrade




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


Basic usage
~~~~~~~~~~~

Academic Tracker expects a configuration JSON file and an authors JSON file. 
The configuration file contains information about the grants to look for, the 
email template to use, etc. The authors file contains information about each 
author. The details of the JSON files are in the README.

academic_tracker <config_json_file> <authors_json_file> [options]
    
Options:
    -h --help                       Show this screen.
    --version                       Show version.
    --test                          Generate pubs and email texts, but do not send emails.
    --grants=<nums>...              Grant numbers to filter publications by.
    --cutoff_year=<num>             YYYY year before which to ignore publications.
    --email=<email>                 Send authors email from provided email address.
    --prev_pub=<file-path>          Filepath to json or csv with publication ids to ignore.
    --affiliation=<affiliation>...  An affiliation to filter publications by.



.. note:: Read :doc:`tutorial` to learn more and see examples on using Academic Tracker.


.. _pip: https://pip.pypa.io/
.. _virtualenv: https://virtualenv.pypa.io/
.. _docopt: https://pypi.org/project/docopt/
.. _schema: https://pypi.org/project/schema/
.. _pymed: https://pypi.org/project/pymed/
.. _jsonschema: https://pypi.org/project/jsonschema/