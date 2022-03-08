Tokenization
============

Academic Tracker is aware of MLA, APA, Harvard, Chicago, and Vancouver style citations. 
Each line is determined to be a citation in one of the styles and then parsed into 
author, title, and tail sections based on the style. Academic Tracker then looks 
for a DOI or PMID in the tail section. A DOI must be indicated with "DOI: doi_address" 
and a PMID must be indicated with "PMID: pubmed_id" (PMID: and DOI: are case insensitive). 
These are optional and only help in searching for the publication and verifying 
identity in any search results. 

Although the citation styles Academic Tracker is aware of have standards for 
citations in reality these standards are not strictly adhered to by the public. 
In developing the citation parsing for Academic Tracker a few different sources 
that generate citations supposedly matching one of the styles were used, including 
Google Scholar. These sources often do not match what is indicated by the standards 
for each style. Due to these discrepancies and the somewhat subjective interpretations 
of "standards" Academic Tracker parses citations with a more heuristic approach. 
The point is, do not expect Academic Tracker to be able to flawlessly parse even 
machine generated citations. It is unfortunately the nature of citations not to 
be standard and therefore difficult to parse.


Regular Expressions
~~~~~~~~~~~~~~~~~~~
The specific regular expressions for each style are shown below. The regular expressions 
break 1 line into 3 parts. The left most part is authors, the middle is the title, 
and the end is the tail. The authors part is then further tokenized into individual 
authors, and a DOI and PMID looked for in the tail. The specifics of how the authors 
are tokenized will not be described here, but the code can be found in the citation_parsing.py 
file in the Academic Tracker source code.

.. code-block:: console

     "MLA":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?]+)\s+\"(.*)\"\s+(.*)"
     "APA":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?]+)\s+\(\d\d\d\d\)\.\s+([^\.]+)\.\s+(.*)"
     "Chicago":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?]+)\s+\"(.*)\"\s+(.*)"
     "Harvard":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?]+)\s+\d\d\d\d\.\s+([^\.]+)\.\s+(.*)"
     "Vancouver":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?.]+)\.\s+([^\.]+)\.\s+(.*)"


Special Cases
~~~~~~~~~~~~~
There are 2 special cases where tokenization is not done as described above. 

One case is where the reference is a MyNCBI My Bibliography page. For this case each 
page of the bibliography is visited and the references are tokenized using the 
HTML tags. The specifics can be found in the tokenize_myncbi_citations function in the 
citation_parsing.py file of the source code.

The other case is where the reference is a MEDLINE_ formatted file. For this type 
of file the tags on the left hand side of the file are used to identify the relevant 
tokens. The specifics can be found in the parse_MEDLINE_format function in the 
citation_parsing.py file of the source code.



.. _MEDLINE: https://www.nlm.nih.gov/bsd/mms/medlineelements.html