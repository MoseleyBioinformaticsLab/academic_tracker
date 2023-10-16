TODO List
=========


.. todolist::



Improve reference search to see if every author on the pub has the pub associated with them on ORCID.

Let the authors_file for add_authors be an excel file.

Add recipes for common use cases such as a trainee project to the documentation.

Add PMCID and grants to pymed package.

Add expanded search to orcid package or look for more up to date package to use. Expanded search was added to ORCID's API with 3.0 release. orcid package appears to be 2.0 only.

Add capability to get the citations each paper cites.

Switch to a merge style from each source, so try to fill in information that wasn't found previously. 
Keep the queries from each source, and do 2 passes with the new merge logic. This makes it so that if 
a publication was on PubMed, but an author couldn't be matched, but an author was matched at another 
source we can merge the information with the second pass. Would need to change the logic to first look 
and see if the publication is in the list already and if it is then we don't need to make an author match 
because an author match was made from another source. The big changes are to keep the queries, do a second 
pass, merge information, and use existence in the list as verification in addition to an author match.
  
Save references out in "citation" format. Look at formats Google Scholar offers, example EndNote.