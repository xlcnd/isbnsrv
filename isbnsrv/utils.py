import logging

from .resources import get_mask
from .typedefs import Author, MetadataDublinCore


logger = logging.getLogger("isbnsrv")


def dict_to_metadata(mdict):
    authors = mdict.get("Authors", [])
    authors = [Author(name=author) for author in authors]
    return MetadataDublinCore(
        isbn13=get_mask(mdict.get("ISBN-13", "")) or mdict.get("ISBN-13", ""),
        title=mdict.get("Title", ""),
        authors=authors,
        publisher=mdict.get("Publisher", ""),
        year=mdict.get("Year", None),
        language=mdict.get("Language", ""),
    )
