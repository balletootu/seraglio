from datetime import datetime
import logging

from seraglio import utils
from .metartnetwork import MetArtNetwork
from .stunning18 import Stunning18


class EternalDesire(Stunning18):
    def __init__(self):
        MetArtNetwork.__init__(self, id='eternaldesire')

        self.thenude_dict = {
            'eternaldesire': {
                'start': datetime(2013, 2, 1),
                'end': datetime(9999, 12, 31),
            },
        }

        self.auth = None

    def _parse_gallery(self, html):
        gallery = super()._parse_gallery(html)
        gallery.photographer = 'Arkisi'
        return gallery
