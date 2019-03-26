from datetime import datetime
import glob
import logging
import os

import mongoengine
from mongoengine import Document, StringField, DateTimeField, IntField, \
    ListField, DictField, BooleanField, ReferenceField

from .gallery import Gallery
from .model_page import ModelPage
from .model import Model
from .nudesite import NudeSite, get_site, sites
from seraglio import utils
from .utils import PrettyPrint


class TheNudeGallery(PrettyPrint, Document):
    cover_id = StringField(primary_key=True)
    official_gallery = ReferenceField(Gallery,
                                      reverse_delete_rule=mongoengine.NULLIFY)
    url = StringField()
    site = StringField(required=True)
    date = DateTimeField()
    name = StringField()
    model_urls = ListField(StringField())
    icgids = ListField(StringField())
    model_names = ListField(StringField())
    photographer = StringField()
    removed = BooleanField(default=False)

    def update_save(self, *args, **kwargs):
        other = TheNudeGallery.objects(cover_id=self.cover_id).first()
        if other:
            for key in ['official_gallery']:
                value = getattr(other, key)
                if value:
                    setattr(self, key, value)
        self.save(*args, **kwargs)


class TheNudePage(Document, PrettyPrint):
    icgid = StringField(primary_key=True)
    name = StringField(required=True)
    url = StringField(required=True)

    birth_date = StringField()
    country = StringField()

    eye_color = StringField()
    hair_color = StringField()
    height = IntField()
    weight = IntField()

    breasts = StringField()
    size = StringField()
    shaved = StringField()
    ethnicity = StringField()

    official_site = StringField()
    interviews = ListField(StringField())
    social_media = ListField(StringField())
    agencies = ListField(StringField())
    activities = ListField(StringField())

    site_names = DictField()
    links = ListField(StringField())

    def update_save(self, *args, **kwargs):
        # other = TheNudePage.objects(icgid=self.icgid).first()
        # if other:
        #     for key in ['official_gallery']:
        #         value = getattr(other, key)
        #         if value:
        #             setattr(self, key, value)
        self.save(*args, **kwargs)

    @property
    def file_name(self):
        return self.url.split('/')[3].replace('.htm', '.html')

    @property
    def model_id(self):
        return self.url.split('_')[1].split('.htm')[0]


class TheNude(NudeSite):
    def __init__(self):
        super().__init__(id='thenude')
        self.hostname = 'www.thenude.eu'
        self._url = 'https://www.thenude.eu/'
        self.index_dir = os.path.join(self.root_dir, 'covers')
        self.gallery_page_dir = os.path.join(self.root_dir, 'covers')

        self.thenude_site_dict = dict()
        for site in sites:
            for thenude_site in site.thenude_dict:
                self.thenude_site_dict[thenude_site] = site.id

    def update(self, site=None, last_date=None, fetch=True):
        if site:
            self._update_site(site, last_date, fetch=fetch)
        else:
            for site in sites:
                self._update_site(site, last_date, fetch=fetch)

    def rebuild(self, site=None, fetch=True):
        min_date = datetime(1998, 1, 1)
        if site:
            self._update_site(site, last_date=min_date, fetch=fetch)
        else:
            for site in sites:
                self._update_site(site, last_date=min_date, fetch=fetch)

    def _update_site(self, site, last_date, fetch=True):
        if isinstance(site, str):
            site = get_site(site)
        if not last_date:
            last_date = self._get_last_date(site)
        elif isinstance(last_date, str):
            last_date = datetime.strptime(last_date, '%Y-%m-%d')
        today = datetime.today()

        for thenude_site in site.thenude_dict:
            start_date = site.thenude_dict[thenude_site]['start']
            end_date = site.thenude_dict[thenude_site]['end']

            if fetch:
                for date in self._year_month_range(last_date, today):
                    if date < start_date:
                        continue
                    if date > end_date:
                        break
                    for cover in self._get_galleries(
                            thenude_site, date.year, date.month):
                        self._update_cover(cover)
            else:
                thenude_site_id = thenude_site.replace(' ', '-')
                paths = glob.glob(os.path.join(
                    self.index_dir, f'{thenude_site_id}_*.html'))
                for path in sorted(paths):
                    logging.info(path)
                    html = utils.load_html_file(path)
                    for cover in self._parse_gallery_page(html):
                        self._update_cover(cover)

    def _get_last_date(self, site):
        gallery = TheNudeGallery.objects(
            site=site.id).order_by('-date').first()
        if gallery:
            return gallery.date
        else:
            return datetime(1998, 1, 1)

    def _year_month_range(self, start, end):
        year = start.year
        month = start.month
        date = datetime(year, month, 1)
        while date <= end:
            yield date
            month += 1
            if month > 12:
                month = 1
                year += 1
            date = datetime(year, month, 1)

    def _get_galleries(self, thenude_site, year, month):
        r = self._fetch_gallery_page(thenude_site, year, month)
        if r:
            return self._parse_gallery_page(r.html)
        else:
            return []

    def _fetch_gallery_page(self, thenude_site, year, month):
        thenude_site_id = thenude_site.replace(' ', '-')
        url = 'https://www.thenude.eu/covers/' \
            f'{thenude_site_id}/{year}/{month:02}/'
        logging.info(url)
        r = utils.fetch_url(url)
        if r:
            if not os.path.exists(self.gallery_page_dir):
                os.makedirs(self.gallery_page_dir)
            path = os.path.join(self.gallery_page_dir,
                                f'{thenude_site_id}_{year}-{month:02}.html')
            with open(path, 'wb') as f:
                f.write(r.content)
        return r

    def _parse_gallery_page(self, html):
        for div in html.find('div.col-xxs-6'):
            yield self._parse_gallery(div)

    def _parse_gallery(self, html):
        cover = TheNudeGallery()
        date = html.find('div.date', first=True)
        if date:
            cover.date = self._parse_date(date.text)
        for a in html.find('a.model-title'):
            cover.model_urls.append(a.attrs['href'])
            cover.icgids.append(a.attrs['title'].split('ICGID: ')[1])
        for div in html.find('div.model-name'):
            if div.text.startswith('as'):
                cover.model_names = div.text[3:].split(' & ')
            elif div.text.startswith('in'):
                cover.name = div.text[4:-1]
        photographer = html.find('div[itemprop=author]', first=True)
        if photographer:
            cover.photographer = photographer.text
        website = html.find('div.website', first=True)
        if website:
            cover.site = self.thenude_site_dict[website.text.lower()]
        url = html.find('a[itemprop=url]', first=True)
        if url:
            cover.url = url.attrs['href']
            cover.id = '_'.join(url.attrs['href'].split('/')[-3:])
        else:
            logging.error(f'failed to parse {cover.site}')

        if html.find('img.withdrawn', first=True):
            cover.removed = True

        return cover

    def _parse_date(self, date):
        '''1 January 2004'''
        return datetime.strptime(date, '%d %B %Y')

    def _get_model_id(self, url):
        return url.split('/')[3].split('.')[0]

    def _parse_model_page(self, html):
        thenude_page = TheNudePage(icgid='')

        link = html.find('link[rel=canonical]', first=True)
        if link:
            thenude_page.url = link.attrs['href']

        name = html.find('h1.navbar-model-name > span.model-name', first=True)
        if name:
            thenude_page.name = name.text

        for bio in html.find('ul.bio-list > li'):
            key_value = bio.text.split(':')
            key = key_value[0].strip()
            value = key_value[1].strip()
            if key == 'ICGID':
                thenude_page.icgid = value
            elif key.startswith('Born'):
                fmt = key.split('[')[1].split(']')[0]
                d = dict(yyyy='????', mm='??', dd='??')
                splits = value.split('-')
                if len(splits) == 3:
                    for k, v in zip(fmt.split('-'), splits):
                        d[k] = v
                elif len(splits) == 1 and splits[0] == 4:
                    d['yyyy'] = splits[0]
                thenude_page.birth_date = d['yyyy'] + '-' + d['mm'] + '-' + d[
                    'dd']
            elif key == 'Birthplace':
                thenude_page.country = value
            elif key == 'Official Site':
                official_site = bio.find('a', first=True)
                if official_site:
                    url = official_site.attrs['href']
                    thenude_page.official_site = url
            elif key == 'Interviews':
                for item in bio.find('a'):
                    thenude_page.interviews.append(item.attrs['href'])
            elif key == 'Social Media':
                for item in bio.find('a'):
                    thenude_page.social_media.append(item.attrs['href'])
            elif key == 'Agencies':
                for item in bio.find('a'):
                    thenude_page.agencies.append(item.attrs['href'])
            elif key == 'Activities':
                thenude_page.activities = value.split(', ')

        site_names = dict()
        for li in html.find('div.essentials ul.model-model-links li'):
            for link in li.links:
                if link not in thenude_page.links:
                    thenude_page.links.append(link)
            splits = li.text.split('(')
            if len(splits) < 2:
                continue
            thenude_site = splits[0].strip().lower()
            splits = splits[1].split(')')
            if len(splits) < 2:
                continue
            model_names = splits[0].strip().split(' & ')
            if thenude_site in self.thenude_site_dict:
                site = self.thenude_site_dict[thenude_site]
            else:
                site = thenude_site.replace('.', '')
            if site not in site_names:
                site_names[site] = []
            for name in model_names:
                if name not in site_names[site]:
                    site_names[site].append(name)
        thenude_page.site_names = site_names

        return thenude_page, None

    def find_official_gallery(self, cover):
        # based on model names
        gallery_ids1 = set()
        model_pages = list(ModelPage.objects(
            site=cover.site,
            name__in=cover.model_names,
        ))
        for gallery in Gallery.objects(
            site=cover.site,
            date=cover.date,
            model_pages__all=model_pages,
        ):
            gallery_ids1.add(gallery.id)

        # based on gallery name
        logging.debug('galleries by name:')
        gallery_ids2 = set()
        for gallery in Gallery.objects(
            site=cover.site,
            date=cover.date,
            name__iexact=cover.name,
        ):
            gallery_ids2.add(gallery.id)

        intersection = gallery_ids1.intersection(gallery_ids2)
        if len(intersection) == 1:
            gallery_id = intersection.pop()
        else:
            union = gallery_ids1.union(gallery_ids2)
            if len(union) == 1:
                gallery_id = union.pop()
            else:
                gallery_id = None

        if gallery_id:
            return Gallery.objects(gallery_id=gallery_id).first()
        return None

    def _update_cover(self, cover):
        cover.update_save()
        self._add_new_models(cover)

        gallery = self.find_official_gallery(cover)
        if gallery:
            cover.update(official_gallery=gallery)

            if len(cover.icgids) == 1 and len(gallery.model_pages) == 1:
                model_page = gallery.model_pages[0]
                if not model_page.various_models:
                    model = Model.objects(icgid=cover.icgids[0]).first()
                    model_page.update(model=model)

    def _add_new_models(self, cover):
        for icgid, url in zip(cover.icgids, cover.model_urls):
            model = Model.objects(icgid=icgid).first()
            if not model:
                thenude_page, _ = self.get_model_page(url)
                if thenude_page is None:
                    name = url.split('/')[-1].split('_')[0]
                    thenude_page = TheNudePage(icgid=icgid, name=name, url=url)
                logging.info(f'        new: {thenude_page.name}')
                thenude_page.update_save()

                model = Model(
                    icgid=thenude_page.icgid,
                    name=thenude_page.name,
                    birth_date=thenude_page.birth_date,
                )
                model.update_save()

    def fetch(self, site=None):
        if site:
            self._fetch_site(site)
        else:
            for site in sites:
                self._fetch_site(site)

    def _fetch_site(self, site):
        if isinstance(site, str):
            site = get_site(site)
        today = datetime.today()

        for thenude_site in site.thenude_dict:
            start_date = site.thenude_dict[thenude_site]['start']
            end_date = site.thenude_dict[thenude_site]['end']

            for date in self._year_month_range(start_date, today):
                if date > end_date:
                    break
                self._fetch_gallery_page(thenude_site, date.year, date.month)
