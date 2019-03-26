from datetime import datetime
import logging

from seraglio import utils, Gallery, ModelPage
from .metartnetwork import MetArtNetwork
from .errotica_archives import ErroticaArchives


class Stunning18(ErroticaArchives):
    def __init__(self):
        MetArtNetwork.__init__(self, id='stunning18')

        self.thenude_dict = {
            'stunning18': {
                'start': datetime(2013, 1, 1),
                'end': datetime(9999, 12, 31),
            },
        }

        self.auth = None

    def _parse_gallery(self, html):
        image = html.find('a', first=True)
        url = image.attrs['href']

        splits = url.split('/')
        gallery_id = '_'.join(
            [self.id, splits[6], splits[4], splits[5], splits[7]]).lower()

        gallery = Gallery(gallery_id=gallery_id)
        gallery.url = url
        gallery.site = self.id
        gallery.date = datetime.strptime(splits[6], '%Y%m%d')
        gallery.name = image.find('img', first=True).attrs['alt']

        # member_rating = html.find(
        #     'li.custom-activity-stats-rating', first=True)
        # if member_rating:
        #     gallery.member_rating = float(member_rating.text)

        for a in html.find('span[itemprop=actor] a'):
            page_id = gallery.site + '_' + a.attrs['href'].split('/')[4]
            model_page = ModelPage.objects(page_id=page_id).first()
            if model_page:
                gallery.model_pages.append(model_page)

        splits = html.find('ul.hover_container_stats li')[2].text.split(' ')
        logging.debug(f'{splits}')
        if len(splits) > 1:
            if splits[1] == 'Photos':
                gallery.type = 'photoset'
                gallery.num_photos = int(splits[0])
            else:
                gallery.type = 'video'
                gallery.length = splits[1]

        gallery.photographer = 'Antonio Clemens'

        return gallery

    def _get_latest_model_urls(self, last_date):
        urls = []
        url = self._url + 'archive/triple/'
        r = utils.fetch_url(url)
        if r:
            for div in r.html.find('div.update_cell'):
                url = div.find(
                    'a.hover_container_title', first=True,
                ).attrs['href']
                date = datetime.strptime(url.split('/')[6], '%Y%m%d')
                if date < last_date:
                    continue
                for a in div.find('span[itemprop=actor] a'):
                    url = a.attrs['href']
                    if url not in urls:
                        urls.append(url)
        return reversed(urls)
