from tarantino.imports import t


class Headers(t.Mapping[str, str]):
    encoding_type = "latin-1"

    def __init__(
        self,
        *,
        headers: t.Mapping[str, str | t.Sequence[str]] | None = None,
        scope: t.MutableMapping[str, t.Any] | None = None,
    ):
        if headers is not None and scope is not None:
            raise AssertionError("Only one of headers and scope should be set.")

        self._headers: t.List[t.Tuple[bytes, bytes]] = []

        if headers is None and scope is None:
            return

        if headers:
            if isinstance(headers, t.Sequence):
                self._headers = [(self.encode(k), self.encode(v)) for (k, v) in headers]
            if isinstance(headers, t.Mapping):
                for k, v in headers.items():
                    key = self.encode(k)
                    if isinstance(v, t.Sequence):
                        for item in v:
                            item = self.encode(item)
                            self._headers.append((key, item))
                    else:
                        value = self.encode(v)
                        self._headers.append((key, value))

        if scope:
            self._headers = scope["headers"]

    def encode(self, s: t.Any):
        return s if isinstance(s, bytes) else bytes(str(s), encoding=self.encoding_type)

    def decode(self, s: bytes):
        return s.decode(self.encoding_type)

    def __setitem__(self, key: str | bytes, value: str | bytes):
        key = self.encode(key)
        value = self.encode(value)
        self._headers.append((key, value))

    def __getitem__(self, key: str | bytes):
        key = self.encode(key)
        values = []

        for k, v in self._headers:
            if key == k:
                values.append(v)

        if len(values) == 0:
            raise KeyError(f"Invalid key: {self.decode(key)}")

        return values if len(values) > 1 else values[0]

    def __iter__(self):
        return iter([k for (k, _) in self._headers])

    def __len__(self):
        return len(self._headers)

    def get(self, key: str | bytes, default: t.Any = None, decode=False):
        try:
            return self.decode(self[key]) if decode else self[key]
        except KeyError:
            return default

    def set(
        self,
        key: str | bytes,
        value: str | bytes,
        mode: t.Literal["append", "replace"] = "replace",
    ):
        if mode not in ["append", "replace"]:
            raise ValueError(f"Invalid set mode: {mode}")

        if mode == "append":
            self[key] = value

        elif mode == "replace":
            replace_idx = -1
            key = self.encode(key)
            for idx, (k, v) in enumerate(self._headers):
                if k == key:
                    replace_idx = idx
                    break

            if replace_idx == -1:
                self[key] = value
            else:
                self._headers[replace_idx] = (self.encode(key), self.encode(value))

    def pop(self, key: str | bytes):
        key = self.encode(key)
        pop_idxs = []
        for idx, (k, v) in enumerate(self._headers):
            if k == key:
                pop_idxs.append(idx)

        for idx in pop_idxs:
            self._headers.pop(idx)

    def setdefault(self, key: str | bytes, default: t.Any = None, decode=False):
        try:
            return self.decode(self[key]) if decode else self[key]
        except KeyError:
            self[key] = self.encode(default)
            return self.decode(self[key]) if decode else self[key]

    def getlist(self, decode=False):
        if not decode:
            return self._headers

        _headers = [(self.decode(k), self.decode(v)) for (k, v) in self._headers]
        return _headers
