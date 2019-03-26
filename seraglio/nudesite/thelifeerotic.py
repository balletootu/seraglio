from datetime import datetime
from .metartnetwork import MetArtNetwork


class TheLifeErotic(MetArtNetwork):
    def __init__(self):
        super().__init__(id='thelifeerotic')

        self.thenude_dict = {
            'thelifeerotic': {
                'start': datetime(2009, 5, 1),
                'end': datetime(9999, 12, 31),
            },
        }
