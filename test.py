from stalker.webio import request_publications
from urllib.request import urlopen
from urllib.error import HTTPError
from os.path import join
from urllib.parse import urlparse


if __name__ == "__main__":

    pubs = request_publications(["Christian Powell"])
    pub_med_url = "https://pubmed.ncbi.nlm.nih.gov/"
    grant_numbers = ("P42ES007380", "P42 ES007380")
    doi_url = "https://doi.org/"

    with_grant = dict()
    without_grant = dict()
    with_error = dict()

    for pub_id in pubs:

        print(pubs[pub_id])
        exit()
        response = urlopen(join(pub_med_url, pub_id))
        url_str = response.read().decode("utf-8")
        response.close()

        # if grant number is on PubMed
        if any(grant_id in url_str for grant_id in grant_numbers):
            with_grant[pub_id] = pubs[pub_id]

        # else, look for grant number with DOI
        else:
            try:
                response = urlopen(join(doi_url, pubs[pub_id][1]["doi"]))
                url_str = response.read().decode("utf-8")
                response.close()

                if any(grant_id in url_str for grant_id in grant_numbers):
                    with_grant[pub_id] = pubs[pub_id]

                else:
                    # manually check later
                    without_grant[pub_id] = pubs[pub_id]

            except HTTPError as e:
                print(join(doi_url, pubs[pub_id][1]["doi"]))
                with_error[pub_id] = pubs[pub_id]

            except Exception as e:
                print(pub_id, e)
