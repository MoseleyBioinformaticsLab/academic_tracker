from email.message import EmailMessage
from pymed import PubMed
import smtplib
import ssl
from time import sleep


def request_publications(author_list, cutoff_date=2019):
    """Returns a dictionary of authors (key) and lists of their publications (values).

    Args:
        author_list (list): list of author names to search PubMed with.
        cutoff_date (int): YYYY year before which publications will be discarded.
    
    Returns:
        publication_dict (dict): author names are keys and publication ids are values

    """
    # initiate PubMed API
    pubmed = PubMed(tool="Stalker", email="christian.powell@uky.edu")

    publication_dict = dict()

    # loop through list of authors and request a list of their publications
    for author in author_list:
        publications = pubmed.query(author, max_results=500)
        for pub in publications:
            if any(["kentucky" in str(author_items.get("affiliation")).lower() for author_items in pub.authors]):
                pub_dict = pub.toDict()
                del pub_dict["xml"]
                pub_dict["publication_date"] = str(pub_dict["publication_date"])

                if int(pub_dict["publication_date"][:4]) >= cutoff_date:

                    # add publications to the publication_dict if not there, else add author to the publication.
                    # author is a dict so that authors are not repeated.
                    if not pub_dict.get("pubmed_id").split("\n")[0] in publication_dict.keys():
                        publication_dict[pub_dict.get("pubmed_id").split("\n")[0]] = [{author}, pub_dict]
                    else:
                        publication_dict[pub_dict.get("pubmed_id").split("\n")[0]][0].add(author)

        # don't piss off NCBI
        sleep(1)

    # convert author dict to list, it was only a dict to get unique names easily.
    for key in publication_dict.keys():
        publication_dict[key][0] = list(publication_dict[key][0])

    return publication_dict


def check_grant_number(publication, pubmed_url="https://pubmed.ncbi.nlm.nih.gov/",
                       grant_numbers=("P42ES007380", "P42 ES007380"), doi_url="https://doi.org/"):
    pass


def create_email_message(to_name, publication_str):
    """Create a string for the body of an email to send to an author.
    
    Args:
        to_name (str): author's name
        publication_str (str): string that has all the publications to alert the author about
        
    Returns:
        message (str): string with a formatted message meant to be the body of an email to the author

    """
    message = """Hey {},
    
Here is your weekly dose of publications I've been able to find.



{}
Kind regards,

This email was sent by an automated service. If you have any questions or concerns please email my creator (christian.powell@uky.edu). 
Beep, boop.""".format(to_name, publication_str)
    return message


def send_email(subject,
               message,
               from_email=None,
               password=None,
               to_email=None,
               cc=None,
               smtp_server_address="smtp.gmail.com",
               port=587):
    """Sends an email via SMTP.

    :param subject:
    :param message:
    :param from_email:
    :param password:
    :param to_email:
    :param cc:
    :param smtp_server_address:
    :param port:
    :return:
    """

    context = ssl.create_default_context()

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg['CC'] = cc
    msg.set_content(message)

    # Send the message via SMTP server.
    try:
        with smtplib.SMTP(smtp_server_address, port) as server:
            server.starttls(context=context)
            server.login(from_email, password)
            server.send_message(msg)
            server.quit()
    except Exception as e:
        raise e
