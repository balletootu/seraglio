import os

import mongoengine
from mongoengine import Document, StringField, ReferenceField, URLField, \
    IntField, FloatField, BooleanField
from .model import Model
from .utils import PrettyPrint


class ModelPage(PrettyPrint, Document):
    page_id = StringField(primary_key=True)
    model = ReferenceField(Model, reverse_delete_rule=mongoengine.NULLIFY)
    url = URLField(required=True, unique=True)
    site = StringField(required=True)
    name = StringField(required=True)

    country = StringField()
    age_debut = IntField()

    num_videos = IntField()
    num_photosets = IntField()

    eye_color = StringField()
    hair_color = StringField()
    height = IntField()
    weight = IntField()

    breasts = StringField()
    size = StringField()
    shaved = StringField()
    ethnicity = StringField()

    bio = StringField()

    member_rating = FloatField()
    num_ratings = IntField()

    male = BooleanField(default=False)
    various_models = BooleanField(default=False)

    @property
    def galleries(self):
        from .gallery import Gallery
        return Gallery.objects(model_pages=self)

    @property
    def model_id(self):
        return self.id.split('_')[1]

    @property
    def file_name(self):
        return self.model_id + '.html'

    @staticmethod
    def export_json():
        cmd = 'mongoexport --db seraglio --collection model_page --pretty ' \
            '--sort "{_id: 1}" --out database/model_pages.json'
        print(cmd)
        os.system(cmd)

    def update_save(self, *args, **kwargs):
        other = ModelPage.objects(page_id=self.page_id).first()
        if other:
            for key in ['model', 'male', 'various_models']:
                value = getattr(other, key)
                if value:
                    setattr(self, key, value)
        self.save(*args, **kwargs)
