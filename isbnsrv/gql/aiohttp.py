"""graphene-aiohttp integration."""

import logging

# from json import dumps

from aiohttp import web
from graphql.execution.executors.asyncio import AsyncioExecutor

from .api import schema
from .. import SERVER

logger = logging.getLogger("isbnsrv")


# From request:
# 1. if POST get body
# 2. parse body (query, params, name)
# 3. validate body
# 4. validate inputs: schema, ...
# 5. set headers
# 6. await execute query
# 7. set response (format, encoding, ...)


async def gql(request):
    # if request.can_read_body:
    data = await request.json()
    # print(data)
    # print(await request.post())
    query = data.get("query")
    print(query)
    variables = data.get("variables")
    operation_name = data.get("operationName")

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

    # q = """
    #       query Search {
    #         search(searchTerms: "reveries of a solitary walker") {
    #             isbn13
    #             title
    #             authors { name }
    #             publisher
    #             year
    #             language
    #         }
    #       }
    #     """
    # q = "query Search { search(searchTerms: \"reveries of a solitary walker\") { isbn13 title authors { name } publisher year language } }"

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

    # q="query Providers { metadataDublinCoreProviders { name } }"

    # result = await schema.execute(q, executor=AsyncioExecutor(), return_promise=True)

    result = await schema.execute(
        query,
        variables=variables,
        operation_name=operation_name,
        executor=AsyncioExecutor(),
        return_promise=True,
    )

    # assert not result.errors
    # with open('result.json', 'w', encoding='utf8') as json_file:
    #    json.dump(result.data, json_file, ensure_ascii=False)
    # print(dumps(result.data, ensure_ascii=False).encode("utf8").decode())

    # print(dumps(schema.introspect()))
    return web.json_response(result.data, status=200, headers=SERVER)


# def run():
#   asyncio.run(gql())  #py3.7+
#    loop = asyncio.get_event_loop()
#    loop.run_until_complete(gql())
#    loop.close()
