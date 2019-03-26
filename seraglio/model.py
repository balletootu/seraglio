import os

from mongoengine import Document, StringField, IntField

from .utils import PrettyPrint


class Model(PrettyPrint, Document):
    icgid = StringField(primary_key=True)
    name = StringField(required=True)

    birth_date = StringField(default='????-??-??')

    my_rating = IntField()

    def update_save(self, *args, **kwargs):
        other = Model.objects(icgid=self.icgid).first()
        if other:
            for key in ['name', 'my_rating']:
                value = getattr(other, key)
                if value:
                    setattr(self, key, value)
        self.save(*args, **kwargs)

    @property
    def rating(self) -> float:
        from .model_page import ModelPage
        rating = 0.0
        num_ratings = 0
        for model_page in ModelPage.objects(model=self):
            rating += model_page.member_rating * model_page.num_ratings
            num_ratings += model_page.num_ratings
        if num_ratings > 0:
            rating /= num_ratings
        if self.my_rating > 0.0:
            rating = self.my_rating * 0.9 + rating * 0.1
        else:
            rating = rating * 0.6
        return round(rating, 2)

    @property
    def galleries(self):
        from .model_page import ModelPage
        from .gallery import Gallery
        model_pages = list(ModelPage.objects(model=self))
        return Gallery.objects(model_pages__in=model_pages).order_by(
            'gallery_id')

    @property
    def thenude_page(self):
        from seraglio import TheNudePage
        return TheNudePage.objects(icgid=self.icgid).first()
