import unicodedata
import urllib
from lxml import html
import requests


def to_str(to_convert):
    """
    Converts a value from the webpage to a string, accounting for the fact that it may be unicode
    :rtype: str
    :param to_convert: the value to be converted
    :return: a string representation of the param
    """
    try:
        return str(to_convert)
    except UnicodeEncodeError:
        return unicodedata.normalize('NFKD', to_convert).encode('ascii', 'ignore')


def encode(string):
    """
    Encodes a string to be used as a url
    :rtype: str
    :type string: str
    :param string: a string to be encoded as a url
    :return: encoded param
    """
    return urllib.quote(string, safe='')


def get_page(url):
    """
    Returns a page retreived from the URL in a format that is usable by the LXML classes
    :type url: str
    """
    content = requests.get(url).content
    return html.fromstring(content)


def join_list_unicode_strings(unicode_list):
    """
    :type unicode_list: list
    """
    output = ""
    for each in unicode_list:
        output += to_str(each)
    return output
