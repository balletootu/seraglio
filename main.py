import argparse
from datetime import datetime
import logging
import os
import time

from mongoengine import connect
from mongoengine import Document, StringField, DateTimeField, ListField
from mongoengine.errors import DoesNotExist

import seraglio
from seraglio import Model, ModelPage, Gallery, TheNudePage, TheNudeGallery


def main(args):

    for model in Model.objects:
        model.update(name=model.thenude_page.name)
    Gallery.objects().update(unset__download_path=1)

    seraglio.export_all()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)s: %(filename)s, %(lineno)d: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler('log.txt')
    file_handler.setLevel(logging.WARNING)
    file_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(filename)s, %(lineno)d: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    connect('seraglio')

    main(args)
