"""

"""
from json import dumps, loads
from fileio import load_json
from webio import create_email_message, request_publications, send_email


if __name__ == "__main__":

    from_email = input("From Email: ")
    password = input("Password: ")
    to_email = input("To Email: ")
    cc = input("CC: ")

    # load list of authors
    author_list = load_json("../data/authors.json")
    publication_dict = request_publications(author_list)

    with open("../data/publications.json", "r") as f:
        old_publication_dict = loads(f.read())

    # get new files
    pub_str = ""
    for author in author_list:
        for pub in publication_dict.get(author):
            if pub not in old_publication_dict.get(author):
                pub_str += "{}\n".format(pub.get("publication_date"))
                pub_str += "\t{}\n".format(pub.get("title"))
                pub_str += "\t{}\n".format(author)
                pub_str += "\t{}\n".format(pub.get("doi"))
                pub_str += "\t{}\n\n".format(pub.get("pubmed_id").split("\n")[0])

                # print(pub.get("publication_date"))
                # print("\t{}".format(pub.get("title")))
                # print("\t{}".format(author))
                # print("\t{}".format(pub.get("doi")))
                # print("\t{}".format(pub.get("pubmed_id").split("\n")[0]), end="\n\n")

    if pub_str:
        # create email message
        email_str = create_email_message("Emily", pub_str)
        send_email(
            "New Publications (\"Stalker\" Update)",
            email_str,
            from_email,
            password,
            to_email,
            cc,
        )

        # update the saved publication list
        with open("../data/publications.json", "w") as f:
            f.write(dumps(publication_dict, indent=4))
