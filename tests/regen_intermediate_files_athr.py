# -*- coding: utf-8 -*-
"""
Regenerate intermediate testing files, must be ran from academic_tracker directory.
"""

import json
import copy
import os

import pymed
import xml.etree.ElementTree as ET

from academic_tracker.fileio import load_json
from academic_tracker.athr_srch_webio import search_PubMed_for_pubs, search_ORCID_for_pubs, search_Google_Scholar_for_pubs, search_Crossref_for_pubs



original_queries = load_json(os.path.join("tests", "testing_files", "all_queries.json"))
## Convert PubMed dictionaries back to articles class.
for author, pub_list in original_queries["PubMed"].items():
    new_list = []
    for pub in pub_list:
        new_list.append(pymed.article.PubMedArticle(ET.fromstring(pub["xml"])))
    original_queries["PubMed"][author] = new_list


config_dict_Hunter_only = load_json(os.path.join("tests", "testing_files", "config_Hunter_only.json"))




running_pubs = {}
running_pubs1, _ = search_PubMed_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
running_pubs2, _ = search_ORCID_for_pubs(copy.deepcopy(running_pubs1), "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
running_pubs3, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs2), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])
running_pubs4, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs3), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])

running_pubs5, _ = search_PubMed_for_pubs(copy.deepcopy(running_pubs4), config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
running_pubs6, _ = search_ORCID_for_pubs(copy.deepcopy(running_pubs5), "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
running_pubs7, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs6), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])
running_pubs8, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs7), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])

with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "all", "running_pubs1.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "all", "running_pubs2.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "all", "running_pubs3.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs3, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "all", "running_pubs4.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs4, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "all", "running_pubs5.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs5, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "all", "running_pubs6.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs6, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "all", "running_pubs7.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs7, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "all", "running_pubs8.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs8, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "all", "publication_dict.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs8, indent=2, sort_keys=True))



running_pubs = {}
running_pubs1, _ = search_PubMed_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
running_pubs2, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs1), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])
running_pubs3, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs2), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])

running_pubs4, _ = search_PubMed_for_pubs(copy.deepcopy(running_pubs3), config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
running_pubs5, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs4), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])
running_pubs6, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs5), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])

with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_ORCID", "running_pubs1.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_ORCID", "running_pubs2.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_ORCID", "running_pubs3.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs3, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_ORCID", "running_pubs4.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs4, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_ORCID", "running_pubs5.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs5, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_ORCID", "running_pubs6.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs6, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_ORCID", "publication_dict.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs6, indent=2, sort_keys=True))



running_pubs = {}
running_pubs1, _ = search_PubMed_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
running_pubs2, _ = search_ORCID_for_pubs(copy.deepcopy(running_pubs1), "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
running_pubs3, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs2), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])

running_pubs4, _ = search_PubMed_for_pubs(copy.deepcopy(running_pubs3), config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
running_pubs5, _ = search_ORCID_for_pubs(copy.deepcopy(running_pubs4), "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
running_pubs6, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs5), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])

with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_Crossref", "running_pubs1.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_Crossref", "running_pubs2.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_Crossref", "running_pubs3.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs3, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_Crossref", "running_pubs4.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs4, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_Crossref", "running_pubs5.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs5, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_Crossref", "running_pubs6.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs6, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_Crossref", "publication_dict.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs6, indent=2, sort_keys=True))



running_pubs = {}
running_pubs1, _ = search_PubMed_for_pubs(running_pubs, config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
running_pubs2, _ = search_ORCID_for_pubs(copy.deepcopy(running_pubs1), "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
running_pubs3, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs2), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])

running_pubs4, _ = search_PubMed_for_pubs(copy.deepcopy(running_pubs3), config_dict_Hunter_only["Authors"], "asdf", original_queries["PubMed"])
running_pubs5, _ = search_ORCID_for_pubs(copy.deepcopy(running_pubs4), "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
running_pubs6, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs5), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])

with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_Google_Scholar", "running_pubs1.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_Google_Scholar", "running_pubs2.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_Google_Scholar", "running_pubs3.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs3, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_Google_Scholar", "running_pubs4.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs4, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_Google_Scholar", "running_pubs5.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs5, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_Google_Scholar", "running_pubs6.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs6, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_Google_Scholar", "publication_dict.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs6, indent=2, sort_keys=True))



running_pubs = {}
running_pubs1, _ = search_ORCID_for_pubs(running_pubs, "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
running_pubs2, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs1), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])
running_pubs3, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs2), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])

running_pubs4, _ = search_ORCID_for_pubs(copy.deepcopy(running_pubs3), "asdf", "asdf", config_dict_Hunter_only["Authors"], original_queries["ORCID"])
running_pubs5, _ = search_Google_Scholar_for_pubs(copy.deepcopy(running_pubs4), config_dict_Hunter_only["Authors"], "asdf", original_queries["Google Scholar"])
running_pubs6, _ = search_Crossref_for_pubs(copy.deepcopy(running_pubs5), config_dict_Hunter_only["Authors"], "asdf", original_queries["Crossref"])

with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_PubMed", "running_pubs1.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs1, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_PubMed", "running_pubs2.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs2, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_PubMed", "running_pubs3.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs3, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_PubMed", "running_pubs4.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs4, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_PubMed", "running_pubs5.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs5, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_PubMed", "running_pubs6.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs6, indent=2, sort_keys=True))
with open(os.path.join("tests", "testing_files", "new_intermediate_results", "author_search", "no_PubMed", "publication_dict.json"),'w') as jsonFile:
    jsonFile.write(json.dumps(running_pubs6, indent=2, sort_keys=True))






