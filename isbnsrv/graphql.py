"""GRAPHQL API for service 'isbnsrv' (isbnlib)."""

import logging

# from aiohttp import web

from json import dumps
from graphene import Field, Int, List, ObjectType, String, Schema
from graphql.execution.executors.asyncio import AsyncioExecutor

from .resources import (
    # get_classify,
    get_cover,
    get_description,
    get_doi,
    get_editions,
    get_goom,
    get_info,
    get_isbn10,
    get_isbn13,
    get_mask,
    get_meta,
    get_providers,
)

logger = logging.getLogger("isbnsrv")


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


class Query(ObjectType):

    search = Field(List(MetadataDublinCore), search_terms=String(required=True))
    full_isbn = Field(ISBN, isbn=String(required=True))
    metadata_dublin_core = Field(
        MetadataDublinCore, isbn=String(required=True), provider=String(default_value="goob")
    )
    metadata_extra = Field(MetadataExtra, isbn=String(required=True))
    metadata_dublin_core_providers = List(MetadataDublinCoreProvider)

    def resolve_search(root, info, search_terms):
        meta_list = get_goom(search_terms)
        return map(dict_to_metadata, meta_list)

    def resolve_full_isbn(root, info, isbn):
        return ISBN(
            isbn13=get_mask(get_isbn13(isbn)) or get_isbn13(isbn),
            ean13=get_isbn13(isbn),
            doi=get_doi(isbn),
            isbn10=get_mask(get_isbn10(isbn)) or get_isbn10(isbn),
            info=get_info(isbn),
        )

    def resolve_metadata_dublin_core(root, info, isbn, provider):
        return dict_to_metadata(get_meta(isbn, provider))

    def resolve_metadata_extra(root, info, isbn):
        def get_covers(isbn):
            covers = get_cover(isbn)
            covers = [Cover(size=k, url=covers[k]) for k in covers]
            return covers

        def get_identifiers(isbn):
            # classifiers = get_classify(isbn)
            classifiers = {
                "owi": "3374702141",
                "oclc": "488613559",
                "lcc": "DF229.T5",
                "ddc": "938.05",
                "fast": {"1000": "dummydummy", "1100": "dummy"},
            }
            fast = classifiers.get("fast", "")
            if fast:
                fast = [FAST(numeric_id=k, class_text=fast[k]) for k in fast]
            return Identifiers(
                isbn13=get_mask(get_isbn13(isbn)) or get_isbn13(isbn),
                ean13=get_isbn13(isbn),
                doi=get_doi(isbn),
                isbn10=get_isbn10(isbn),
                lcc=classifiers.get("lcc", ""),
                ddc=classifiers.get("ddc", ""),
                owi=classifiers.get("owi", ""),
                oclc=classifiers.get("oclc", ""),
                fast=fast,
            )

        return MetadataExtra(
            description=get_description(isbn),
            identifiers=get_identifiers(isbn),
            covers=get_covers(isbn),
            editions=get_editions(isbn),
        )

    def resolve_metadata_dublin_core_providers(root, info):
        return [MetadataDublinCoreProvider(name=prov) for prov in get_providers()]


def run():
    schema = Schema(query=Query, auto_camelcase=True)

    # result = schema.execute(
    #     """
    #      query FullIsbn($isbn: String!) {
    #        fullIsbn(isbn: $isbn) {
    #          isbn13
    #          ean13
    #          doi
    #          isbn10
    #          info
    #        }
    #      }
    #    """,
    #     variables={"isbn": "9780140440393"},
    # executor=AsyncioExecutor(),)

    result = schema.execute(
        """
         query Search {
           search(searchTerms: "the name of the rose") {
               isbn13
               title
               authors { name }
               publisher
               year
               language
           }
         }
        """,
        executor=AsyncioExecutor(),
    )

    # result = schema.execute(
    #     '''
    #       query FullIsbn {
    #         fullIsbn(isbn: "9780140440393") {
    #           isbn13
    #           ean13
    #           doi
    #           isbn10
    #           info
    #         }
    #       }
    #     '''
    # )

    # result = schema.execute(
    #    """
    #      query Providers {
    #        metadataDublinCoreProviders {
    #          name
    #        }
    #      }
    #    """,
    # executor=AsyncioExecutor(),)

    # result = schema.execute(
    #     """
    #      query MetadataDublinCore {
    #        metadataDublinCore(isbn: "9780192821911") {
    #          isbn13
    #          title
    #          authors { name }
    #          publisher
    #          year
    #          language
    #        }
    #      }
    #    """,
    # executor=AsyncioExecutor(),)

    # result = schema.execute(
    #     """
    #       query MetadataExtra {
    #         metadataExtra(isbn: "9780192821911") {
    #           description
    #           covers { size, url }
    #           identifiers { isbn13, doi, owi, ddc, fast { numericId, classText } }
    #         }
    #       }
    #     """,
    # executor=AsyncioExecutor(),)

    assert not result.errors
    # with open('result.json', 'w', encoding='utf8') as json_file:
    #    json.dump(result.data, json_file, ensure_ascii=False)
    print(dumps(result.data, ensure_ascii=False).encode("utf8").decode())

    # print(dumps(schema.introspect()))
