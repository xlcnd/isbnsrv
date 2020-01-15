from isbnsrv.server import make_app


# all requests on same (app) instance
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

    resp = await client.get("/api/v1/isbns/978-0192821911/metadata")
    assert resp.status == 200
    text = await resp.text()
    assert "Peloponnesian War" in text

    resp = await client.get("/api/v1/isbns/9780192821911?fields=metadata")
    assert resp.status == 200
    text = await resp.text()
    assert "Peloponnesian War" in text

    resp = await client.get("/api/v1/isbns/9780192821911/metadata/openl")
    assert resp.status == 200
    text = await resp.text()
    assert "Peloponnesian War" in text

    resp = await client.get("/api/v1/isbns/9780192821911?fields=metadata,openl")
    assert resp.status == 200
    text = await resp.text()
    assert "Peloponnesian War" in text

    resp = await client.get("/api/v1/isbns/9780192821911/metadata/goob")
    assert resp.status == 200
    text = await resp.text()
    assert "Thucydides" in text

    resp = await client.get("/api/v1/isbns/9780192821911?fields=metadata,goob")
    assert resp.status == 200
    text = await resp.text()
    assert "Peloponnesian War" in text

    resp = await client.get("/api/v1/isbns/9780192821911/description")
    assert resp.status == 200
    text = await resp.text()
    assert "Peloponnesian" in text

    resp = await client.get("/api/v1/isbns/9780192821911?fields=description")
    assert resp.status == 200
    text = await resp.text()
    assert "Peloponnesian" in text

    resp = await client.get("/api/v1/isbns/9780192821911/cover")
    assert resp.status == 200
    text = await resp.text()
    assert "id=CSZFAQAAIAAJ" in text

    resp = await client.get("/api/v1/isbns/9780192821911?fields=cover")
    assert resp.status == 200
    text = await resp.text()
    assert "id=CSZFAQAAIAAJ" in text

    resp = await client.get("/api/v1/isbns/9780192821911/editions")
    assert resp.status == 200
    text = await resp.text()
    assert "9780192821911" in text

    resp = await client.get("/api/v1/isbns/9780192821911?fields=editions")
    assert resp.status == 200
    text = await resp.text()
    assert "9780192821911" in text

    resp = await client.get("/api/v1/isbns/9780140440393")
    assert resp.status == 200
    text = await resp.text()
    assert "9780140440393" in text

    resp = await client.get("/api/v1/isbns/978014044039")
    assert resp.status == 404
    text = await resp.text()
    assert "ERROR" in text


# request on different (app) instance
async def test_isbn10(aiohttp_client):
    app = await make_app()
    client = await aiohttp_client(app)

    resp = await client.get("/api/v1/isbns/9780140440393/isbn10")
    assert resp.status == 200
    text = await resp.text()
    assert '{"isbn10": "0140440399"}' == text


# request on different (app) instance
async def test_isbn13(aiohttp_client):
    app = await make_app()
    client = await aiohttp_client(app)

    resp = await client.get("/api/v1/isbns/9780140440393/isbn13")
    assert resp.status == 200
    text = await resp.text()
    assert '{"isbn13": "9780140440393"}' == text
