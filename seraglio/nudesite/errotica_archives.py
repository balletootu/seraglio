from datetime import datetime
import logging

from seraglio import utils, ModelPage, Gallery
from .metartnetwork import MetArtNetwork


class ErroticaArchives(MetArtNetwork):
    def __init__(self):
        super().__init__(id='errotica-archives')

        self.thenude_dict = {
            'errotica-archives': {
                'start': datetime(2004, 6, 1),
                'end': datetime(9999, 12, 31),
            },
            'erro-arch movies': {
                'start': datetime(2005, 7, 1),
                'end': datetime(9999, 12, 31),
            },
        }

    def _parse_index(self, html):
        return [
            a.attrs['href']
            for a in html.find('a.update_information_model_name')
        ]

    def _parse_model_page(self, html):
        link = html.find('link[rel=canonical]', first=True)
        if link:
            url = link.attrs['href']

        model_id = url.split('/')[4]
        page_id = self.id + '_' + model_id

        model_page = ModelPage(page_id=page_id)

        model_page.url = url
        model_page.site = self.id

        name = html.find('span.set_title > a', first=True)
        if name:
            model_page.name = name.text
        else:
            return None, []

        for li in html.find('div.model_info li'):
            key, value = li.text.split(':')
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()

            if key == 'age_first_shot':
                model_page.age_debut = int(value)
            elif key == 'measurements':
                model_page.size = value
            elif key == 'height':
                height = value.strip('"').split('\'')
                model_page.height = int(
                    (float(height[0]) * 12 + float(height[1])) * 2.54)
            elif key == 'weight':
                model_page.weight = int(float(value.split()[0]) * 0.45359237)
            else:
                setattr(model_page, key, value)

        bio = html.find('div.model_bio', first=True)
        if bio:
            model_page.bio = bio.text.strip()

        try:
            member_rating = html.find('div.options_voting_rating', first=True)
            model_page.member_rating = float(member_rating.text)
        except:
            pass

        try:
            num_ratings = html.find(
                'span.options_voting_score_based', first=True)
            model_page.num_ratings = int(num_ratings.text.split()[2])
        except:
            pass

        galleries = []
        for td in html.find('table.updates_table td'):
            gallery = self._parse_gallery(td)
            if model_page not in gallery.model_pages:
                gallery.model_pages.append(model_page)
            if gallery not in galleries:
                galleries.append(gallery)
                if gallery.type == 'video':
                    if model_page.num_videos:
                        model_page.num_videos += 1
                    else:
                        model_page.num_videos = 1
                else:
                    if model_page.num_photosets:
                        model_page.num_photosets += 1
                    else:
                        model_page.num_photosets = 1
        return model_page, galleries

    def _parse_gallery(self, html):
        image = html.find('a.gallery_image_cell', first=True)
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

        for a in html.find('div.update_information_model_name a'):
            page_id = self.id + '_' + a.attrs['href'].split('/')[4]
            model_page = ModelPage.objects(page_id=page_id).first()
            if model_page:
                gallery.model_pages.append(model_page)

        num_photos = html.find('span.display_gallery_cell_photo', first=True)
        if num_photos:
            gallery.type = 'photoset'
            gallery.num_photos = int(num_photos.text.split()[-2])
        video_length = html.find('span.display_gallery_cell_movie', first=True)
        if video_length:
            gallery.type = 'video'
            gallery.length = video_length.text.split()[-1]

        return gallery

    def _get_latest_model_urls(self, last_date):
        urls = []
        url = self._url + 'archive/triple/'
        r = utils.fetch_url(url)
        if r:
            for div in r.html.find('div.update_information'):
                url = div.find(
                    'a.update_information_gallery_name', first=True,
                ).attrs['href']
                date = datetime.strptime(url.split('/')[6], '%Y%m%d')
                if date < last_date:
                    continue
                for url_div in div.find('div.update_information_model_name a'):
                    url = url_div.attrs['href']
                    if url not in urls:
                        urls.append(url)
        return reversed(urls)

    def get_gallery_download_link(self, gallery):
        if not self.auth:
            return None, None, None
        url = ''
        file_name = ''
        member_url = self._get_gallery_member_url(gallery)
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
