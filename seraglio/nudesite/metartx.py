from datetime import datetime
import logging

from seraglio import utils
from .metartnetwork import MetArtNetwork


class MetArtX(MetArtNetwork):
    def __init__(self):
        super().__init__(id='metartx')

        self.thenude_dict = {
            'metart-x': {
                'start': datetime(2016, 3, 1),
                'end': datetime(9999, 12, 31),
            },
        }

        self.auth = None

    def _get_gallery_member_url(self, gallery):
        splits = gallery.url.split('/')
        return f'https://{splits[2].replace("www", "v2")}/members/' \
            f'model/{splits[4]}/gallery/{splits[6]}/{splits[7]}/'

    def get_gallery_download_link(self, gallery):
        if not self.auth:
            return None, None, None
        url = ''
        member_url = self._get_gallery_member_url(gallery)
        r = utils.fetch_url(member_url, auth=self.auth)
        url = r.html.find('ul.dropdown-menu a')[0].absolute_links[0]
        if not url:
            logging.warning(f'parsing {gallery.member_url} failed')
        if gallery.type == 'photoset':
            file_name = gallery.id + '.zip'
        else:
            file_name = gallery.id + '.mp4'
        return url, self.auth, file_name
