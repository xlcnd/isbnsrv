"""graphene-aiohttp integration."""

import logging

from aiohttp import web
from graphql.execution.executors.asyncio import AsyncioExecutor

from .api import schema
from .. import SERVER

logger = logging.getLogger("isbnsrv")

# TODO(handle batch requests https://github.com/syrusakbary/aiodataloader)
# However due to the nature of the external services only allow batch requests
# for core services.


async def gql(request):
    """Parse the request and resolve the graphql query."""

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
            err = result.errors[0]
            raise Exception("execution errors - %r", err)
    except Exception as exc:
        logger.debug("Failed to execute the query - %r", exc)
        raise web.HTTPBadRequest(reason=f"Failed to execute the query -- {exc}.")

    return web.json_response(result.data, status=200, headers=SERVER)
