# import pytest
from isbnsrv.server import make_app

# FIXME


# all requests on same loop
async def test_api(aiohttp_client):
    app = await make_app()
    client = await aiohttp_client(app)

    resp = await client.get("/api/v1/isbns/9780140440393/isbn10")
    assert resp.status == 200
    text = await resp.text()
    assert '{"isbn10": "0140440399"}' == text

    resp = await client.get("/api/v1/isbns/9780140440393/isbn13")
    assert resp.status == 200
    text = await resp.text()
    assert '{"isbn13": "9780140440393"}' == text

    resp = await client.get("/api/v1/isbns/9780140440393/mask")
    assert resp.status == 200
    text = await resp.text()
    assert '{"mask": "978-0-14-044039-3"}' == text

    resp = await client.get("/api/v1/isbns/9780140440393/info")
    assert resp.status == 200
    text = await resp.text()
    assert '{"info": "English language"}' == text

    resp = await client.get("/api/v1/isbns/9780140440393/metadata")
    assert resp.status == 200
    text = await resp.text()
    assert "History Of The Peloponnesian War" in text

    resp = await client.get("/api/v1/isbns/9780140440393?fields=metadata")
    assert resp.status == 200
    text = await resp.text()
    assert "History Of The Peloponnesian War" in text

    resp = await client.get("/api/v1/isbns/9780140440393/metadata/goob")
    assert resp.status == 200
    text = await resp.text()
    assert "Thucydides" in text

    resp = await client.get("/api/v1/isbns/9780140440393?fields=metadata,goob")
    assert resp.status == 200
    text = await resp.text()
    assert "History Of The Peloponnesian War" in text

    resp = await client.get("/api/v1/isbns/9780140440393/description")
    assert resp.status == 200
    text = await resp.text()
    assert "four hundred years" in text

    resp = await client.get("/api/v1/isbns/9780140440393?fields=description")
    assert resp.status == 200
    text = await resp.text()
    assert "four hundred years before the birth of Christ" in text

    resp = await client.get("/api/v1/isbns/9780140440393/cover")
    assert resp.status == 200
    text = await resp.text()
    assert "id=RQo1YIvlwRAC" in text

    resp = await client.get("/api/v1/isbns/9780140440393?fields=cover")
    assert resp.status == 200
    text = await resp.text()
    assert "id=RQo1YIvlwRAC" in text

    resp = await client.get("/api/v1/isbns/9780140440393/editions")
    assert resp.status == 200
    text = await resp.text()
    assert "9780140440393" in text

    resp = await client.get("/api/v1/isbns/9780140440393?fields=editions")
    assert resp.status == 200
    text = await resp.text()
    assert "9780140440393" in text

    resp = await client.get("/api/v1/isbns/9780140440393")
    assert resp.status == 200
    text = await resp.text()
    assert "9780140440393" in text

    resp = await client.get("/api/v1/isbns/978014044039")
    assert resp.status == 404
    text = await resp.text()
    assert "ERROR" in text

    # await client.close()
    # await app.shutdown()


# request on different loop
async def test_isbn10(aiohttp_client):
    app = await make_app()
    client = await aiohttp_client(app)

    resp = await client.get("/api/v1/isbns/9780140440393/isbn10")
    assert resp.status == 200
    text = await resp.text()
    assert '{"isbn10": "0140440399"}' == text

    # await client.close()
    # await app.shutdown()


# request on different loop
async def test_isbn13(aiohttp_client):
    app = await make_app()
    client = await aiohttp_client(app)

    resp = await client.get("/api/v1/isbns/9780140440393/isbn13")
    assert resp.status == 200
    text = await resp.text()
    assert '{"isbn13": "9780140440393"}' == text

    # await client.close()
    # await app.shutdown()
