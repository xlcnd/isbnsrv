"""GRAPHQL API for service 'isbnsrv' (isbnlib)."""

from graphene import Field, Int, List, ObjectType, String


class ISBN(ObjectType):
    isbn13 = String(required=True)
    ean13 = String(required=True)
    doi = String(required=True)
    isbn10 = String()
    info = String()


class MetadataDublinCoreProvider(ObjectType):
    name = String()


class FAST(ObjectType):
    numeric_id = String()
    class_text = String()


class Author(ObjectType):
    name = String()


class Identifiers(ObjectType):
    isbn13 = String(required=True)
    ean13 = String(required=True)
    doi = String(required=True)
    isbn10 = String()
    lcc = String()
    ddc = String()
    owi = String()
    oclc = String()
    fast = List(FAST)


class Cover(ObjectType):
    size = String()
    url = String()


class MetadataDublinCore(ObjectType):
    isbn13 = String(required=True)
    title = String(required=True)
    authors = List(Author)
    publisher = String()
    year = Int()
    language = String()


class MetadataExtra(ObjectType):
    description = String()
    identifiers = Field(Identifiers)
    covers = List(Cover)
    editions = List(String)
