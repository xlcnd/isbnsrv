"""Read and write to a dict-like cache."""


from collections import MutableMapping


class IMCache(MutableMapping):
    """Read and write to a dict-like cache."""

    MAXLEN = 1000

    # pylint: disable=keyword-arg-before-vararg
    def __init__(self, maxlen=MAXLEN, *a, **k):
        self.filepath = "IN MEMORY"
        self.maxlen = maxlen
        self.d = dict(*a, **k)
        while len(self.d) > maxlen:  # pragma: no cache
            self.popitem()

    async def __iter__(self):
        return iter(self.d)

    async def __len__(self):
        return len(self.d)

    async def __getitem__(self, k):
        return self.d[k]

    async def __setitem__(self, k, v):
        if k not in self.d and len(self.d) == self.maxlen:
            self.popitem()
        self.d[k] = v

    async def __contains__(self, key):
        return key in self.d

    async def __delitem__(self, k):
        del self.d[k]

    async def __bool__(self):
        return len(self.d) != 0

    async def __call__(self, k):
        """Implement function call operator."""
        try:
            return self.__getitem__(k)
        except KeyError:
            return None

    async def set(self, k, v):
        return self.__setitem__(k, v)

    async def get(self, k):
        return self.__getitem__(k)

    async def get_key(self, request):
        key = "{method}#{host}#{path}#{postdata}#{ctype}".format(
            method=request.method,
            path=request.rel_url.path_qs,
            host=request.url.host,
            postdata="".join(await request.post()),
            ctype=request.content_type,
        )

        return key
