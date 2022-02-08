Reporting
=========

To allow users some flexibility in report creation a unique system for specifying 
their creation was created, and is described here. The key framework to keep in 
mind is that there are 2 different reports and their specifications are slightly 
different between each other and between author_search and reference_search.


Summary Report
~~~~~~~~~~~~~~
Using the summary_report section of the configuration JSON a custom summary report 
can be created. Academic Tracker will read the template attribute of this section 
and certain keywords (described below) will be replaced with information collected 
during the run. The keywords and inherent nature of how the report is built differs 
between author_search and reference_search.

If the summary_report section is missing then no summary report will be made. 
If the template property is not in the summary_report section then a default template 
will be used (described below). To email the report as an attachment simply include 
the email related attributes in the summary_report section. If the email attributes 
are missing then no email is sent.


Author Search
-------------
The report for the author_search is built by looping over each project, each 
author associated with the project, and each publication associated with the author. 
The template for author_search has 3 sections, 1 for each loop (project_loop, 
author_loop, and pub_loop). Tags denote the beginning and end of the author_loop 
and pub_loop, but not the project_loop as the whole template is considered to be 
the project_loop. The section determines when keywords in the template are replaced. 
Keywords inside the pub_loop section are replaced for each publication associated 
with the author. Keywords inside the author_loop are replaced for each author 
associated with the project. Keywords inside the project loop section are replaced 
for each project.


Reference Search
----------------
The report for the reference_search is built by looping over each publication matched 
in the reference. It does not have sections and keywords are replaced for each 
publication matched in the reference.


Project Report
~~~~~~~~~~~~~~
Project reports are only created for author_search. There is no conception of them 
in reference_search. To create project reports for a project include the project_report 
attribute for the project in the config JSON. The project report works similar 
to the summary report but is isolated to one project so lacks the project loop. 

If the project_report attribute is missing then no project report will be made. 
If the template property is not in the project_report section then a default template 
will be used (described below). If from_email is absent then 1 report that loops 
over each author and publication in the project will be generated and no emails 
sent. If from_email is provided and to_email is provided then the report is emailed. 
If to_email is not provided then a report is generated for each author individually 
and emailed to each author.


Keywords
~~~~~~~~
.. code-block:: console

    <author_loop> </author_loop>  - Denotes the beginning and end of the author_loop section.
    <pub_loop> </pub_loop>        - Denotes the beginning and end of the pub_loop section.
    
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
    <authors>              Will be replaced with a comma separated list of author names of all authors.
    <grants>               Will be replaced with a comma separated list of grants associated with the publication.
    
    Author Keywords - Pulled from the Authors section of the Project Tracking Configuration file.
    <author_first>
    <author_last>
    <author_name_search>
    <author_email>
    
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
    <project_name>
    <author_loop>        <author_first> <author_last>:
    <pub_loop>                <title> <authors> <grants>
    </pub_loop></author_loop>
    
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
    Reference Line: <ref_line>
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


Default Template Strings
~~~~~~~~~~~~~~~~~~~~~~~~
Author Search
-------------
Summary
+++++++
.. code-block:: console

    <project_name>\n<author_loop>\t<author_first> <author_last>:<pub_loop>\n\t\tTitle: <title> \n\t\tAuthors: <authors> \n\t\tJournal: <journal> \n\t\tDOI: <DOI> \n\t\tPMID: <PMID> \n\t\tPMCID: <PMCID> \n\t\tGrants: <grants>\n</pub_loop>\n</author_loop>


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

    Reference Line:\n\t<ref_line>\nTokenized Reference:\n\tAuthors: <tok_authors>\n\tTitle: <tok_title>\n\tPMID: <tok_PMID>\n\tDOI: <tok_DOI>\nQueried Information:\n\tDOI: <DOI>\n\tPMID: <PMID>\n\tPMCID: <PMCID>\n\tGrants: <grants>\n\n


