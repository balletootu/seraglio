from datetime import datetime
from .metartnetwork import MetArtNetwork


class VivThomas(MetArtNetwork):
    def __init__(self):
        super().__init__(id='vivthomas')

        self.thenude_dict = {
            'vivthomas': {
                'start': datetime(2004, 1, 1),
                'end': datetime(9999, 12, 31),
            },
            'vivthomas video': {
                'start': datetime(1999, 9, 1),
                'end': datetime(9999, 12, 31),
            },
        }
