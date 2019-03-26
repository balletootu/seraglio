import argparse
import logging

from mongoengine import connect

import seraglio


def main(args):
    thenude = seraglio.thenude

    if args.url:
        site = seraglio.get_site(args.url.split('/')[2].split('.')[-2])
        model_page, galleries = site.get_model_page(args.url)
        seraglio.update_model_page(model_page)
        for gallery in galleries:
            gallery.update_save()
    else:
        if args.site:
            site = seraglio.get_site(args.site)
            site.update(last_date=args.date)
            thenude.update(site=site, last_date=args.date)
        else:
            for site in seraglio.sites:
                site.update(last_date=args.date)
                thenude.update(site=site, last_date=args.date)

    seraglio.export_all()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--date', type=str, default='')
    parser.add_argument('-s', '--site', type=str, default='')
    parser.add_argument('-u', '--url', type=str, default='')
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
