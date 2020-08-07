from os.path import exists
from json import loads


def load_json(filepath):
    if exists(filepath):
        try:
            with open(filepath, "r") as f:
                internal_data = loads(f.read())
        except Exception as e:
            raise e

    return internal_data
