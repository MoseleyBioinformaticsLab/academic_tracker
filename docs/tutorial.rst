Tutorial
========

Typical run:
.. code:: bash
    
    academic_tracker config_file.json authors.json


Run in test mode so emails aren't sent:
.. code:: bash
    
    academic_tracker config_file.json authors.json --test


Designating a previous publications filepath instead of letting Academic Tracker find the most recent:
.. code:: bash
    
    academic_tracker config_file.json authors.json --prev_pub prev_pub_file_path.json


Overwriting the cutoff_year in the config file:
.. code:: bash
    
    academic_tracker config_file.json authors.json --cutoff_year 2018


Overwriting the grants in the config file:
.. code:: bash
    
    academic_tracker config_file.json authors.json --grants grant_1,grant2,grant3









