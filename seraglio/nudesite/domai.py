from datetime import datetime
from .metartnetwork import MetArtNetwork


class Domai(MetArtNetwork):
    def __init__(self):
        super().__init__(id='domai')

        self.thenude_dict = {
            'domai': {
                'start': datetime(1998, 11, 1),
                'end': datetime(9999, 12, 31),
            },
        }

    def _get_gallery_member_url(self, gallery):
        splits = gallery.url.split('/')
        return f'https://{splits[2].replace("www", "m.members")}/members/' \
            f'model/{splits[4]}/gallery/{splits[6]}/{splits[7]}/'
