"""Web server and API for service 'isbnsrv' (isbnlib)."""

import asyncio
import concurrent.futures
import logging
import os

from aiohttp import web

from . import __version__

from .cache import MemoryCache

from .resources import (
    get_bag,
    get_cover,
    get_description,
    get_editions,
    get_info,
    get_isbn10,
    get_isbn13,
    get_mask,
    get_meta,
    get_providers,
)

SERVER = {"Server": f"isbnsrv/{__version__}"}

executor = concurrent.futures.ThreadPoolExecutor()  # max_workers=(5 x #cores)

logger = logging.getLogger("isbnsrv")

logging.basicConfig(level=logging.INFO)

cache = MemoryCache()


async def make_key(request):
    key = "{method}#{host}#{path}#{postdata}#{ctype}".format(
        method=request.method,
        path=request.rel_url.path_qs,
        host=request.url.host,
        postdata="".join(await request.post()),
        ctype=request.content_type,
    )
    return key


async def bag(request):
    isbn = request.match_info.get("isbn", "")
    params = request.rel_url.query.get("fields", "")
    try:
        if params:
            params = tuple(params.split(","))
            data = await asyncio.get_event_loop().run_in_executor(
                executor, get_bag, isbn, params
            )
        else:
            data = await asyncio.get_event_loop().run_in_executor(executor, get_bag, isbn)
    except Exception as exc:
        logger.info("Failed to get the bag for %s - %r", isbn, exc, exc_info=True)
        raise web.HTTPInternalServerError(
            reason=f"Internal server error for {isbn}!"
        ) from None
    return web.json_response(data, headers=SERVER)


async def meta(request):
    isbn = request.match_info.get("isbn", "")
    service = request.match_info.get("provider", "")
    if service and service not in get_providers():
        logger.error("Provider '%s' not available!", service)
        raise web.HTTPNotFound(reason=f"Provider '{service}' not available!")
    try:
        if service:
            data = await asyncio.get_event_loop().run_in_executor(
                executor, get_meta, isbn, service
            )
        else:
            data = await asyncio.get_event_loop().run_in_executor(executor, get_meta, isbn)
    except Exception as exc:
        logger.info("Failed to get metadata for %s - %r", isbn, exc, exc_info=True)
        raise web.HTTPInternalServerError(
            reason=f"Internal server error for {isbn}!"
        ) from None
    data = {"metadata": data}
    return web.json_response(data, headers=SERVER)


async def isbn10(request):
    isbn = request.match_info.get("isbn", "")
    data = {"isbn10": get_isbn10(isbn)}
    return web.json_response(data, headers=SERVER)


async def isbn13(request):
    isbn = request.match_info.get("isbn", "")
    data = {"isbn13": get_isbn13(isbn)}
    return web.json_response(data, headers=SERVER)


async def info(request):
    isbn = request.match_info.get("isbn", "")
    data = {"info": get_info(isbn)}
    return web.json_response(data, headers=SERVER)


async def mask(request):
    isbn = request.match_info.get("isbn", "")
    data = {"mask": get_mask(isbn)}
    return web.json_response(data, headers=SERVER)


async def description(request):
    isbn = request.match_info.get("isbn", "")
    try:
        data = await asyncio.get_event_loop().run_in_executor(executor, get_description, isbn)
    except Exception as exc:
        logger.info("Failed to get the description for %s - %r", isbn, exc, exc_info=True)
        raise web.HTTPInternalServerError(
            reason=f"Internal server error for {isbn}!"
        ) from None
    data = {"description": data}
    return web.json_response(data, headers=SERVER)


async def cover(request):
    isbn = request.match_info.get("isbn", "")
    try:
        data = await asyncio.get_event_loop().run_in_executor(executor, get_cover, isbn)
    except Exception as exc:
        logger.info("Failed to get the cover for %s - %r", isbn, exc, exc_info=True)
        raise web.HTTPInternalServerError(
            reason=f"Internal server error for {isbn}!"
        ) from None
    data = {"cover": data}
    return web.json_response(data, headers=SERVER)


async def editions(request):
    isbn = request.match_info.get("isbn", "")
    try:
        data = await asyncio.get_event_loop().run_in_executor(executor, get_editions, isbn)
    except Exception as exc:
        logger.info("Failed to get the editions for %s - %r", isbn, exc, exc_info=True)
        raise web.HTTPInternalServerError(
            reason=f"Internal server error for {isbn}!"
        ) from None
    data = {"editions": data}
    return web.json_response(data, headers=SERVER)


async def providers(request):
    return web.json_response({"providers": get_providers()}, headers=SERVER)


async def healthcheck(request):
    return web.json_response({"isbnsrv": "OK"}, status=200, headers=SERVER)


async def version(request):
    return web.json_response({"version": SERVER["Server"]}, status=200, headers=SERVER)


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
            status=original_response.status, headers=headers, body=original_response.body
        )
        await cache.set(key, data)
        return original_response
    except Exception as exc:
        logger.info("Error in async cache - %r", exc, exc_info=True)
        raise web.HTTPInternalServerError(reason=f"Internal server error!") from None


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
                "(%s) HTTPException in error_middleware - %s", status, message, exc_info=True
            )
        else:
            logger.info("(%s) HTTPException in error_middleware - %s", status, message)
    data = {"ERROR": {"code": status, "reason": message}}
    return web.json_response(data, status=status, headers=SERVER)


async def make_app():
    app = web.Application(
        middlewares=[error_middleware, cache_middleware, validate_isbn_middleware]
    )
    app.add_routes(
        [
            web.get("/api/v1/isbns/{isbn}", bag),
            web.get("/api/v1/isbns/{isbn}/metadata", meta),
            web.get("/api/v1/isbns/{isbn}/metadata/{provider}", meta),
            web.get("/api/v1/isbns/{isbn}/isbn10", isbn10),
            web.get("/api/v1/isbns/{isbn}/isbn13", isbn13),
            web.get("/api/v1/isbns/{isbn}/info", info),
            web.get("/api/v1/isbns/{isbn}/mask", mask),
            web.get("/api/v1/isbns/{isbn}/description", description),
            web.get("/api/v1/isbns/{isbn}/cover", cover),
            web.get("/api/v1/isbns/{isbn}/editions", editions),
            web.get("/api/v1/providers", providers),
            web.get("/api/v1/version", version),
            web.get("/api/v1/7E2", healthcheck),
        ]
    )
    return app


def run():
    app = make_app()
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, port=port, access_log=None)
