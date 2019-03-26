from datetime import datetime
from .metartnetwork import MetArtNetwork


class MetArt(MetArtNetwork):
    def __init__(self):
        super().__init__(id='metart')

        self.thenude_dict = {
            'metart': {
                'start': datetime(2004, 1, 1),
                'end': datetime(9999, 12, 31),
            },
            'metmovies': {
                'name': 'metart',
                'start': datetime(2004, 1, 1),
                'end': datetime(9999, 12, 31),
            },
            'metart archives': {
                'name': 'metart',
                'start': datetime(1999, 8, 1),
                'end': datetime(2003, 12, 31),
            },
        }
