import logging

from json import dumps

# from aiohttp import web
from graphql.execution.executors.asyncio import AsyncioExecutor

from .graphql_api import schema

logger = logging.getLogger("isbnsrv")


def run():

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

    q = """
          query Search {
            search(searchTerms: "reveries of a solitary walker") {
                isbn13
                title
                authors { name }
                publisher
                year
                language
            }
          }
        """

    # q = """
    #       query FullIsbn {
    #         fullIsbn(isbn: "9780140440393") {
    #           isbn13
    #           ean13
    #           doi
    #           isbn10
    #           info
    #         }
    #       }
    #     """

    # q = """
    #       query Providers {
    #         metadataDublinCoreProviders {
    #           name
    #         }
    #       }
    #     """

    # q = """
    #       query MetadataDublinCore {
    #         metadataDublinCore(isbn: "9780192821911") {
    #           isbn13
    #           title
    #           authors { name }
    #           publisher
    #           year
    #           language
    #         }
    #      }
    #    """

    # q = """
    #       query MetadataExtra {
    #         metadataExtra(isbn: "9780192821911") {
    #           description
    #           covers { size, url }
    #           identifiers { isbn13, doi, owi, ddc, fast { numericId, classText } }
    #           editions
    #         }
    #       }
    #     """

    result = schema.execute(q, executor=AsyncioExecutor())

    # assert not result.errors
    # with open('result.json', 'w', encoding='utf8') as json_file:
    #    json.dump(result.data, json_file, ensure_ascii=False)
    print(dumps(result.data, ensure_ascii=False).encode("utf8").decode())

    # print(dumps(schema.introspect()))
