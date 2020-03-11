"""REST API for service 'isbnsrv' (isbnlib)."""

import asyncio
import logging

from aiohttp import web

from .. import SERVER, executor

from ..resources import (
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


logger = logging.getLogger("isbnsrv")


async def bag(request):
    isbn = request.match_info.get("isbn", "")
    params = request.rel_url.query.get("fields", "")
    try:
        if params:
            params = tuple(params.split(","))
            data = await get_bag(isbn, params)
        else:
            data = await get_bag(isbn)
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
