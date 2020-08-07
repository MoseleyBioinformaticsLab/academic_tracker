from json import dumps
from stalker.fileio import load_json
from stalker.webio import request_publications


if __name__ == "__main__":
    # load list of authors
    author_list = load_json("../data/authors.json")
    publication_dict = request_publications(author_list)

    with open("../data/publications.json", "w") as f:
        f.write(dumps(publication_dict, indent=4))
