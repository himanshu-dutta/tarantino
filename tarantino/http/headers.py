from tarantino.imports import t


class Headers(t.Mapping[str, str]):
    encoding_type = "latin-1"

    def __init__(
        self,
        *,
        headers_dict: t.Mapping[str, str | t.Sequence[str]] | None = None,
        scope: t.MutableMapping[str, t.Any] | None = None,
    ):
        if headers_dict is not None and scope is not None:
            raise AssertionError("Only one of headers and scope should be set.")

        self._headers: t.Dict[bytes, t.List[bytes] | bytes] = dict()

        if headers_dict is None and scope is None:
            return

        if headers_dict:
            for k, v in headers_dict.items():

                key = self.encode_key(k)
                value = self.encode_value(v)
                self._headers[key] = value

        if scope:
            for k, v in scope["headers"]:
                self.set(k, v, mode="append")

    def encode(self, s: t.Any):
        return s if isinstance(s, bytes) else bytes(str(s), encoding=self.encoding_type)

    def decode(self, s: bytes):
        return s.decode(self.encoding_type)

    def encode_key(self, key: str | bytes):
        assert isinstance(key, (str, bytes))
        return self.encode(key)

    def encode_value(self, value: t.Any | list):
        value = value if isinstance(value, list) else [value]
        value = [self.encode(item) for item in value]
        return value

    def decode_key(self, key: bytes):
        return self.decode(key)

    def decode_value(self, value: t.List[bytes]):
        value = [self.decode(item) for item in value]
        if len(value) == 1:
            return value[0]
        else:
            return value

    def __setitem__(self, key: str | bytes, value: str | bytes):
        key = self.encode_key(key)
        value = self.encode_value(value)
        self._headers[key] = value

    def __getitem__(self, key: str | bytes):
        return self._headers[self.encode(key)]

    def __delitem__(self, key: str | bytes):
        del self._headers[self.encode_key(key)]

    def __iter__(self):
        return iter(self._headers.keys())

    def __len__(self):
        return len(self._headers)

    def keys(self):
        return [self.decode_key(key) for key in self._headers.keys()]

    def values(self):
        return [self.decode_value(value) for value in self._headers.values()]

    def get(
        self,
        key: str | bytes,
        default: t.Any = None,
        decode=False,
    ):
        value = self._headers.get(self.encode(key), self.encode_value(default))
        return self.decode_value(value) if decode else value

    def set(
        self,
        key: str | bytes,
        value: str | bytes,
        mode: t.Literal["append", "replace"] = "replace",
    ):
        if mode not in ["append", "replace"]:
            raise ValueError(f"Invalid set mode: {mode}")

        key = self.encode_key(key)

        if mode == "append":
            value = self._headers.get(key, []) + self.encode_value(value)
            self[key] = value

        elif mode == "replace":
            self[key] = self.encode_value(value)

    def pop(
        self,
        key: str | bytes,
        default: t.Any = None,
        decode=False,
    ):
        key = self.encode_key(key)
        value = self.get(
            key,
            default=default,
            decode=decode,
        )
        if key in self._headers:
            del self[key]
        return value

    def setdefault(
        self,
        key: str | bytes,
        default: t.Any = None,
        decode=False,
    ):
        key = self.encode_key(key)
        value = default

        if key not in self._headers:
            self[key] = value
        else:
            value = self.get(key, default=default, decode=decode)

        return value

    def to_list(self, decode=False):
        headers_list = list()

        for k, v in self._headers.items():
            key = self.decode_key(k) if decode else k
            values = self.decode_value(v) if decode else v
            values = values if isinstance(values, list) else [values]

            for value in values:
                headers_list.append((key, value))

        return headers_list
