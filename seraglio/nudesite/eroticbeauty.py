from datetime import datetime
from .metartnetwork import MetArtNetwork


class EroticBeauty(MetArtNetwork):
    def __init__(self):
        super().__init__(id='eroticbeauty')

        self.thenude_dict = {
            'eroticbeauty': {
                'start': datetime(2005, 5, 1),
                'end': datetime(9999, 12, 31),
            },
            # 'metmodels': {
            #     'start': datetime(2005, 5, 1),
            #     'end': datetime(2012, 2, 1),
            # },
            # 'metgirls': {
            #     'start': datetime(2002, 1, 1),
            #     'end': datetime(2005, 2, 1),
            # },
        }
