"""graphene-aiohttp integration."""

import logging

from aiohttp import web
from graphql.execution.executors.asyncio import AsyncioExecutor

from .api import schema
from .. import SERVER

logger = logging.getLogger("isbnsrv")


async def gql(request):
    try:
        data = await request.json()
    except Exception as exc:
        logger.debug("Failed to get the body's text - %r", exc, exc_info=False)
        raise web.HTTPBadRequest(
            reason="Failed to get the POST body's text. Check the JSON sent."
        )
    try:
        query = data.get("query")
        if not query:
            raise Exception("Empty query")
    except Exception as exc:
        logger.debug("Failed to get the query - %r", exc, exc_info=False)
        raise web.HTTPBadRequest(reason="Query not found. Check the JSON sent.")

    variables = data.get("variables")
    operation_name = data.get("operationName")

    try:
        result = await schema.execute(
            query,
            variables=variables,
            operation_name=operation_name,
            executor=AsyncioExecutor(),
            return_promise=True,
        )
        if result.errors:
            raise Exception("execution errors")
    except Exception:
        err = result.errors[0]
        logger.debug("Failed to execute the query - %r", err)
        raise web.HTTPBadRequest(reason=f"Failed to execute the query -- {err}.")

    # print(dumps(schema.introspect()))

    return web.json_response(result.data, status=200, headers=SERVER)
