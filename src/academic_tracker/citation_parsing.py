# -*- coding: utf-8 -*-
"""
Citation Parsing
~~~~~~~~~~~~~~~~

Functions for parsing citations.
"""

import re

import bs4

from . import helper_functions


def parse_text_for_citations(text):
    """Parse text line by line and tokenize it.
    
    The function is aware of MLA, APA, Chicago, Harvard, and Vancouver style citations.
    Although the citation styles the function is aware of have standards for citations 
    in reality these standards are not strictly adhered to by the public. Therefore
    the function uses a more heuristic approach.
    
    Args:
        text (str): The text to parse.
        
    Returns:
        parsed_pubs (dict): the citations tokenized in a dictionary matching the tokenized citations JSON schema.  
    """
 
## A known issue with these regexes is that authors with 2nd, 3rd, etc in thier name won't get picked up, but allowing numbers in causes too many false positives.      
    regex_dict = {"MLA":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?]+)\s+\"(.*)\"\s+(.*)",
                  "APA":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?]+)\s+\(\d\d\d\d\)\.\s+([^\.]+)\.\s+(.*)",
                  "Chicago":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?]+)\s+\"(.*)\"\s+(.*)",
                  "Harvard":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?]+)\s+\d\d\d\d\.\s+([^\.]+)\.\s+(.*)",
                  "Vancouver":r"([^0-9!@#$%^*()[\]_+=\\|<>:;'\"{}`~/?.]+)\.\s+([^\.]+)\.\s+(.*)"}
    
    tokenize_function_dict = {"MLA":tokenize_MLA_or_Chicago_authors,
                              "APA":tokenize_APA_or_Harvard_authors,
                              "Chicago":tokenize_MLA_or_Chicago_authors,
                              "Harvard":tokenize_APA_or_Harvard_authors,
                              "Vancouver":tokenize_Vancouver_authors}
        
    parsed_pubs = []
    
    lines = text.split("\n")
    for count, line in enumerate(lines):
        for citation_style, regex in regex_dict.items():
            groups = helper_functions.regex_match_return(regex, line)
            if groups:
                authors = groups[0].strip()
                ## Sanity check to make sure we are looking at author names separated by commas and not a sentence with a comma in it.
                ## Assuming names won't be more than 4 words.
                temp_authors = authors.replace(" and ", ",")
                sanity_check = any([len(author.strip().split(" ")) > 4 for author in temp_authors.split(",")])
                if sanity_check:
                    continue
                title = groups[1].strip()
                tail = groups[2].strip()
                
                tokenized_authors = tokenize_function_dict[citation_style](authors)
                
                match = helper_functions.regex_match_return(r"(?i).*pmid:\s*(\d+).*", tail)
                pmid = match[0] if match else None
                
                match = helper_functions.regex_match_return(r"(?i).*doi:\s*([^\s]+\w).*", tail)
                if match:
                    doi = match[0].lower()
                    if "doi.org" in doi:
                        match = helper_functions.regex_match_return(r".*doi.org/(.*)", doi)
                        if match:
                            doi = match[0]
                else:
                    doi = None
                            
                parsed_pubs.append({"authors":tokenized_authors, "title":title, "PMID":pmid, "DOI":doi, "reference_line":line.strip(), "pub_dict_key":""})
                break
            
    return parsed_pubs



def tokenize_Vancouver_authors(authors_string):
    """Tokenize authors based on Vancouver citation style.
    
    Args:
        authors_string (str): string with the authors to tokenize.
        
    Returns:
        (list): list of dictionaries with the authors last names and initials. [{"last":lastname, "initials":initials}, ...]
    """
    
    authors_string = authors_string.replace("...", "")
    authors_string = authors_string.replace("&", ",")
    authors_string = authors_string.replace(" and ", ",")
    authors_string = authors_string.replace("et al", "")
    
    names = authors_string.split(",")
    names = [name.strip() for name in names if name.strip()]
    names = [name.split(" ") for name in names]
    
    return [{"last":name[0], "initials":name[1]} if len(name) >1 else {"last":name[0], "initials":""} for name in names]




def tokenize_MLA_or_Chicago_authors(authors_string):
    """Tokenize authors based on MLA or Chicago citation style.
    
    Args:
        authors_string (str): string with the authors to tokenize.
        
    Returns:
        (list): list of dictionaries with the authors first, middle, and last names. [{"first":firstname, "middle":middlename, "last":lastname}, ...]
    """
    
    authors_string = authors_string.replace("...", "")
    authors_string = authors_string.replace(" and ", ",")
    authors_string = authors_string.replace("&", ",")
    authors_string = authors_string.replace("et al.", "")
    
    authors_string = authors_string.strip()
    
    names = authors_string.split(",")
    names = [name.strip() for name in names if name.strip()]
    
    ## The authors_string could have a period at the end that is not part of an initial.
    last_name = names[-1]
    last_name = last_name.split(" ")[-1]
    if len(last_name) > 2 and not re.match(r"([a-zA-Z]\.)+", last_name) and "." in last_name:
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
    """Tokenize authors based on APA or Harvard citation style.
    
    Args:
        authors_string (str): string with the authors to tokenize.
        
    Returns:
        (list): list of dictionaries with the authors last names and initials. [{"last":lastname, "initials":initials}, ...]
    """
    
    authors_string = authors_string.replace("&", ",")
    authors_string = authors_string.replace(" and ", ",")
    authors_string = authors_string.replace("et al.", "")
    authors_string = authors_string.replace(" ", "")
    authors_string = authors_string.replace("...", "")
    
    names_and_initials = authors_string.split(",")
    names_and_initials = [token.strip() for token in names_and_initials if token.strip()]

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
    """Tokenize the citations on a MyNCBI HTML page.
    
    Note that authors and title can be missing or empty from the webpage.
    
    Args:
        html (str): the html of the MyNCBI page.
        
    Returns:
        parsed_pubs (dict): the citations tokenized in a dictionary matching the tokenized citations JSON schema. 
    """
    
    soup = bs4.BeautifulSoup(html, "html.parser")
    
    parsed_pubs = []
    
    citations = soup.find_all("div", class_ = "ncbi-docsum")
    for i, citation in enumerate(citations):
        
        authors_str = citation.find("span", class_ = "authors")
        authors_str = authors_str.text if authors_str else list(citation.children)[1].text
        
        authors_str = authors_str.strip()
        if authors_str and authors_str[-1] == ".":
            authors_str = authors_str[:-1]
        authors = tokenize_Vancouver_authors(authors_str)
        
        ## Some citations don't use Vancouver, so check to see if all initials are blank and if so try Harvard/APA.
        if all([not author["initials"] for author in authors]):
            authors = tokenize_APA_or_Harvard_authors(authors_str)
        
        ## Look for blank authors and remove them.
        authors = [author for author in authors if any([author_attribute for author_attribute in author.values()])]
        
        ## If there is not a span with the class title then the title should be a 
        ## hyperlink that is the 3rd child. 
        ## If the reference is a book then the "title" will likely be the book title, and "chaptertitle" will be the actual reference.
        chapter_title = citation.find("span", class_ = "chaptertitle")
        if chapter_title:
            title = chapter_title.text.strip()
        else:
            title = citation.find("span", class_ = "title")
            if title:
                title = title.text.strip()
            else:
                children = list(citation.children)
                title = "" if children[2].name == "span" else children[2].text.strip()
            
        doi = citation.find("span", class_ = "doi")
        if doi:
            match = helper_functions.regex_match_return(r"(?i).*doi:\s*([^\s]+\w).*", doi.text)
            doi = match[0].lower() if match else ""
        else:
            doi = ""
            
        pmid = citation.find("span", class_ = "pmid")
        if pmid:
            match = helper_functions.regex_match_return(r"(?i).*pmid:\s*(\d+).*", pmid.text)
            pmid = match[0] if match else ""
        else:
            pmid = ""
        
        parsed_pubs.append({"authors":authors, "title":title, "PMID":pmid, "DOI":doi, "reference_line":citation.text.strip(), "pub_dict_key":""})
        
    return parsed_pubs




def parse_MEDLINE_format(text_string):
    """Tokenize text_string based on it being of the MEDLINE format.
    
    Args:
        text_string (str): The string to tokenize.
        
    Returns:
        parsed_pubs (dict): the citations tokenized in a dictionary matching the tokenized citations JSON schema. 
    """
    
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
                parsed_pubs.append({"authors":authors, "title":title, "PMID":pmid, "DOI":doi, "reference_line":"", "pub_dict_key":""})
            pmid = ""
            doi = ""
            title = ""
            found_title = False
            authors = []
            
    return parsed_pubs




