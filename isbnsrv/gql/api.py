"""GRAPHQL API for service 'isbnsrv' (isbnlib)."""

import asyncio
import logging

from graphene import Field, List, ObjectType, String, Schema

from .. import executor
from ..resources import (
    get_classify,
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
from .typedefs import (
    ISBN,
    MetadataDublinCoreProvider,
    FAST,
    Identifiers,
    Cover,
    MetadataDublinCore,
    MetadataExtra,
)
from .utils import dict_to_metadata


logger = logging.getLogger("isbnsrv")


class Query(ObjectType):

    search = Field(List(MetadataDublinCore), search_terms=String(required=True))
    full_isbn = Field(ISBN, isbn=String(required=True))
    metadata_dublin_core = Field(
        MetadataDublinCore, isbn=String(required=True), provider=String(default_value="goob")
    )
    metadata_extra = Field(MetadataExtra, isbn=String(required=True))
    metadata_dublin_core_providers = List(MetadataDublinCoreProvider)

    async def resolve_search(root, info, search_terms):
        meta_list = await asyncio.get_event_loop().run_in_executor(
            executor, get_goom, search_terms
        )
        return map(dict_to_metadata, meta_list)

    def resolve_full_isbn(root, info, isbn):
        isbn = get_isbn13(isbn)
        if not isbn:
            raise Exception("Not valid isbn")
        return ISBN(
            isbn13=get_mask(isbn) or isbn,
            ean13=isbn,
            doi=get_doi(isbn),
            isbn10=get_mask(get_isbn10(isbn)) or get_isbn10(isbn),
            info=get_info(isbn),
        )

    async def resolve_metadata_dublin_core(root, info, isbn, provider):
        isbn = get_isbn13(isbn)
        if not isbn:
            raise Exception("Not valid isbn")
        meta = await asyncio.get_event_loop().run_in_executor(
            executor, get_meta, isbn, provider
        )
        return dict_to_metadata(meta)

    async def resolve_metadata_extra(root, info, isbn):
        isbn = get_isbn13(isbn)
        if not isbn:
            raise Exception("Not valid isbn")

        async def get_covers(isbn):
            covers = await asyncio.get_event_loop().run_in_executor(executor, get_cover, isbn)
            covers = [Cover(size=k, url=covers[k]) for k in covers]
            return covers

        async def get_identifiers(isbn):
            classifiers = await asyncio.get_event_loop().run_in_executor(
                executor, get_classify, isbn
            )
            fast = classifiers.get("fast", {})
            if fast:
                fast = [FAST(numeric_id=k, class_text=fast[k]) for k in fast]
            else:
                fast = [{}]
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

        async def get_desc(isbn):
            return await asyncio.get_event_loop().run_in_executor(
                executor, get_description, isbn
            )

        async def get_eds(isbn):
            return await asyncio.get_event_loop().run_in_executor(executor, get_editions, isbn)

        return MetadataExtra(
            description=await get_desc(isbn),
            identifiers=await get_identifiers(isbn),
            covers=await get_covers(isbn),
            editions=await get_eds(isbn),
        )

    def resolve_metadata_dublin_core_providers(root, info):
        return [MetadataDublinCoreProvider(name=prov) for prov in get_providers()]


schema = Schema(query=Query, auto_camelcase=True)
