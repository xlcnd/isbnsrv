"""Resources manager for 'isbnsrv'."""

import isbnlib
from isbnlib.registry import PROVIDERS
from isbnlib._imcache import IMCache

cache = IMCache(maxlen=50)

FIELDS = ("isbn13", "isbn10", "mask", "info", "metadata", "editions", "cover", "description")


def bag(isbn, fields=FIELDS):
    """Get all fields (bag) for a given ISBN.

       'fields' acts like a filter.
    """
    res = {}

    if "isbn13" in fields:
        res["isbn13"] = get_isbn13(isbn)

    if "isbn10" in fields:
        res["isbn10"] = get_isbn10(isbn)

    if "mask" in fields:
        res["mask"] = get_mask(isbn)

    if "info" in fields:
        res["info"] = get_info(isbn)

    if "metadata" in fields:
        service = None
        for srv in PROVIDERS:
            if srv in fields:
                service = srv
                break
        metadata = get_meta(isbn, service) if service else get_meta(isbn)
        res["metadata"] = metadata

    if "editions" in fields:
        res["editions"] = get_editions(isbn)

    if "cover" in fields:
        res["cover"] = get_cover(isbn)

    if "description" in fields:
        res["description"] = get_description(isbn)

    return res


def get_bag(isbn, fields=FIELDS):
    """Get big bag of data."""
    key = isbn + "".join(sorted(fields)) if fields != FIELDS else isbn
    if key not in cache:
        cache[key] = bag(isbn, fields)
    return cache[key]


def get_meta(isbn, service="goob"):
    """Get metadata from 'service'."""
    res = {}
    metadata = isbnlib.meta(isbn, service)
    if metadata:
        res = metadata
        res["Provider"] = service
    return res


def get_isbn13(isbn):
    return isbnlib.to_isbn13(isbn)


def get_isbn10(isbn):
    return isbnlib.to_isbn10(isbn)


def get_info(isbn):
    return isbnlib.info(isbn)


def get_mask(isbn):
    return isbnlib.mask(isbn)


def get_description(isbn):
    desc = isbnlib.desc(isbn)
    desc = desc.replace("\n", " ").strip() if desc else ""
    return desc


def get_cover(isbn):
    return isbnlib.cover(isbn)


def get_editions(isbn):
    return isbnlib.editions(isbn)


def get_providers():
    return PROVIDERS
