"""Web server and API for service 'isbnsrv' (isbnlib)."""

import asyncio
import concurrent.futures
import logging

from aiohttp import web

from async_imcache import MemoryCache

from resources import (
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

SERVER = {"Server": "isbnsrv/0.0.1"}

executor = concurrent.futures.ThreadPoolExecutor()  # max_workers=(5 x #cores)

logger = logging.getLogger("isbnsrv")

logging.basicConfig(level=logging.ERROR)

cache = MemoryCache()


async def bag(request):
    isbn = request.match_info.get("isbn", "")
    params = request.rel_url.query.get("fields", "")
    try:
        if params:
            params = params.split(",")
            data = await asyncio.get_event_loop().run_in_executor(
                executor, get_bag, isbn, tuple(params)
            )
        else:
            data = await asyncio.get_event_loop().run_in_executor(executor, get_bag, isbn)
    except Exception as ex:
        logger.error(f"Failed to get the bag for {isbn} - " + str(ex))
        raise web.HTTPInternalServerError(reason=f"Internal server error for {isbn}!")
    return web.json_response(data, headers=SERVER)


async def meta(request):
    isbn = request.match_info.get("isbn", "")
    service = request.match_info.get("provider", "")
    if service and service not in get_providers():
        raise web.HTTPNotFound(reason=f"Provider '{service}' not available!")
    try:
        if service:
            data = await asyncio.get_event_loop().run_in_executor(
                executor, get_meta, isbn, service
            )
        else:
            data = await asyncio.get_event_loop().run_in_executor(executor, get_meta, isbn)
    except Exception as ex:
        logger.error(f"Failed to get metadata for {isbn} - " + str(ex))
        raise web.HTTPInternalServerError(reason=f"Internal server error for {isbn}!")
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
    except Exception as ex:
        logger.error(f"Failed to get the description for {isbn} - " + str(ex))
        raise web.HTTPInternalServerError(reason=f"Internal server error for {isbn}!")
    data = {"description": data}
    return web.json_response(data, headers=SERVER)


async def cover(request):
    isbn = request.match_info.get("isbn", "")
    try:
        data = await asyncio.get_event_loop().run_in_executor(executor, get_cover, isbn)
    except Exception as ex:
        logger.error(f"Failed to get the cover for {isbn} - " + str(ex))
        raise web.HTTPInternalServerError(reason=f"Internal server error for {isbn}!")
    data = {"cover": data}
    return web.json_response(data, headers=SERVER)


async def editions(request):
    isbn = request.match_info.get("isbn", "")
    try:
        data = await asyncio.get_event_loop().run_in_executor(executor, get_editions, isbn)
    except Exception as ex:
        logger.error(f"Failed to get the editions for {isbn} - " + str(ex))
        raise web.HTTPInternalServerError(reason=f"Internal server error for {isbn}!")
    data = {"editions": data}
    return web.json_response(data, headers=SERVER)


async def providers(request):
    return web.json_response({"providers": get_providers()}, headers=SERVER)


@web.middleware
async def if_isbn_validate(request, handler):
    isbn = request.match_info.get("isbn", "")
    if isbn:
        if not get_isbn13(isbn):
            #  raise web.HTTPNotFound(reason=f"{isbn} is NOT a valid ISBN!")
            data = {"ERROR": {"code": 404, "reason": f"{isbn} is not a valid ISBN!"}}
            return web.json_response(data, status=404, headers=SERVER)
    return await handler(request)


@web.middleware
async def cache_middleware(request, handler):
    key = await cache.get_key(request)
    if await cache.has(key):
        data = await cache.get(key)
        return web.json_response(**data)
    try:
        original_response = await handler(request)
        headers = dict(original_response.headers)
        del headers["Content-Type"]
        data = dict(
            status=original_response.status, headers=headers, body=original_response.body
        )
        await cache.set(key, data)
        return original_response
    except:
        data = {"ERROR": {"code": 500, "reason": "Internal server error."}}
        return web.json_response(data, status=500, headers=SERVER)


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        if response.status == 200:
            return response
        status = response.status
        message = getattr(response, "message", "")
    except web.HTTPException as ex:
        status = ex.status
        message = ex.reason
    data = {"ERROR": {"code": status, "reason": message}}
    return web.json_response(data, status=status, headers=SERVER)


app = web.Application(middlewares=[cache_middleware, if_isbn_validate, error_middleware])
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
    ]
)

web.run_app(app, access_log=None)
