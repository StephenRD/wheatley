"""
A module to store functions related to parsing the HTML of the Ringing Room tower pages to find
things like the load-balanced URL of the socket-io server.
"""

import urllib

import requests


class TowerNotFoundError(ValueError):
    """ An error class created whenever the user inputs an incorrect room id. """

    def __init__(self, tower_id, url):
        super().__init__()
        self._id = tower_id
        self._url = url

    def __str__(self):
        return f"Tower {self._id} not found at '{self._url}'."

class InvalidURLError(Exception):
    """ An error class created whenever the user inputs a URL that is invalid. """

    def __init__(self, url):
        super().__init__()
        self._url = url

    def __str__(self):
        return f"Unable to make a connection to '{self._url}'."


def fix_url(url):
    """ Add 'https://' to the start of a URL if necessary """

    if not url.startswith("http"):
        return "https://" + url

    return url


def get_load_balancing_url(tower_id, http_server_url):
    """
    Get the URL of the socket server which (since the addition of load balancing) is not
    necessarily the same as the URL of the http server that people will put into their browser URL
    bars.
    """

    # Trying to extract the following line in the rendered html:
    # server_ip: "{{server_ip}}"
    # See https://github.com/lelandpaul/virtual-ringing-room/blob/
    #     ec00927ca57ab94fa2ff6a978ffaff707ab23a57/app/templates/ringing_room.html#L46
    url = urllib.parse.urljoin(http_server_url, str(tower_id))

    try:
        html = requests.get(url).text
    except requests.exceptions.ConnectionError:
        raise InvalidURLError(http_server_url)

    try:
        url_start_index = html.index("server_ip") + len('server_ip: "')
        string_that_starts_with_url = html[url_start_index:]
        load_balancing_url = string_that_starts_with_url[:string_that_starts_with_url.index('"')]

        return load_balancing_url
    except ValueError:
        raise TowerNotFoundError(tower_id, http_server_url)
