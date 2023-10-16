Change Log
==========

Version 2.0.0
~~~~~~~~~~~~~

Changes
-------
In the 1.0.0 version each source was queried in a certain order and if later sources found the 
same publicaiton as a previous one it was simply ignored. Now a best attempt is made to try and 
merge information from the previous source with information from later sources. An additional 
"queried_sources" attribute was added to the publication object created for each publication to 
indicate all of the sources where the publication was found. It is a list field, and each source 
is appended to it as it is found.

Enhancements
------------
A "references" attribute was added to the publication object for each publication and the references 
for the publication will appear there if available. It is a list of objects that have the attributes 
"citation", "title", "PMID", "PMCID", and "DOI". Fields that can't be determined will have a null value.

More information is able to be obtained from PubMed, such as DOI author affiliations, and author ORCIDs.

Collective authors can now be specified and are handled appropriately when present on information from 
queried sources.

All new publication attributes were added to the reporting and the documentation updated.

The raw queries from each source can now be saved using the --save-all-queries option. An "all_results.json" 
file will be saved in the output if the option is given.

The --keep-duplicates option was added to reference_search. This allows the user to force the search 
not to drop what it deems as duplicates. The default is that they are still dropped automatically, but 
this option allows for an override when the program thinks, incorrectly, that 2 references are the same.

Bug Fixes
--------- 
Crossref publication dates will now have day and month when available. A bug made it so only the year 
was captured even if month and day were available.



