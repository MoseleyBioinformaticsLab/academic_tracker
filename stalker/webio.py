from email.message import EmailMessage
from pymed import PubMed
import smtplib
import ssl
from time import sleep


def request_publications(author_list):
    """Returns a dictionary of authors (key) and lists of their publications (values).

    :param author_list:
    :type author_list: list
    :return: Dictionary of authors (key) and lists of their publications (values)
    :rtype: dict
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

                if not pub_dict.get("pubmed_id").split("\n")[0] in publication_dict.keys():
                    publication_dict[pub_dict.get("pubmed_id").split("\n")[0]] = [{author}, pub_dict]
                else:
                    publication_dict[pub_dict.get("pubmed_id").split("\n")[0]][0].add(author)

        # don't piss off NCBI
        sleep(5)

    for key in publication_dict.keys():
        publication_dict[key][0] = list(publication_dict[key][0])

    return publication_dict


def create_email_message(to_name, publication_str):
    """

    :param to_name:
    :param publication_str:
    :return:
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
               stmp_server_address="smtp.gmail.com",
               port=587):
    """Sends an email via SMTP.

    :param subject:
    :param message:
    :param from_email:
    :param password:
    :param to_email:
    :param cc:
    :param stmp_server_address:
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
        with smtplib.SMTP(stmp_server_address, port) as server:
            server.starttls(context=context)
            server.login(from_email, password)
            server.send_message(msg)
            server.quit()
    except Exception as e:
        raise e
