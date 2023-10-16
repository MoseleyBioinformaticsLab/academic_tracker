Reporting
=========

To allow users some flexibility in report creation a unique system for specifying 
how to build reports was created. This system is described here. The key framework 
to keep in mind is that there are 3 different reports and 2 ways to build each one. 
The specifications also slightly differ between each other and between author_search 
and reference_search. The 3 reports are summary_report, project_report, and collaborator_report. 
Each report can be specified using a formatted text string or using a dictionary 
to specify rows and columns.

To specify a report using a formatted string include the "template" attribute for 
the report. To specify a report using rows and columns include the "columns" 
attribute for the report. "columns" should be a dictionary where the keys are 
column names and values are what should be in each row of the column. Typically, 
the values will be keywords. 

If specifying the report with the "columns" attribute there are other attributes 
that can be used in conjuction. "file_format" allows you to specify whether the 
report should be a CSV or Excel file. The 2 allowed values are "csv" and "xlsx". 
"sort" allows you to specify how to sort the table. It should be a list of column 
names. Similarly, "column_order" allows you to specify the order of the columns 
of the table. The order of the columns should be the same as the order given in 
"columns", but just in case "column_order" is provided to manually set the order. 
"separator" allows you to specify the separator character for CSV files. It must 
be one character in length and defaults to a comma. 

"filename" allows you to specify the filename of the report regardless of whether 
"columns" or "template" are used to specify the report, but if the "file_format" 
is "xlsx" and the filename extension is not xlsx then ".xlsx" will be added to 
the filename.

To email a report as an attachment simply include the email related attributes 
in the report section. If the email attributes are missing then no email is sent.


Example Config JSON Excerpt
---------------------------
.. code-block:: console
    
    "summary_report" : {"template":"This is a header\n<project_loop><project_name>:\n<author_loop><author_first>:\n<pub_loop><title></pub_loop></author_loop></project_loop>",
                        
                        "columns":{"Project":"<project_name>", "Author":"<author_first>; <author_last>", "Publication":"<title>"},
                        "column_order":["Project", "Author", "Publication"],
                        "sort":["Project", "Author"],
                        "file_format":"csv",
                        "separator":"\t",
                        
                        "filename":"summary_report.txt",
                        
                        "email_body":"Please see attached summary_report.",
                        "email_subject":"Summary of Publications",
                        "to_email":["person1@email.edu"],
                        "from_email":"your_email@email.edu",
                        "cc_email":["person2@email.edu"]}
                        
    Note that "template" takes precedent over "columns" so if both are specified "template" is used. This example is just trying to give a full example.




Summary Report
~~~~~~~~~~~~~~
Using the summary_report section of the configuration JSON a custom summary report 
can be created. Academic Tracker will read the template or columns attribute of 
this section and certain keywords (described below) will be replaced with information 
collected during the run. The keywords and inherent nature of how the report is 
built differs between author_search and reference_search.

If the summary_report section is missing then no summary report will be made. 
If the template and columns attributes are not in the summary_report section then 
a default template will be used (described below). 

Summary reports are saved in the tracker directory under summary_report.txt by default.


Author Search
-------------
The report for the author_search is built by looping over each project, each 
author associated with the project, each publication associated with the author, 
and each author on the publication. The template for author_search has 5 sections, 
1 for each loop (project_loop, author_loop, pub_loop, pub_author_loop, and reference_loop). Tags 
denote the beginning and end of each loop.
 
The section determines when keywords in the template are replaced. Keywords inside
the pub_author_loop section are replaced for each author on the publication. Keywords 
inside the reference loop section are replaced for each reference on the publication. 
Keywords inside the pub_loop section are replaced for each publication associated 
with the author. Keywords inside the author_loop are replaced for each author 
associated with the project. Keywords inside the project loop section are replaced 
for each project. The sections are expected to be nested inside of each other, 
so the pub_author_loop and reference_loop tags should be inside the pub_loop tags, the pub_loop tags 
should be inside the author_loop tags, and the author_loop tags should be inside 
the project_loop tags. The pub_author_loop and reference_loop are on the same level 
and should not be nested within each other. Any incorrect nesting will most likely 
cause the report not to look as expected.

If specifying a tabular report using the "columns" attribute the loops are determined 
by what keywords are present. If there are keywords from the pub_author_loop in 
"columns" then a new row will be created for each publication author, but if there 
are only keywords from the author_loop then a new row will be created for each 
author.


Reference Search
----------------
The report for the reference_search is built by looping over each publication matched 
in the reference, and each author on the publication. The template has 3 sections, 
1 for each loop (pub_loop, pub_author_loop, and reference_loop). Tags denote the beginning and end 
of each loop. The section determines when keywords in the template are replaced. 
Keywords inside the pub_author_loop section are replaced for each author on the 
publication. Keywords inside the reference loop section are replaced 
for each reference on the publication. Keywords inside the pub_loop section are replaced for each publication. 
The sections are expected to be nested inside of each other, so the pub_author_loop and reference_loop 
tags should be inside the pub_loop tags. The pub_author_loop and reference_loop are on the same level 
and should not be nested within each other. Any incorrect nesting will most likely 
cause the report not to look as expected.


Project Report
~~~~~~~~~~~~~~
Project reports are only created for author_search. There is no conception of them 
in reference_search. To create project reports for a project include the project_report 
attribute for the project in the config JSON. The project report works similar 
to the summary report but is isolated to one project so lacks the project loop. 

If the project_report attribute is missing then no project report will be made. 
If the template and columns attributes are not in the project_report section then 
a default template will be used (described below). If from_email is absent then 
1 report that loops over each author and publication in the project will be 
generated and no emails sent. If from_email is provided and to_email is provided 
then the report is emailed. If to_email is not provided then a report is generated 
for each author individually and emailed to each author.

Project reports are saved in the tracker directory under 
projectname_project_report.txt or projectname_authorname_project_report.txt by 
default.


Keywords
~~~~~~~~
.. code-block:: console

    <project_loop> </project_loop>         - Denotes the beginning and end of the project_loop section.
    <author_loop> </author_loop>           - Denotes the beginning and end of the author_loop section.
    <pub_loop> </pub_loop>                 - Denotes the beginning and end of the pub_loop section.
    <pub_author_loop> </pub_author_loop>   - Deontes the beginning and end of the pub_author_loop section.
    
    Project Keywords - Pulled from the project_descriptions section of the configuration JSON file.
    <project_name>
    
    Publication Keywords - Pulled from the data that will be in the publication.json file output. Any missing data will be either blank or None in the report.
    <abstract>
    <conclusions>
    <copyrights>
    <DOI>
    <journal>
    <keywords>
    <methods>
    <PMID>
    <results>
    <title>
    <PMCID>
    <publication_year>
    <publication_month>
    <publication_day>
    <first_author>
    <last_author>
    <authors>              Will be replaced with a comma separated list of author names of all authors.
    <grants>               Will be replaced with a comma separated list of grants associated with the publication.
    <queried_sources>      Will be replaced with a comma separated list of the sources where information was found for the publication.
    
    Pub Author Keywords - Pulled from the authors section of each publication in the publications.json file.
    <pub_author_first>
    <pub_author_last>
    <pub_author_initials>
    <pub_author_collective>        Some authors are a collective and have a special field for the name instead of first and last.
    <pub_author_affiliations>
    <pub_author_ORCID>
    <pub_author_id>
    
    Author Keywords - Pulled from the Authors section of the configuration JSON file.
    <author_first>
    <author_last>
    <author_collective>        Some authors are a collective and have a special field for the name instead of first and last.
    <author_name_search>
    <author_email>
    
    Publication References Keywords
    <reference_citation>      The full citation for the reference if available.
    <reference_title>         The reference title if available.
    <reference_PMID>          The reference PMID if available.
    <reference_PMCID>         The reference PMCID if available.
    <reference_DOI>           The reference DOI if available.
    
    Reference Search Specific Keywords
    <ref_line>                The line from the reference file used to find the publication.
    <tok_title>               The title parsed (tokenized) from the reference line.
    <tok_DOI>                 The DOI parsed (tokenized) from the reference line.
    <tok_PMID>                The PMID parsed (tokenized) from the reference line.
    <tok_authors>             The authors parsed (tokenized) from the reference line. Will be a comma separated list.
    <is_in_comparison_file>   If the publication is in the comparison file True otherwise False.
    
    

Examples
~~~~~~~~
.. code-block:: console

    Summary Report Author Search Example:
    <project_loop><project_name>
    <author_loop>        <author_first> <author_last>:
    <pub_loop>                <title> <authors> <grants>
    </pub_loop></author_loop></project_loop>
    
    Output:
    Core A Administrative Core
            Kelly Pennell:
                    Appalachian Environmental Health Literacy: Building Knowledge and Skills to Protect Health. Anna G Hoover, Annie Koempel, W Jay Christian, Kimberly I Tumlin, Kelly G Pennell, Steven Evans, Malissa McAlister, Lindell E Ormsbee, Dawn Brewer G08 LM013185, P30 ES026529, P42 ES007380, R01 ES032396
                    Direct injection analysis of per and polyfluoroalkyl substances in surface and drinking water by sample filtration and liquid chromatography-tandem mass spectrometry Kelly Pennell, Andrew Morris None Found
    Core B BEAC
            Jianzhong Chen:
                    Rubusoside-assisted solubilization of poorly soluble C6-Ceramide for a pilot pharmacokinetic study Jianzhong Chen None Found
                    Tris(1,3&#x2010;Dichloro&#x2010;2&#x2010;Propyl)Phosphate Is an Endocrine Disrupting Compound Causing Sex&#x2010;Specific Changes in Body Composition and Insulin Sensitivity Cetewayo Rashid, Sara Tenlep, Jianzhong Chen, Andrew Morris None Found
                    Pioglitazone does not synergize with mirabegron to increase beige fat or further improve glucose metabolism Jianzhong Chen, Andrew Morris None Found
                    The &beta;3-adrenergic receptor agonist mirabegron improves glucose homeostasis in obese humans Jianzhong Chen, Andrew Morris None Found
    
    
    Summary Report Reference Search Example:
    <pub_loop>Reference Line: <ref_line>
    Tokenized Reference:
            Authors: <tok_authors>
            Title: <tok_title>
            PMID: <tok_PMID>
            DOI: <tok_DOI>
    Queried Information:
            DOI: <DOI>
            PMID: <PMID>
            PMCID: <PMCID>
            Grants: <grants>
    
    </pub_loop>
    
    Output:
    Reference Line: Baran M, Huang Y, Moseley H, Montelione G.  Automated Analysis of Protein NMR Assignments and Structures. ChemInform. 2004 November; 35(45):-. doi: 10.1002/chin.200445293.
    Tokenized Reference:
       Authors: Baran M, Huang Y, Moseley H, Montelione G.
       Title: Automated Analysis of Protein NMR Assignments and Structures. 
       PMID: 
       DOI: 10.1002/chin.200445293
    Queried Information:
       DOI: 10.1002/chin.200445293
       PMID: None
       PMCID: None
       Grants: None
    
    Reference Line: Lane AN, Arumugam S, Lorkiewicz PK, Higashi RM, Laulhé S, Nantz MH, Moseley HN, Fan TW.  Chemoselective detection and discrimination of carbonyl-containing compounds in metabolite mixtures by 1H-detected 15N nuclear magnetic resonance. Magn Reson Chem.   2015 May;53(5):337-43. doi: 10.1002/mrc.4199. Epub 2015 Jan 23. PubMed PMID: 25616249; PubMed Central PMCID: PMC4409496.
    Tokenized Reference:
       Authors: Lane AN, Arumugam S, Lorkiewicz PK, Higashi RM, Laulhé S, Nantz MH, Moseley HN, Fan TW.
       Title: Chemoselective detection and discrimination of carbonyl-containing compounds in metabolite mixtures by 1H-detected 15N nuclear magnetic resonance. 
       PMID: 25616249 
       DOI: 10.1002/mrc.4199
    Queried Information:
       DOI: 10.1002/mrc.4199
       PMID: 25616249
       PMCID: PMC4409496
       Grants: R01ES022191-01, R01 ES022191, 1 U24 DK097215-01A1, P01CA163223-01A1, P01 CA163223, P30 CA177558, U24 DK097215
    
    
    Summary Report Tabular Example:
    {"columns": {"Project":"<project_name>"", "Author":"<author_first>", "Publication":"<title>"},
     "sort":["Project", "Author"]}
     
    Output:
    Project       Author           Publication
    Project 1     Jerika Durham    Differential Fuel Requirements of Human NK Cells and Human CD8 T Cells: Glutamine Regulates Glucose Uptake in Strongly Activated CD8 T Cells
    Project 2     Pan Deng         Nutritional modulation of the toxicity of environmental pollutants: Implications in atherosclerosis
    Project 2     Pan Deng         SSIF: Subsumption-based sub-term inference framework to audit gene ontology
    Project 2     Pan Deng         MEScan: a powerful statistical framework for genome-scale mutual exclusivity analysis of cancer mutations
    
    
    Project Report Individual Report Example:
    Hey <author_first>,\n\nThese are the publications I was able to find on PubMed. Are any missing?\n\n<author_loop><pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>\n\nKind regards,\n\nThis email was sent by an automated service. If you have any questions or concerns please email my creator ptth222@uky.edu"
    
    Output:
    Hey Angela,
    
    These are the publications I was able to find on PubMed. Are any missing?
    
            Hydrogels and Hydrogel Nanocomposites: Enhancing Healthcare Through Human and Environmental Treatment Angela M. Gutierrez, E. Molly Frazar, Victoria Klaus, Pranto Paul, J. Z. Hilt None Found
            Synthesis of magnetic nanocomposite microparticles for binding of chlorinated organics in contaminated water sources Angela M. Gutierrez, Rohit Bhandari, Jiaying Weng, Arnold Stromberg, Thomas D. Dziubla, J. Zach Hilt P42ES007380
    
    
    Project Report Example:
    <author_loop><author_first> <author_last>:\n<pub_loop>\t<title> <authors> <grants>\n</pub_loop></author_loop>\n\nKind regards,\n\n
    
    Output:
    
    Jerika Durham:
            Differential Fuel Requirements of Human NK Cells and Human CD8 T Cells: Glutamine Regulates Glucose Uptake in Strongly Activated CD8 T Cells Jerika Durham None Found
    Pan Deng:
            Nutritional modulation of the toxicity of environmental pollutants: Implications in atherosclerosis Pan Deng None Found
            SSIF: Subsumption-based sub-term inference framework to audit gene ontology Hunter Moseley None Found
            MEScan: a powerful statistical framework for genome-scale mutual exclusivity analysis of cancer mutations Hunter Moseley None Found
            
            
    Project Report Tabular Example:
    {"columns": {"Author":"<author_first>", "Publication":"<title>"},
     "sort":["Author"]}
     
    Output:
    Author           Publication
    Jerika Durham    Differential Fuel Requirements of Human NK Cells and Human CD8 T Cells: Glutamine Regulates Glucose Uptake in Strongly Activated CD8 T Cells
    Pan Deng         Nutritional modulation of the toxicity of environmental pollutants: Implications in atherosclerosis
    Pan Deng         SSIF: Subsumption-based sub-term inference framework to audit gene ontology
    Pan Deng         MEScan: a powerful statistical framework for genome-scale mutual exclusivity analysis of cancer mutations


Default Template Strings
------------------------
Author Search
~~~~~~~~~~~~~
Summary
+++++++
.. code-block:: console

    <project_loop><project_name>\n<author_loop>\t<author_first> <author_last>:<pub_loop>\n\t\tTitle: <title> \n\t\tAuthors: <authors> \n\t\tJournal: <journal> \n\t\tDOI: <DOI> \n\t\tPMID: <PMID> \n\t\tPMCID: <PMCID> \n\t\tGrants: <grants>\n</pub_loop>\n</author_loop></project_loop>


Project
+++++++
.. code-block:: console

    <author_loop><author_first> <author_last>:<pub_loop>\n\tTitle: <title> \n\tAuthors: <authors> \n\tJournal: <journal> \n\tDOI: <DOI> \n\tPMID: <PMID> \n\tPMCID: <PMCID> \n\tGrants: <grants>\n</pub_loop>\n</author_loop>


Author
++++++
.. code-block:: console

    <author_loop><author_first> <author_last>:<pub_loop>\n\tTitle: <title> \n\tAuthors: <authors> \n\tJournal: <journal> \n\tDOI: <DOI> \n\tPMID: <PMID> \n\tPMCID: <PMCID> \n\tGrants: <grants>\n</pub_loop>\n</author_loop>


Reference Search
----------------
.. code-block:: console

    <pub_loop>Reference Line:\n\t<ref_line>\nTokenized Reference:\n\tAuthors: <tok_authors>\n\tTitle: <tok_title>\n\tPMID: <tok_PMID>\n\tDOI: <tok_DOI>\nQueried Information:\n\tDOI: <DOI>\n\tPMID: <PMID>\n\tPMCID: <PMCID>\n\tGrants: <grants>\n\n</pub_loop>



Collaborator Report
~~~~~~~~~~~~~~~~~~~
Creating a collaborator report for an author is actually a unique use case from 
a typical author_search run, but since all of the steps are the same it is included 
as a report in author_search rather than being its own command. The idea is to 
be able to go through an author's publications and build a report that contains 
all of the other authors they have worked with. This type of report is required 
by some funding providers.

Collaborator reports are only created for author_search. There is no conception 
of them in reference_search. To create a collaborator report for an author include 
the collaborator_report attribute for the author in the config JSON. Although a 
collaborator report is done on a per author basis it can be included in a project 
of the config JSON as a convenience. If it is included in a project then a collaborator 
report will be created for each author associated with the project. 

The report is built by looping over each publication for the author and each 
author on the publication. Unlike the project report though only the pub_author_loop 
is available for the collaborator report. Tags denote the beginning and end of 
the loop.

The collaborator report is a little unique compared to the sumary and project 
reports because it defaults to a tabular file using the "columns" attribute rather 
than using the "template" attribute. 

If the collaborator_report attribute is missing then no collaborator report will 
be made. If the template and columns attributes are not in the collaborator_report 
section then a default columns and sort will be used (described below). If from_email 
is absent then no emails will be sent. If from_email is provided and to_email is 
provided then the report is sent to the to_email address, otherwise it is sent 
to the author's email.

Collaborator reports are saved in the tracker directory under 
author_id_collaborators.csv by default.


Keywords
~~~~~~~~
.. code-block:: console

    <pub_author_first>         -  Collaborator's first name.
    <pub_author_last>          -  Collaborator's last name.
    <pub_author_initials>      -  Collaborator's initials.
    <pub_author_affiliations>  -  Collaborator's affiliations.
    <pub_author_ORCID>         -  Collaborator's ORCID.
    <pub_author_id>            -  Collaborator's ID.
    

Examples
~~~~~~~~
.. code-block:: console

    Collaborator Report Attributes:
    columns = ["Name", "Affiliations"]
    values = ["<last_name>, <first_name>", "<affiliations>"]
    sort = ["Name"]
    
    Output CSV:
    Name	           Affiliations
    Brewer, Dawn	   University of Kentucky Department of Dietetics and Human Nutrition.
    Christian, W Jay   University of Kentucky College of Public Health.
    Evans, Steven	   Kentucky Water Resources Research Institute.
    
    
Default Values
~~~~~~~~~~~~~~
.. code-block:: console

    columns : {"Name":"<last_name>, <first_name>", "Affiliations":"<affiliations>"}
    column_order : ["Name", "Affiliations"]
    sort : ["Name"]
    separator : ","

    



