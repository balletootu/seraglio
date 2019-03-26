from datetime import datetime
import os
import glob
import logging
import warnings

from seraglio import utils, Gallery, ModelPage


class NudeSite:
    def __init__(self, id):
        self.id = id
        self.name = self.__class__.__name__

        self.host_name = f'www.{self.id}.com'
        self._url = 'https://www.' + self.id + '.com/'

        self.root_dir = os.path.join('html', self.id)
        self.index_dir = os.path.join(self.root_dir, 'all')
        self.model_page_dir = os.path.join(self.root_dir, 'model')

        self.thenude_dict = None

        self.auth = None

    def rebuild(self, fetch=True):
        urls = self.get_index(fetch=fetch)
        for page in ModelPage.objects(site=self.id, url__nin=urls):
            logging.info(f'deleted {page.id}')
            for gallery in Gallery.objects(model_pages=page):
                logging.info(f'deleted   {gallery.id}')
                gallery.delete()
            page.delete()

        if fetch:
            for url in urls:
                logging.info(url)
                page, galleries = self.get_model_page(url)
                page.update_save()
                for gallery in galleries:
                    gallery.update_save()
        else:
            for page, galleries in self.get_model_pages(fetch=False):
                page.update_save()
                for gallery in galleries:
                    gallery.update_save()

    def _get_index_urls(self):
        '''yields file name and index url'''
        raise NotImplementedError

    def _parse_index(self, html) -> list:
        '''returns list of model page urls'''
        raise NotImplementedError

    def get_index(self, fetch=True) -> list:
        '''returns list of model page urls'''
        urls = []
        if fetch:
            if not os.path.exists(self.index_dir):
                os.makedirs(self.index_dir)
            for file_name, url in self._get_index_urls():
                logging.info(url)
                r = utils.fetch_url(url)
                if r:
                    path = os.path.join(self.index_dir, file_name + '.html')
                    with open(path, 'wb') as f:
                        f.write(r.content)
                    for url in self._parse_index(r.html):
                        if url not in urls:
                            urls.append(url)
        else:
            paths = glob.glob(os.path.join(self.index_dir, '*.html'))
            for path in sorted(paths):
                logging.info(path)
                html = utils.load_html_file(path)
                for url in self._parse_index(html):
                    if url not in urls:
                        urls.append(url)
        return urls

    def get_local_index(self) -> list:
        warnings.warn('use get_index(fetch=False)', DeprecationWarning)
        return self.get_index(fetch=False)

    def _get_model_id(self, url):
        '''returns the model id'''
        raise NotImplementedError

    def _fetch_model_page(self, url):
        '''returns a html response'''
        if not os.path.exists(self.model_page_dir):
            os.makedirs(self.model_page_dir)
        model_id = self._get_model_id(url)
        r = utils.fetch_url(url)
        if r:
            path = os.path.join(self.model_page_dir, model_id + '.html')
            with open(path, 'wb') as f:
                f.write(r.content)
        return r

    def fetch_all_model_pages(self):
        for url in self.get_index():
            logging.info(url)
            self._fetch_model_page(url)

    def _parse_model_page(self, html):
        '''returns a model page and a list of galleries'''
        raise NotImplementedError

    def get_model_page(self, url):
        '''returns a model page and a list of galleries'''
        r = self._fetch_model_page(url)
        if r:
            return self._parse_model_page(r.html)
        else:
            return None, None

    def get_model_pages(self, fetch=True):
        '''yields a model page and a list of galleries'''
        if fetch:
            for url in self.get_index():
                logging.info(url)
                yield self.get_model_page(url)
        else:
            paths = glob.glob(os.path.join(self.model_page_dir, '*.html'))
            for path in sorted(paths):
                logging.info(path)
                html = utils.load_html_file(path)
                yield self._parse_model_page(html)

    def get_local_model_pages(self):
        warnings.warn('use get_model_pages(fetch=False)', DeprecationWarning)
        return self.get_model_pages(fetch=False)

    def update(self, last_date=None):
        logging.info(f'updating {self.name}')
        for model_page, galleries in self.get_updates(last_date=last_date):
            model_page.update_save()
            for gallery in galleries:
                gallery.update_save()

    def get_updates(self, last_date=None):
        '''yields a model page and a list of galleries'''
        if not last_date:
            last_date = self._get_last_date()
            logging.info(last_date)
        elif isinstance(last_date, str):
            last_date = datetime.strptime(last_date, '%Y-%m-%d')
        urls = list(self._get_latest_model_urls(last_date=last_date))
        for i, url in enumerate(urls):
            r = self._fetch_model_page(url)
            if r:
                model_page, galleries = self._parse_model_page(r.html)
                logging.info(f'    {i}/{len(urls)} {model_page.id}')
                yield model_page, galleries

    def _get_latest_model_urls(self, last_date):
        '''returns a list of urls of updated model pages'''
        raise NotImplementedError

    def _get_last_date(self):
        gallery = Gallery.objects(site=self.id).order_by('-date').first()
        if gallery:
            return gallery.date
        else:
            return datetime(1970, 1, 1)

    def get_gallery_download_link(self, gallery):
        if not self.auth:
            return None, None, None
        else:
            raise NotImplementedError

    @property
    def models(self):
        for model_page in ModelPage.objects(site=self.id).order_by('page_id'):
            if model_page.model:
                yield model_page.model

    @property
    def model_pages(self):
        return ModelPage.objects(site=self.id).order_by('page_id')

    @property
    def galleries(self):
        return Gallery.objects(site=self.id).order_by('gallery_id')
