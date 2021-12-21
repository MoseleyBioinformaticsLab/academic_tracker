# -*- coding: utf-8 -*-

## How to import from a full file path
#import importlib
#path_to_helper = 'C:/Users/Sparda/Desktop/Moseley Lab/Code/academic_tracker/academic_tracker/citation_parsing.py'
#spec = importlib.util.spec_from_file_location("module.name", path_to_helper)
#foo = importlib.util.module_from_spec(spec)
#citation_parsing = importlib.util.module_from_spec(spec)
#spec.loader.exec_module(citation_parsing)

from . import helper_functions
import re
import bs4


def parse_text_for_citations(text):
    """"""
 
## A known issue with these regexes is that authors with 2nd, 3rd, etc in thier name won't get picked up, but allowing numbers in causes too many false positives.      
    regex_dict = {"MLA":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?]+)\s+\"(.*)\"\s+(.*)",
                  "APA":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?]+)\s+\(\d\d\d\d\)\.\s+([^\.]+)\.\s+(.*)",
                  "Chicago":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?]+)\s+\"(.*)\"\s+(.*)",
                  "Harvard":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?]+)\s+\d\d\d\d\.\s+([^\.]+)\.\s+(.*)",
                  "Vancouver":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?]+)\.\s+([^\.]+)\.\s+(.*)"}
    
    tokenize_function_dict = {"MLA":tokenize_MLA_or_Chicago_authors,
                              "APA":tokenize_APA_or_Harvard_authors,
                              "Chicago":tokenize_MLA_or_Chicago_authors,
                              "Harvard":tokenize_APA_or_Harvard_authors,
                              "Vancouver":tokenize_Vancouver_authors}
        
    parsed_pubs = []
    reference_lines = []
    
    lines = text.split("\n")
    for count, line in enumerate(lines):
        for citation_style, regex in regex_dict.items():
            groups = helper_functions.regex_match_return(regex, line)
            if groups:
                authors = groups[0].strip()
                title = groups[1].strip()
                tail = groups[2].strip()
                
                tokenized_authors = tokenize_function_dict[citation_style](authors)
                
                match = helper_functions.regex_match_return(r"(?i).*pmid:\s*(\d+).*", tail)
                if match:
                    pmid = match[0]
                else:
                    pmid = None
                
                match = helper_functions.regex_match_return(r"(?i).*doi:\s*([^\s]+\w).*", tail)
                if match:
                    doi = match[0].lower()
                    if "doi.org" in doi:
                        match = helper_functions.regex_match_return(r".*doi.org/(.*)", doi)
                        if match:
                            doi = match[0]
                else:
                    doi = None
                            
                parsed_pubs.append({"authors":tokenized_authors, "title":title, "PMID":pmid, "DOI":doi})
                reference_lines.append(line.strip())
                break
            
    return parsed_pubs, reference_lines



def tokenize_Vancouver_authors(authors_string):
    """"""
    
    authors_string = authors_string.replace("&", "")
    authors_string = authors_string.replace("and", "")
    authors_string = authors_string.replace("et al", "")
    
    names = authors_string.split(",")
    names = [name.strip().split(" ") for name in names]
    
    return [{"last":name[0], "initials":name[1]} if len(name) >1 else {"last":name[0], "initials":""} for name in names]




def tokenize_MLA_or_Chicago_authors(authors_string):
    """"""
    
    authors_string = authors_string.replace("...", "")
    authors_string = authors_string.replace("and", "")
    authors_string = authors_string.replace("&", "")
    authors_string = authors_string.replace("et al.", "")
    
    authors_string = authors_string.strip()
    
    names = authors_string.split(",")
    names = [name for name in names if name]
    
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
        if len(tokens) == 1:
            first = ""
            middle = ""
            last = tokens[0]
        elif len(tokens) > 2:
            first = tokens[0]
            middle = tokens[1]
            last = tokens[2]
        else:
            first = tokens[0]
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

    authors = []
    previous_token_type = ""
    for token in names_and_initials:
        if re.match(r".*\..*", token):
            if previous_token_type == "last_name":
                authors[-1]["initials"] = token
            else:
                authors.append({"last":"", "initials":token})
            previous_token_type = "initials"
        else:
            authors.append({"last":token, "initials":""})
            previous_token_type = "last_name"
                
            
    return authors
    


def tokenize_myncbi_citations(html):
    """
    Note that authors and title can be empty or missing.
    """
    
    soup = bs4.BeautifulSoup(html, "html.parser")
    
    parsed_pubs = []
    reference_lines = []
    
    citations = soup.find_all("div", class_ = "ncbi-docsum")
    for citation in citations:
        
        authors = citation.find("span", class_ = "authors")
        if authors:
            authors = authors.text
        else:
            authors = list(citation.children)[1].text
            
        authors = tokenize_Vancouver_authors(authors)
        
        ## Look for blank authors and remove them.
        authors = [author for author in authors if any([author_attribute for author_attribute in author.values()])]
        
        ## If there is not a span with the class title then the title should be a 
        ## hyperlink that is the 3rd child. 
        title = citation.find("span", class_ = "title")
        if title:
            title = title.text.strip()
        else:
            children = list(citation.children)
            if children[2].name == "span":
                title = ""
            else:
                title = children[2].text.strip()
            
        doi = citation.find("span", class_ = "doi")
        if doi:
            match = helper_functions.regex_match_return(r"(?i).*doi:\s*([^\s]+\w).*", doi.text)
            if match:
                doi = match[0].lower()
            else:
                doi = ""
        else:
            doi = ""
            
        pmid = citation.find("span", class_ = "pmid")
        if pmid:
            match = helper_functions.regex_match_return(r"(?i).*pmid:\s*(\d+).*", pmid.text)
            if match:
                pmid = match[0]
            else:
                pmid = ""
        else:
            pmid = ""
        
        parsed_pubs.append({"authors":authors, "title":title, "PMID":pmid, "DOI":doi})
        reference_lines.append(citation.text.strip())
        
    return parsed_pubs, reference_lines



def parse_MEDLINE_format(text_string):
    """"""
    
    parsed_pubs = []
    pmid = ""
    doi = ""
    title = ""
    found_title = False
    authors = []
    lines = text_string.split("\n")
    for line in lines:
        if line:
            field = line[0:4]
            if field == "PMID":
                pmid = int(line[6:])
            elif field == "TI  ":
                title = line[6:]
                found_title = True
            elif field == "    " and found_title:
                title += line[6:]
            elif not field == "    " and found_title:
                found_title = False
            elif field == "AU  ":
                last_and_initials = line[6:].split(" ")
                if len(last_and_initials) > 2:
                    if sum(1 for char in last_and_initials[1] if char.isupper()) == 1 and len(last_and_initials[1]) > 1:
                        authors.append({"last":last_and_initials[0] + " " + last_and_initials[1], "initials":last_and_initials[2]})
                    else:
                        authors.append({"last":last_and_initials[0], "initials":last_and_initials[1]})
                elif len(last_and_initials) == 2:
                    authors.append({"last":last_and_initials[0], "initials":last_and_initials[1]})
                else:
                    authors.append({"last":last_and_initials[0], "initials":""})
            elif field == "LID ":
                value = line[6:].lower()
                if "doi" in value:
                    doi = value.split(" ")[0]
            elif field == "AID ":
                value = line[6:].lower()
                if "doi" in value:
                    doi = value.split(" ")[0]
                
        else:
            if pmid or doi or title or authors:
                parsed_pubs.append({"authors":authors, "title":title, "PMID":pmid, "DOI":doi})
            pmid = ""
            doi = ""
            title = ""
            found_title = False
            authors = []
            
    return parsed_pubs




