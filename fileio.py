from os.path import exists
from json import loads


def load_json(filepath):
    """Adds error checking around loading a json file.
    
    Args:
        filepath (str): filepath to the json file
        
    Returns:
        internal_data (dict): json read from file in a dictionary
        
    """
    if exists(filepath):
        try:
            with open(filepath, "r") as f:
                internal_data = loads(f.read())
        except Exception as e:
            raise e

    return internal_data
