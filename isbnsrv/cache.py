"""Read and write to a dict-like cache."""

from hashlib import sha256


class MemoryCache:
    """Read and write to a dict-like cache."""

    MAXLEN = 1000

    def __init__(self, maxlen=MAXLEN):
        self.filepath = "IN MEMORY"
        self.maxlen = maxlen
        self.d = {}
        while len(self.d) > maxlen:  # pragma: no cache
            self.d.popitem()

    async def set(self, k, v):
        if k not in self.d and len(self.d) == self.maxlen:
            self.d.popitem()
        if v:
            self.d[k] = v

    async def get(self, k, default=None):
        try:
            return self.d[k]
        except KeyError:
            return default

    async def delitem(self, k):
        del self.d[k]

    async def has(self, key):
        return key in self.d

    async def len(self):
        return len(self.d)


async def make_key(request):
    key = "{method}#{host}#{path}#{postdata}#{ctype}".format(
        method=request.method,
        path=request.rel_url.path_qs,
        host=request.url.host,
        postdata=await request.text(),
        ctype=request.content_type,
    )
    return sha256(key.encode()).hexdigest()
