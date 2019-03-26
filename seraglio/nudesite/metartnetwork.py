from datetime import datetime
import logging
import string

from seraglio import utils, ModelPage, Gallery
from .nudesite import NudeSite


class MetArtNetwork(NudeSite):
    def __init__(self, id):
        super().__init__(id=id)
        self.auth = None

    def _get_index_urls(self):
        for letter in string.ascii_uppercase:
            yield letter, f'{self._url}models/all/{letter}/'

    def _parse_index(self, html):
        urls = [a.attrs['href'] for a in html.find('a.custom-list-item-name')]
        return urls

    def _get_model_id(self, url):
        return url.split('/')[4]

    def _parse_model_page(self, html):
        link = html.find('link[rel=canonical]', first=True)
        if link:
            url = link.attrs['href']

        model_id = url.split('/')[4]
        page_id = self.id + '_' + model_id

        model_page = ModelPage(page_id=page_id)

        model_page.url = url
        model_page.site = self.id

        name = html.find('h1 > a', first=True)
        if name:
            model_page.name = name.text
        else:
            return None, []

        stats = html.find('div.custom-photo-stats', first=True)
        if stats:
            country = stats.find('span.custom-country', first=True)
            if country:
                model_page.country = country.text
            age_debut = stats.find('span.custom-age', first=True)
            if age_debut:
                model_page.age_debut = int(
                    age_debut.text.split(':')[1].strip())

            num_videos = stats.find(
                'li.custom-photo-details-movies', first=True)
            num_photosets = stats.find(
                'li.custom-photo-details-photos', first=True)
            if num_videos:
                model_page.num_videos = int(num_videos.text)
            if num_photosets:
                model_page.num_photosets = int(num_photosets.text)

        stats = html.find('div.custom-photo-modal-stats', first=True)
        for li in stats.find('li'):
            key, value = li.text.split(':')
            key = key.lower().replace(' ', '_')
            value = value.strip()

            if key == 'height':
                height = value.strip('"').split('\'')
                model_page.height = int(
                    (float(height[0]) * 12 + float(height[1])) * 2.54)
            elif key == 'weight':
                model_page.weight = int(float(value.split()[0]) * 0.45359237)
            else:
                setattr(model_page, key, value)

        bio = html.find('div.custom-modal-model-bio-text', first=True)
        if bio:
            model_page.bio = bio.text.strip()

        try:
            member_rating = html.find(
                'span.custom-activity-rating-average', first=True)
            model_page.member_rating = float(member_rating.text)
        except:
            pass

        try:
            num_ratings = html.find(
                'span.custom-activity-rating-based', first=True)
            num_ratings = num_ratings.find('span > span', first=True)
            model_page.num_ratings = int(num_ratings.text.split()[0])
        except:
            pass

        rows = html.find('div.row.container.custom-content-list')
        galleries = []
        for row in rows:
            h2 = row.find('h2', first=True)
            if h2:
                if h2.text.startswith('Films'):
                    gallery_type = 'video'
                else:
                    gallery_type = 'photoset'
                lis = row.find('li.list-group-item')
                for li in lis:
                    gallery = self._parse_gallery(li)
                    gallery.type = gallery_type
                    if model_page not in gallery.model_pages:
                        gallery.model_pages.append(model_page)
                    galleries.append(gallery)
        return model_page, galleries

    def _parse_gallery(self, html):
        url = html.find(
            'a.custom-list-item-name', first=True).attrs['href']
        splits = url.split('/')
        gallery_id = '_'.join(
            [self.id, splits[6], splits[4], splits[5], splits[7]]).lower()

        gallery = Gallery(gallery_id=gallery_id)

        gallery.url = url
        gallery.site = self.id
        gallery.date = datetime.strptime(splits[6], '%Y%m%d')
        gallery.name = html.find('img.img-responsive', first=True).attrs['alt']

        # member_rating = html.find(
        #     'li.custom-activity-stats-rating', first=True)
        # if member_rating:
        #     gallery.member_rating = float(member_rating.text)

        spans = html.find('span.custom-age')
        for a in spans[1].find('a'):
            page_id = self.id + '_' + a.attrs['href'].split('/')[4]
            model_page = ModelPage.objects(page_id=page_id).first()
            if model_page:
                gallery.model_pages.append(model_page)
        gallery.photographer = spans[2].find(
            'a', first=True).text

        num_photos = html.find('li.custom-photo-details-medias', first=True)
        if num_photos:
            gallery.num_photos = int(num_photos.text)
        video_length = html.find('li.custom-photo-details-runtime', first=True)
        if video_length:
            gallery.length = video_length.text

        return gallery

    def _get_latest_model_urls(self, last_date):
        urls = []
        url = self._url + 'archive/triple/'
        r = utils.fetch_url(url)
        if r:
            for li in r.html.find('li.list-group-item'):
                url = li.find(
                    'div.custom-list-item-detailed-photo a', first=True,
                ).attrs['href']
                date = datetime.strptime(url.split('/')[6], '%Y%m%d')
                if date < last_date:
                    continue
                for a in li.find('a.custom-list-item-name-model'):
                    url = a.attrs['href']
                    if url not in urls:
                        urls.append(url)
        return reversed(urls)

    def _get_gallery_member_url(self, gallery):
        # https://www.metart.com/model/lena-flora/gallery/20190203/EXEMPLARY/
        splits = gallery.url.split('/')
        # https://members.metart.com/members/model/lena-flora/gallery/20190203/EXEMPLARY/
        return f'https://{splits[2].replace("www", "members")}/members/' \
            f'model/{splits[4]}/gallery/{splits[6]}/{splits[7]}/'

    def get_gallery_download_link(self, gallery):
        if not self.auth:
            return None, None, None
        url = ''
        file_name = ''
        member_url = self._get_gallery_member_url(gallery)
        r = utils.fetch_url(member_url, auth=self.auth)
        if not r:
            return None, None, None
        url = r.html.find('ul.custom-download-menu a')[0].attrs['href']
        if not url:
            logging.warning(f'parsing {self.member_url} failed')
        if gallery.type == 'photoset':
            file_name = gallery.id + '.zip'
        else:
            file_name = gallery.id + '.mp4'
        return url, self.auth, file_name
