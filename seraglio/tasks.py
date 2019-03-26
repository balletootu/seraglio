import logging
import os

from .gallery import Gallery
from .model_page import ModelPage
from .model import Model


def reload():
    os.system('bash reload.sh')


def export_all():
    os.system('bash export.sh')
