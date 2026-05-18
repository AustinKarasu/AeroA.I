from urllib.request import urlopen
import urllib.parse
import webbrowser
from sys import platform
import os

def open_url(url):
    try:
        webbrowser.open_new_tab(url)
    except Exception:
        webbrowser.open(url)


def youtube(textToSearch):
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    open_url(url)


if __name__ == '__main__':
    youtube('any text')
