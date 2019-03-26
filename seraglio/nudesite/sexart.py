from datetime import datetime
from .metartnetwork import MetArtNetwork


class SexArt(MetArtNetwork):
    def __init__(self):
        super().__init__(id='sexart')

        self.thenude_dict = {
            'sexart': {
                'start': datetime(2012, 4, 1),
                'end': datetime(9999, 12, 31),
            },
            'sexart video': {
                'start': datetime(2012, 3, 1),
                'end': datetime(9999, 12, 31),
            },
        }
