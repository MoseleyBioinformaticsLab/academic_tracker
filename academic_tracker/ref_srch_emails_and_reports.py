# -*- coding: utf-8 -*-
"""
Functions to create emails and reports for reference_search.
"""


DEFAULT_SUMMARY_TEMPLATE = "Reference Line:\n\t<ref_line>\nTokenized Reference:\n\tAuthors: <tok_authors>\n\tTitle: <tok_title>\n\tPMID: <tok_PMID>\n\tDOI: <tok_DOI>\nQueried Information:\n\tDOI: <DOI>\n\tPMID: <PMID>\n\tPMCID: <PMCID>\n\tGrants: <grants>\n\n"


def convert_tokenized_authors_to_str(authors):
    """Combine authors into a comma separated string.
    
    Try to do first_name last_name for each author, but if first name isn't there
    then last_name initials. ex. first_name1 last_name1, last_name2 initials2
    
    Args:
        authors (list): a list of dictionaries [{"last":last_name, "initials":initials}, {"last":last_name, "first":first_name}]
        
    Returns:
        authors_string (str): comma separated list of authors.
    """
    
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
    
    if not authors_string:
        authors_string = str(None)
            
    return authors_string




def create_report_from_template(publication_dict, is_citation_in_prev_pubs_list, tokenized_citations, template_string = DEFAULT_SUMMARY_TEMPLATE):
    """Create project report based on template_string.
    
    Loop over each publication in publication_dict and build a report based on 
    the tags in the template_string. Details about reports are in the documentation.
    
    Args:
        publication_dict (dict): keys and values match the publications JSON file.
        is_citation_in_prev_pubs_list (list): list of bools that indicate whether or not the citation at the same index in tokenized_citations is in the prev_pubs
        tokenized_citations (list): list of dicts. Matches the JSON schema for tokenized citations.
        template_string (str): string with tags indicated what information to put in the report.
        
    Returns:
        report_string (str): text of the created report.
    """
    
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
    
    publication_date_keywords_map = {"<publication_year>":"year",
                                     "<publication_month>":"month",
                                     "<publication_day>":"day"}
    
    tokenized_keywords_map = {"<tok_title>":"title", 
                              "<tok_DOI>":"DOI", 
                              "<tok_PMID>":"PMID"}
    
    matching_key_for_citation = [citation["pub_dict_key"] for citation in tokenized_citations]
    
    report_string = ""
    for pub_id, pub_values in publication_dict.items():
        template_string_copy = template_string
        
        for keyword, pub_key in simple_publication_keywords_map.items():
            template_string_copy = template_string_copy.replace(keyword, str(pub_values[pub_key]))
            
        authors = ", ".join([str(author["firstname"]) + " " + str(author["lastname"]) for author in pub_values["authors"]])
        template_string_copy = template_string_copy.replace("<authors>", authors)
        
        if pub_values["grants"]:
            grants = ", ".join(pub_values["grants"])
        else:
            grants = "None"
        template_string_copy = template_string_copy.replace("<grants>", grants)
        
        for keyword, date_key in publication_date_keywords_map.items():
            template_string_copy = template_string_copy.replace(keyword, str(pub_values["publication_date"][date_key]))
        
        tok_index = matching_key_for_citation.index(pub_id)
        for keyword, tok_key in tokenized_keywords_map.items():
            replacement = str(tokenized_citations[tok_index][tok_key])
            if not replacement:
                replacement = "None"
            template_string_copy = template_string_copy.replace(keyword, replacement)
            
        tok_authors = convert_tokenized_authors_to_str(tokenized_citations[tok_index]["authors"])
        template_string_copy = template_string_copy.replace("<tok_authors>", tok_authors)
        
        if tokenized_citations[tok_index]["reference_line"]:
            pretty_print = tokenized_citations[tok_index]["reference_line"].split("\n")
            pretty_print = " ".join([line.strip() for line in pretty_print])
            template_string_copy = template_string_copy.replace("<ref_line>", pretty_print)
        else:
            template_string_copy = template_string_copy.replace("<ref_line>", "N/A")
        
        if is_citation_in_prev_pubs_list:
            template_string_copy = template_string_copy.replace("<is_in_comparison_file>", str(is_citation_in_prev_pubs_list[tok_index]))
        else:
            template_string_copy = template_string_copy.replace("<is_in_comparison_file>", "N/A")
        
        report_string += template_string_copy

    return report_string




def create_tokenization_report(tokenized_citations):
    """Create a report that details all the information about how a reference was tokenized.
    
    Intended as a troubleshooting report.
    
    Args:
        tokenized_citations (list): list of dicts. Matches the JSON schema for tokenized citations.
        
    Returns:
        report_string (str): report text built from tokenized_citations.
    """
    
    report_string = ""
    for count, citation in enumerate(tokenized_citations):
        if tokenized_citations[count]["reference_line"]:
            pretty_print = tokenized_citations[count]["reference_line"].split("\n")
            pretty_print = " ".join([line.strip() for line in pretty_print])
            report_string += "Reference Line: \n\t" + pretty_print + "\n"
        else:
            report_string += "Reference Line: \n\tN/A\n"
        
        report_string += "Tokenized Reference: \n\tAuthors: " + convert_tokenized_authors_to_str(citation["authors"])
        if citation["title"]:
            report_string += "\n\tTitle: " + citation["title"]
        else:
            report_string += "\n\tTitle: None"
        if citation["PMID"]:
            report_string += "\n\tPMID: " + str(citation["PMID"])
        else:
            report_string += "\n\tPMID: None"
        if citation["DOI"]:
            report_string += "\n\tDOI: " + citation["DOI"]
        else:
            report_string += "\n\tDOI: None"
        report_string += "\n\n"
        
    return report_string



###############
## Unused
###############
    

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





