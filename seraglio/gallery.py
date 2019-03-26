import os

import mongoengine
from mongoengine import Document, StringField, DateTimeField, URLField, \
    SortedListField, ListField, IntField, ReferenceField

from .utils import PrettyPrint
from .model_page import ModelPage


class Gallery(PrettyPrint, Document):
    gallery_id = StringField(primary_key=True)
    site = StringField(required=True)
    date = DateTimeField(required=True)
    name = StringField(required=True)

    type = StringField(required=True, choices=['photoset', 'video'])
    model_pages = ListField(ReferenceField(ModelPage),
                            reverse_delete_rule=mongoengine.CASCADE)
    photographer = StringField()

    url = URLField(required=True, unique=True)

    length = StringField()
    num_photos = IntField()

    # member_rating = 0.0
    # num_ratings = 0

    # tags = []

    download_path = StringField()

    # meta = {'allow_inheritance': True}

    _nudesite = None

    @property
    def nudesite(self):
        if not self._nudesite:
            import seraglio
            self._nudesite = seraglio.get_site(self.site)
        return self._nudesite

    @property
    def models(self):
        return [model_page.model for model_page in self.model_pages
                if model_page.model]

    @property
    def member_url(self):
        return self.nudesite._get_gallery_member_url(self)

    def get_download_link(self):
        return self.nudesite.get_gallery_download_link(self)

    @property
    def path_name(self):
        name = self.name.replace('/', '_').replace(':', '_')
        site_name = self.nudesite.name
        return site_name + ' ' + self.date.strftime('%Y-%m-%d') + ' ' + name

    def update_save(self, *args, **kwargs):
        other = Gallery.objects(gallery_id=self.gallery_id).first()
        if other:
            for key in ['download_path']:
                value = getattr(other, key)
                if value:
                    setattr(self, key, value)
                model_pages = list(self.model_pages)
                self.model_pages = list(other.model_pages)
                for page in model_pages:
                    if page not in self.model_pages:
                        self.model_pages.append(page)
        self.save(*args, **kwargs)
