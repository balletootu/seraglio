from datetime import datetime
import logging

from seraglio import utils
from .metartnetwork import MetArtNetwork
from .errotica_archives import ErroticaArchives


class RylskyArt(ErroticaArchives):
    def __init__(self):
        MetArtNetwork.__init__(self, id='rylskyart')

        self.thenude_dict = {
            'rylsky art': {
                'start': datetime(2012, 9, 1),
                'end': datetime(9999, 12, 31),
            },
        }

        self.auth = None

    def _parse_gallery(self, html):
        gallery = super()._parse_gallery(html)
        gallery.photographer = 'Rylsky'
        return gallery

    def get_gallery_download_link(self, gallery):
        if not self.auth:
            return None, None, None
        url = ''
        file_name = ''
        member_url = self._get_gallery_member_url(gallery)
        logging.debug(self.auth)
        r = utils.fetch_url(member_url, auth=self.auth)
        if not r:
            logging.error(
                f'failed to get download link of {gallery.id}')
            return None, None, None
        if gallery.type == 'photoset':
            url = r.html.find('div.gallery_zip_download a')[0].attrs['href']
            file_name = gallery.id + '.zip'
        else:
            url = r.html.find('ul.downloading_options_list a')[0].attrs['href']
            file_name = gallery.id + '.mp4'
        if not url:
            logging.error(
                f'failed to parse download link of {gallery.id}')
        return url, self.auth, file_name
