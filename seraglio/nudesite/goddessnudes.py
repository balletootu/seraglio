from datetime import datetime
from .metartnetwork import MetArtNetwork


class GoddessNudes(MetArtNetwork):
    def __init__(self):
        super().__init__(id='goddessnudes')

        self.thenude_dict = {
            'goddessnudes': {
                'start': datetime(2009, 10, 1),
                'end': datetime(9999, 12, 31),
            },
        }

    def _get_gallery_member_url(self, gallery):
        splits = gallery.url.split('/')
        return f'https://{splits[2].replace("www", "m.members")}/members/' \
            f'model/{splits[4]}/gallery/{splits[6]}/{splits[7]}/'
