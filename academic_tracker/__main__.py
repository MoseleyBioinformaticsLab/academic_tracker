# -*- coding: utf-8 -*-


import docopt

from . import academic_tracker
from . import __version__


def main():
    
    args = docopt.docopt(academic_tracker.__doc__, version=str("Academic Tracker ") + __version__)
    
    if args["<authors_json_file>"] and args["<config_json_file>"]:
        academic_tracker.find_publications(args)
    else:
        print("Unrecognized command")               
                
                
if __name__ == "__main__":
    
    main()

