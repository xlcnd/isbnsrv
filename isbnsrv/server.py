"""Web server and API for service 'isbnsrv' (isbnlib)."""

import logging
import os

from aiohttp import web

from . import __api__, SERVER
from .cache import MemoryCache, make_key
from .resources import get_isbn13
from .rest import rest
from .gql.aiohttp import gql


logger = logging.getLogger("isbnsrv")
logging.basicConfig(level=logging.INFO)

cache = MemoryCache()
api_id = "/api/v" + __api__ + "/"


async def healthcheck(request):
    return web.json_response({"isbnsrv": "OK"}, status=200, headers=SERVER)


async def version(request):
    return web.json_response({"version": SERVER["Server"]}, status=200, headers=SERVER)


@web.middleware
async def preflight_middleware(request, handler):
    """Preflight request support for apollo-client.

    https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request
    """
    if request.method.upper() == "OPTIONS":
        headers = request.headers
        origin = headers.get("Origin", "")
        method = headers.get("Access-Control-Request-Method", "").upper()

        accepted_methods = ["GET", "OPTIONS"]
        if request.path == "/graphql":
            accepted_methods = ["POST", "OPTIONS"]
        if method and method in accepted_methods:
            return web.Response(
                status=200,
                headers={
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Methods": ", ".join(accepted_methods),
                    "Access-Control-Max-Age": str(86400),
                },
            )
        return web.Response(status=400)
    return await handler(request)


@web.middleware
async def validate_isbn_middleware(request, handler):
    isbn = request.match_info.get("isbn", "")
    if isbn:
        if not get_isbn13(isbn):
            logger.error("%s is not a valid ISBN!", isbn)
            raise web.HTTPNotFound(reason=f"{isbn} is NOT a valid ISBN!")
    return await handler(request)


@web.middleware
async def cache_middleware(request, handler):
    key = await make_key(request)
    if await cache.has(key):
        data = await cache.get(key)
        return web.json_response(**data)
    original_response = await handler(request)
    try:
        headers = dict(original_response.headers)
        del headers["Content-Type"]
        data = dict(
            status=original_response.status,
            headers=headers,
            body=original_response.body,
        )
        await cache.set(key, data)
        return original_response
    except Exception as exc:
        logger.info("Error in async cache - %r", exc, exc_info=True)
        raise web.HTTPInternalServerError(reason="Internal server error!") from None


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        if response.status == 200:
            return response
        status = response.status
        message = getattr(response, "message", "")
        logger.error("(%s) error %s", status, message, exc_info=True)
    except web.HTTPException as exc:
        status = exc.status
        message = exc.reason
        if status == 404:
            logger.info(
                "(%s) HTTPException in error_middleware - %s",
                status,
                message,
                exc_info=True,
            )
        else:
            logger.info("(%s) HTTPException in error_middleware - %s", status, message)
    data = {"errors": [{"code": status, "reason": message}]}
    return web.json_response(data, status=status, headers=SERVER)


async def make_app():
    app = web.Application(
        middlewares=[
            preflight_middleware,
            error_middleware,
            cache_middleware,
            validate_isbn_middleware,
        ]
    )
    app.add_routes(
        [
            web.get(api_id + "isbns/{isbn}", rest.bag),
            web.get(api_id + "isbns/{isbn}/metadata", rest.meta),
            web.get(api_id + "isbns/{isbn}/metadata/{provider}", rest.meta),
            web.get(api_id + "isbns/{isbn}/isbn10", rest.isbn10),
            web.get(api_id + "isbns/{isbn}/isbn13", rest.isbn13),
            web.get(api_id + "isbns/{isbn}/info", rest.info),
            web.get(api_id + "isbns/{isbn}/mask", rest.mask),
            web.get(api_id + "isbns/{isbn}/description", rest.description),
            web.get(api_id + "isbns/{isbn}/classifiers", rest.classify),
            web.get(api_id + "isbns/{isbn}/cover", rest.cover),
            web.get(api_id + "isbns/{isbn}/editions", rest.editions),
            web.get(api_id + "providers", rest.providers),
            web.get(api_id + "version", version),
            web.get(api_id + "7E2", healthcheck),
            web.post("/graphql", gql),
        ]
    )
    return app


def run():
    app = make_app()
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, port=port, access_log=None)
