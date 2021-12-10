# -*- coding: utf-8 -*-


from . import helper_functions
import re


def parse_text_for_citations(text):
    """"""
       
    regex_dict = {"MLA":r"(.*) \"(.*)\" (.*)",
                  "APA":r"(.*) \(\d\d\d\d\)\. (.*)\. (.*)",
                  "Chicago":r"(.*) \"(.*)\" (.*)",
                  "Harvard":r"(.*) \d\d\d\d\. (.*)\. (.*)",
                  "Vancouver":r"(.*)\. (.*)\. (.*)"}
    
    tokenize_function_dict = {"MLA":tokenize_MLA_authors,
                              "APA":tokenize_APA_or_Harvard_authors,
                              "Chicago":tokenize_Chicago_authors,
                              "Harvard":tokenize_APA_or_Harvard_authors,
                              "Vancouver":tokenize_Vancouver_authors}
        
    parsed_pubs = []
    
    lines = text.split("\n")
    for line in lines:
        for citation_style, regex in regex_dict.items():
            groups = helper_functions.regex_match_return(regex, line)
            if groups:
                authors = groups[0]
                title = groups[1]
                tail = groups[2]
                
                tokenized_authors = tokenize_function_dict[citation_style](authors)
                

                match = helper_functions.regex_match_return(r"(?i).*pmid:\s*(\d+).*", tail)
                if match:
                    pmid = match[0]
                else:
                    pmid = None
                
                match = helper_functions.regex_match_return(r"(?i).*doi:\s*([^\s]+\w).*", tail)
                if match:
                    doi = match[0]
                    if "doi.org" in doi:
                        match = helper_functions.regex_match_return(r".*doi.org/(.*)", doi)
                        if match:
                            doi = match[0]
                else:
                    doi = None
                            
                parsed_pubs.append({"authors":tokenized_authors, "title":title, "PMID":pmid, "DOI":doi})
                break
            
    return parsed_pubs



def tokenize_Vancouver_authors(authors_string):
    """"""
    
    authors_string = authors_string.replace("&", "")
    authors_string = authors_string.replace("and", "")
    authors_string = authors_string.replace("et al", "")
    
    names = authors_string.split(",")
    names = [name.strip().split(" ") for name in names]
    
    return [{"last":name[0], "initials":name[1]} for name in names]




def tokenize_Chicago_authors(authors_string):
    """"""
    
    authors_string = authors_string.replace("...", "")
    authors_string = authors_string.replace("and", "")
    
    names = authors_string.split(",")
    
    ## The authors_string could have a period at the end that is not part of an initial.
    last_name = names[-1]
    last_name = last_name.split(" ")[-1]
    if len(last_name) > 2 and not re.match(r"([a-zA-Z]\.)+", last_name):
        names[-1] = names[-1][:-1]
    
    authors = []
    
    ##The first author in the list doesn't follow the same rules as the rest.
    first_author = names[0]
    if not " " in first_author:
        last = names.pop(0)
        first = names.pop(0)
        first = first.strip()
        first = first.split(" ")
        if len(first) > 1:
            middle = first[1]
            first = first[0]
        else:
            middle = ""
            first = first[0]
            
        authors.append({"first":first, "middle":middle, "last":last})
    
    for name in names:
        name = name.strip()
        tokens = name.split(" ")
        first = tokens[0]
        if len(tokens) > 2:
            middle = tokens[1]
            last = tokens[2]
        else:
            middle = ""
            last = tokens[1]
            
        authors.append({"first":first, "middle":middle, "last":last})
        
    return authors




def tokenize_APA_or_Harvard_authors(authors_string):
    """"""
    
    authors_string = authors_string.replace("&", "")
    authors_string = authors_string.replace("and", "")
    authors_string = authors_string.replace("et al.", "")
    authors_string = authors_string.replace(" ", "")
    authors_string = authors_string.replace("...", "")
    
    names_and_initials = authors_string.split(",")

    names = []    
    initials = []
    for count, token in enumerate(names_and_initials):
        if not count%2:
            names.append(token)
        else:
            initials.append(token)
            
    return [{"last":name, "initials":initials[count]} for count, name in enumerate(names)]
    




def tokenize_MLA_authors(authors_string):
    """"""
    
    authors = []
    
    if "and" in authors_string or "&" in authors_string:
        MLA_2author = r"(.*), (and|&) (.*)\."
        
        groups = helper_functions.regex_match_return(MLA_2author, authors_string)
        
        if groups:
            
            if groups[0]:
                first_name_regex = r"(.*), (.*) (.*)|(.*), (.*)"
                first_name_groups = helper_functions.regex_match_return(first_name_regex, groups[0])
                
                if first_name_groups:
                    if first_name_groups[0]:
                        first = first_name_groups[1]
                        middle = first_name_groups[2]
                        last = first_name_groups[0]
                    else:
                        first = first_name_groups[3]
                        middle = ""
                        last = first_name_groups[4]
                   
                    authors.append({"first":first, "middle":middle, "last":last})
            
            ##Tokenize the second name for MLA if 2 authors
            if groups[2]:
                second_name = groups[2]
                name_tokens = second_name.split(" ")
                if len(name_tokens) == 2:
                    first = name_tokens[0]
                    middle = ""
                    last = name_tokens[1]
                elif len(name_tokens) == 3:
                    first = name_tokens[0]
                    middle = name_tokens[1]
                    last = name_tokens[2]
                
                authors.append({"first":first, "middle":middle, "last":last})
        

    elif "et al" in authors_string:
        MLA_3author = r"(.*), (.*) (.*), et al.|(.*), (.*), et al."
        
        groups = helper_functions.regex_match_return(MLA_3author, authors_string)
        
        if groups:
            if groups[0]:
                first = groups[1]
                middle = groups[2]
                last = groups[0]
            else:
                first = groups[3]
                middle = ""
                last = groups[4]
                
            authors.append({"first":first, "middle":middle, "last":last})
            
    else:

        MLA_1author = r"(.*), (.*) (.*)|(.*), (.*)\."
        
        groups = helper_functions.regex_match_return(MLA_1author, authors_string)
        
        if groups:
            if groups[0]:
                first = groups[1]
                middle = groups[2]
                last = groups[0]
            else:
                first = groups[3]
                middle = ""
                last = groups[4]
                
            authors.append({"first":first, "middle":middle, "last":last})
                
    return authors









