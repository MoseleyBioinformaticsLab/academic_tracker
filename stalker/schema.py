# -*- coding: utf-8 -*-
"""
Problems with Schema:
    Very poor support for better error messages.
    Only supports Any checking for elements of a list, can't do All.

"""

from schema import Schema, Optional, And, Use, Or, SchemaError
import re


## Replacing the SchemaError class in the library with this one lets you print the auto messages and error.
## autos and errors are typically a tuple though for some reason. It's hard to figure out when to pop off auto.
## the commented out line seems to work okay, but I only tested one example. 
class SchemaError(Exception):
    """Error during Schema validation."""

    def __init__(self, autos, errors=None):
        self.autos = autos if type(autos) is list else [autos]
        self.errors = errors if type(errors) is list else [errors]
        if type(errors) is list and any(errors):
            print(autos)
#            self.autos.pop()
            self.autos += errors
        Exception.__init__(self, self.code)

    @property
    def code(self):
        """
        Removes duplicates values in auto and error list.
        parameters.
        """

        def uniq(seq):
            """
            Utility function that removes duplicate.
            """
            seen = set()
            seen_add = seen.add
            # This way removes duplicates while preserving the order.
            return [x for x in seq if x not in seen and not seen_add(x)]

        data_set = uniq(i for i in self.autos if i is not None)
        return "\n".join(data_set)











def uniq(seq):
    """
    Utility function that removes duplicate.
    """
    seen = set()
    seen_add = seen.add
    # This way removes duplicates while preserving the order.
    return [x for x in seq if x not in seen and not seen_add(x)]

temp = {'grants': [''], 
 'cutoff_year': 2019,
 'affiliations': ['kentucky'],
 'from_email': 'ptth222@uky.edu',
 'cc_email': [],
 'email_template': '<formatted-string>',
 'email_subject': '<formatted-string>'}

def len_greater_than_zero(x):
    return len(x)



## Alias And so when we use for error messages it's less confusing.
Error= And    


config_schema = Schema(
        
        {
            "grants" : And([str], [len], len, error="asdf"),
            "cutoff_year": And(Use(int), lambda n: n <= 3000),
            "affiliations": And([str], [len], len),
            "from_email": And(str, lambda f: re.match(r".+@.+\..+", f)),
            Optional("cc_email"): [And(str, lambda f: re.match(r".+@.+\..+", f))],
            "email_template": str,
            "email_subject": str}, 
                
            name="Configuration File Schema:",
            ignore_extra_keys=True
        
        )

try:
    config_schema.validate(temp)
except SchemaError as exc:
    raise exc

publications_schema = Schema()

authors_schema = Schema()















Schema(And([str], [len], len)).validate(["asdf", ""])
