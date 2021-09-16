from stalker.create_author_list import project_4
from stalker.webio import request_publications
from collections import OrderedDict
from urllib.request import urlopen
from urllib.error import HTTPError
from os.path import join

from stalker.create_author_list import project_1, project_2, project_3, project_4, BEACC


# project 1
project_1_leaders = {"Bernhard Hennig"}

# project 2
project_2_leaders = {"Kevin Pearson", "Hollie Swanson"}

# project 3
project_3_leaders = {"Dibakar Bhattacharyya", "Zach Hilt", "Lindell Ormsbee", "Isabel Escobar", "Tom Dziubla", "T John Balk"}

# project 4
project_4_leaders = {"Kelly Pennell", "Anna Hoover"}

beacc = {"Andrew Morris"}


def create_citation(publication):
    """

    :param publication:
    :return:
    """
    publication_str = ""

    publication_str += ", ".join([auth["lastname"] + " " + auth["initials"] for auth in publication[1]["authors"]]) + "."
    publication_str += " {}.".format(publication[1]["publication_date"][:4])
    publication_str += " {}.".format(publication[1]["title"])
    publication_str += " {}.".format(publication[1]["journal"])
    publication_str += " {}".format(publication[1]["doi"])
    publication_str += " PMID:{}".format(publication[1]["pubmed_id"].split("\n")[0])

    return publication_str


if __name__ == "__main__":

    pub_med_url = "https://pubmed.ncbi.nlm.nih.gov/"
    grant_numbers = ("P42ES007380", "P42 ES007380")
    doi_url = "https://doi.org/"
    citations = list()

    # author_list = [author for author in project_4]
    for author in {"Andrew Morris"}:

        author_list = [author]
        for member in BEACC.keys():
            if BEACC[member].get("mentor(s)"):
                if author in BEACC[member].get("mentor(s)"):
                    author_list.append(member)

        # author_list = ["Kelly Pennell", "Ying Li", "Sweta Ojha", "Nader Rezaei", "Ariel Robinson", "Hong Cheng Tay"]
        print(author_list)
        publication_dict = request_publications(author_list)

        publication_dict = OrderedDict(sorted(publication_dict.items(), key=lambda x: x[1][1]["publication_date"], reverse=True))

        for pub_id in publication_dict:

            response = urlopen(join(pub_med_url, pub_id))
            url_str = response.read().decode("utf-8")
            response.close()

            # if grant number is on PubMed
            if any(grant_id in url_str for grant_id in grant_numbers):
                citations.append(create_citation(publication_dict[pub_id]))
                print(create_citation(publication_dict[pub_id]))

            # else, look for grant number with DOI
            else:
                print()
                print(pub_id)
                print()

        print()
        print()
                # try:
                #     response = urlopen(join(doi_url, pubs[pub_id][1]["doi"]))
                #     url_str = response.read().decode("utf-8")
                #     response.close()
                #
                #     if any(grant_id in url_str for grant_id in grant_numbers):
                #         with_grant[pub_id] = pubs[pub_id]
                #
                #     else:
                #         # manually check later
                #         without_grant[pub_id] = pubs[pub_id]
                #
                # except HTTPError as e:
                #     print(join(doi_url, pubs[pub_id][1]["doi"]))
                #     with_error[pub_id] = pubs[pub_id]
                #
                # except Exception as e:
                #     print(pub_id, e)
