from datetime import datetime

from seraglio import utils, Gallery, ModelPage
from .nudesite import NudeSite


class MPLStudios(NudeSite):
    def __init__(self):
        super().__init__(id='mplstudios')

        self.thenude_dict = {
            'mplstudios': {
                'start': datetime(2003, 9, 1),
                'end': datetime(9999, 12, 31),
            },
        }

        self.auth = None

    def _get_index_urls(self):
        yield 'studio_girls', 'https://www.mplstudios.com/studio_girls/'

    def _parse_index(self, html):
        urls = []
        options = html.find('select.select[name="modelSearch"] > option')
        for option in options[1:]:
            model_id = option.attrs['value']
            url = f'https://www.mplstudios.com/portfolio/{model_id}/'
            urls.append(url)
        return reversed(urls)

    def _get_model_id(self, url):
        return url.split('/')[4]

    def _parse_model_page(self, html):
        option = html.find(
            'select.select[name="modelSearch"] > option[SELECTED]')[1]
        model_id = option.attrs['value']
        page_id = self.id + '_' + model_id

        model_page = ModelPage(page_id=page_id)

        model_page.url = f'https://www.mplstudios.com/portfolio/{model_id}/'
        model_page.site = self.id

        model_page.name = html.find('div#current_m > h2', first=True).text

        stats = html.find('div#details', first=True).text.split('\n')
        for line in stats:
            splits = line.split(': ')
            if len(splits) != 2:
                continue
            key, value = splits
            if key == 'Country':
                model_page.country = value
            elif key == 'Eyes':
                model_page.eye_color = value
            elif key == 'Photo Series':
                model_page.num_photosets = int(value)
            elif key == 'Videos':
                model_page.num_videos = int(value)

        bio = html.find('div#model_text', first=True)
        if bio:
            model_page.bio = bio.text.strip()

        try:
            member_rating = html.find('div#vote_bin > b.sand')[1]
            model_page.member_rating = float(member_rating.text.split('/')[0])
        except:
            pass

        galleries = []

        for div in html.find('div#update_covers > div.u_bin'):
            gallery = self._parse_gallery(div)
            gallery.model_pages.append(model_page)
            galleries.append(gallery)

        return model_page, galleries

    def _parse_gallery(self, html):
        rel_url = html.find('a', first=True).attrs['href'][1:]
        gallery_id = '_'.join([self.id, rel_url.split('/')[1]])

        gallery = Gallery(gallery_id=gallery_id)

        gallery.url = self._url + rel_url
        gallery.site = self.id
        gallery.name = html.find('div.u_text i', first=True).text[1:-1]

        text = html.find('div.u_text', first=True).text
        if 'v' in gallery.id:
            gallery.type = 'video'
        else:
            gallery.type = 'photoset'
        gallery.date = self._parse_date(text.split('\n')[0])
        gallery.photographer = html.find('a.phol', first=True).text

        return gallery

    def _parse_date(self, date):
        '''December 27th 2018'''
        import re
        s = re.sub(r'(\d)(st|nd|rd|th)', r'\1', date)
        return datetime.strptime(s, '%B %d %Y')

    def _get_latest_model_urls(self, last_date):
        urls = []
        url = 'https://www.mplstudios.com/updates/'
        r = utils.fetch_url(url)
        if r:
            for div in r.html.find('div#update_covers div.u_bin'):
                date = div.find('div.u_text u', first=True).text
                if len(date.split(' ')) == 3:
                    date = self._parse_date(date)
                else:
                    date = datetime(9999, 12, 31)
                if date < last_date:
                    continue
                rel_url = div.find('a.phol', first=True).attrs['href']
                if rel_url.split('/')[1] == 'portfolio':
                    url = f'https://www.mplstudios.com{rel_url}'
                    urls.append(url)
                if url not in urls:
                    urls.append(url)
        return reversed(urls)

    def _get_gallery_member_url(self, gallery):
        return gallery.url

    def get_gallery_download_link(self, gallery, auth=None):
        url = ''
        file_name = ''
        member_url = self._get_gallery_member_url(gallery)
        r = utils.fetch_url(member_url, auth=self.auth)
        exts = ['.zip', '.mp4', '.mov']
        for a in r.html.find('div#links a'):
            url = 'https://www.mplstudios.com' + a.attrs['href']
            for ext in exts:
                if url.endswith(ext):
                    file_name = gallery.id + ext
                    break
            if file_name:
                break
        return url, self.auth, file_name
