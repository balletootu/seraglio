import logging
import time

import requests_html


class PrettyPrint:
    def __repr__(self):
        # attrs = [f'{type(self).__name__} {{']
        # for name in self._fields.keys():
        #     value = getattr(self, name)
        #     attrs.append(f'    {name.__repr__()}: {value.__repr__()},')
        # attrs.append('}')
        # return '\n'.join(attrs)
        return f'{type(self).__name__}({self.id})'

    def __str__(self):
        return self.__repr__()

    def __format__(self, fmt):
        return self.__repr__()


def load_html_file(path):
    with open(path) as f:
        html = requests_html.HTML(html=f.read())
    return html


html_session = requests_html.HTMLSession()


def fetch_url(url, auth=None):
    r = None
    try:
        r = html_session.get(url, allow_redirects=True, auth=auth)
    except:
        logging.warning('Failed url: {}'.format(url))
        # return None
    # time.sleep(1)
    return r


def fetch_url_head(url, auth=None):
    r = None
    try:
        r = html_session.head(url, allow_redirects=True, auth=auth)
    except:
        logging.warning('Failed url: {}'.format(url))
        return None
    return r


def get_redirected_url(url, auth=None):
    try:
        r = html_session.head(url, allow_redirects=True, auth=auth)
    except:
        logging.warning('Failed url: {}'.format(url))
        return None
    return r.url
