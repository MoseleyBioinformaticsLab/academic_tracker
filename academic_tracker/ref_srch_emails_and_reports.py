# -*- coding: utf-8 -*-
"""
Functions to create emails and reports for reference_search.
"""

from . import helper_functions



def convert_tokenized_authors_to_str(authors):
    """"""
    
    authors_string = ""
    for author in authors:
        if "first" in author:
            if author["first"]:
                authors_string += author["first"]
                if author["last"]:
                    authors_string += " " + author["last"] + ", "
                else:
                    authors_string += ", "
            elif author["last"]:
                authors_string += author["last"] + ", "
        else:
            if author["last"]:
                authors_string += author["last"]
                if author["initials"]:
                    authors_string += " " + author["initials"] + ", "
                else:
                    authors_string += ", "
            else:
                authors_string += author["initials"] + ", "
        
    authors_string = authors_string[:-2]
            
    return authors_string




def create_report_from_template(template_string, publication_dict, is_citation_in_prev_pubs_list, tokenized_citations):
    """"""
    
    simple_publication_keywords_map = {"<abstract>":"abstract",
                                        "<conclusions>":"conclusions",
                                        "<copyrights>":"copyrights",
                                        "<DOI>":"doi",
                                        "<journal>":"journal",
                                        "<keywords>":"keywords",
                                        "<methods>":"methods",
                                        "<PMID>":"pubmed_id",
                                        "<results>":"results",
                                        "<title>":"title",
                                        "<PMCID>":"PMCID",}
    
    publication_date_keywords_map = {"<publication_year>":["publication_date", "year"],
                                     "<publication_month>":["publication_date", "month"],
                                     "<publication_day>":["publication_date", "day"],}
    
    tokenized_keywords_map = {"<tok_title>":"title", 
                              "<tok_DOI>":"DOI", 
                              "<tok_PMID>":"PMID"}
    
    matching_key_for_citation = [citation["pub_dict_key"] for citation in tokenized_citations]
    
    report_string = ""
    for pub_id, pub_values in publication_dict.items():
        template_string_copy = template_string
        
        for keyword, pub_key in simple_publication_keywords_map.items():
            template_string_copy = template_string_copy.replace(keyword, str(pub_values[pub_key]))
            
        authors = ",".join([str(author["firstname"]) + " " + str(author["lastname"]) for author in pub_values["authors"]])
        template_string_copy = template_string_copy.replace("<authors>", authors)
        
        if pub_values["grants"]:
            grants = ", ".join(pub_values["grants"])
        else:
            grants = "None"
        template_string_copy = template_string_copy.replace("<grants>", grants)
        
        for keyword, key_list in publication_date_keywords_map.items():
            template_string_copy = template_string_copy.replace(keyword, str(helper_functions.nested_get(pub_values, key_list)))
        
        tok_index = matching_key_for_citation.index(pub_id)
        for keyword, tok_key in tokenized_keywords_map.items():
            template_string_copy = template_string_copy.replace(keyword, str(tokenized_citations[tok_index][tok_key]))
            
        tok_authors = convert_tokenized_authors_to_str(tokenized_citations[tok_index]["authors"])
        template_string_copy = template_string_copy.replace("<tok_authors>", tok_authors)
        
        if tokenized_citations[tok_index]["reference_line"]:
            pretty_print = tokenized_citations[tok_index]["reference_line"].split("\n")
            pretty_print = " ".join([line.strip() for line in pretty_print])
            template_string_copy = template_string_copy.replace("<ref_line>", pretty_print)
        
        if is_citation_in_prev_pubs_list:
            template_string_copy = template_string_copy.replace("<is_in_comparison_file>", str(is_citation_in_prev_pubs_list[tok_index]))
        
        report_string += template_string_copy

    return report_string




def create_reference_search_diagnostic(publication_dict, is_citation_in_prev_pubs_list, tokenized_citations):
    """"""
    
    report_string = ""
    for count, citation in enumerate(tokenized_citations):
        if tokenized_citations[count]["reference_line"]:
            pretty_print = tokenized_citations[count]["reference_line"].split("\n")
            pretty_print = " ".join([line.strip() for line in pretty_print])
            report_string += "Reference Line: " + pretty_print + "\n"
        
        report_string += "Tokenized Reference: \n\tAuthors: " + convert_tokenized_authors_to_str(citation["authors"]) + " \n\tTitle: " + citation["title"]
        if citation["PMID"]:
            report_string += " \n\tPMID: " + str(citation["PMID"])
        if citation["DOI"]:
            report_string += " \n\tDOI: " + citation["DOI"]
        report_string += "\n"
        
        if tokenized_citations[count]["pub_dict_key"]:
            doi = publication_dict[tokenized_citations[count]["pub_dict_key"]]["doi"]
            pmid = publication_dict[tokenized_citations[count]["pub_dict_key"]]["pubmed_id"]
            pmcid = publication_dict[tokenized_citations[count]["pub_dict_key"]]["PMCID"]
            if publication_dict[tokenized_citations[count]["pub_dict_key"]]["grants"]:
                grants = ", ".join(publication_dict[tokenized_citations[count]["pub_dict_key"]]["grants"])
        
                
        if not doi:
            doi = "Not Found"
        if not pmid:
            pmid = "Not Found"
        if not pmcid:
            pmcid = "Not Found"
        if not grants:
            grants = "None Found"
        
        report_string += "Queried Information: \n\tDOI: " + doi + \
                         " \n\tPMID: " + pmid + \
                         " \n\tPMCID: " + pmcid +\
                         " \n\tGrants: " + grants
        if is_citation_in_prev_pubs_list:
            report_string += " \n\tIs In Comparison File: " + str(is_citation_in_prev_pubs_list[count])
        
        report_string += "\n\n\n"
        
    return report_string



def create_tokenization_report(tokenized_citations):
    """"""
    
    report_string = ""
    for count, citation in enumerate(tokenized_citations):
        if tokenized_citations[count]["reference_line"]:
            pretty_print = tokenized_citations[count]["reference_line"].split("\n")
            pretty_print = " ".join([line.strip() for line in pretty_print])
            report_string += "Reference Line: " + pretty_print + "\n"
        
        report_string += "Tokenized Reference: \n\tAuthors: " + convert_tokenized_authors_to_str(citation["authors"]) + " \n\tTitle: " + citation["title"]
        if citation["PMID"]:
            report_string += " \n\tPMID: " + str(citation["PMID"])
        if citation["DOI"]:
            report_string += " \n\tDOI: " + citation["DOI"]
        report_string += "\n\n"
        
    return report_string

