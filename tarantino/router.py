from ._types import HTTPCallback
from .imports import t

_default_cast = str
_default_cast_name = "str"
_cast_registry: t.Dict[str, t.Callable] = {
    "int": int,
    "str": str,
    "float": float,
    "bool": bool,
}


_indent_factor = 4


class _Node:
    _default_key = 0

    def __init__(self):

        self.cast_name = _default_cast_name
        self.ptrs: t.Dict[str | int, "_Node"] = dict()

        self.cb: t.Callable = None
        self.is_leaf = False

    def get_repr(self, key_name="...", indent=0):

        o = ""

        # indentation: Option A
        for ind in range(0, indent, _indent_factor):
            if ind > 0:
                o += " " * (_indent_factor - 1)
            if ind == indent - _indent_factor:
                o += "|- "
            else:
                o += "|"

        # indentation: Option B
        # o += " " * indent

        o += key_name

        if self.is_leaf:
            o += f" -> {self.cb.__qualname__}()"

        if len(self.ptrs):
            o += ":"

        for (k, n) in self.ptrs.items():
            if k == 0:
                key = "/{%s}" % (n.cast_name)
            else:
                key = "/" + k

            o += "\n"
            o += n.get_repr(key, indent + _indent_factor)

        return o

    def __repr__(self):
        return self.get_repr()


class Router:
    def __init__(self):
        self.root = _Node()

    def __repr__(self):
        return repr(self.root)

    def add(self, uri, cb):
        uri_split = uri.split("/")

        if uri_split[0] == "":
            uri_split = uri_split[1:]

        self.root = self._add(uri_split, 0, cb, self.root)

    def _parse_split(self, split: str):

        key: str | int = _Node._default_key
        if split.startswith("{") and split.endswith("}"):
            split = split[1:-1]
            kc = split.split(":")

            if len(kc) > 2:
                raise ValueError(f"Invalid placeholder found in url: {':'.join(kc)}")

            cast_name = kc[1] if len(kc) == 2 else _default_cast_name

        else:
            cast_name = _default_cast_name
            key = split

        return key, cast_name

    def _add(self, uri_split, idx, cb, _node: _Node) -> _Node:

        if idx == len(uri_split):
            _node.is_leaf = True
            _node.cb = cb

        else:
            split = str(uri_split[idx])
            key, cast_name = self._parse_split(split)

            _node.cast_name = cast_name
            _node.ptrs[key] = self._add(
                uri_split,
                idx + 1,
                cb,
                _node.ptrs.get(key, _Node()),
            )

        return _node

    def find(
        self, uri: str
    ) -> t.Union[t.Tuple[HTTPCallback, t.List], t.Tuple[None, None]]:
        uri_split = uri.split("/")
        if uri_split[0] == "":
            uri_split = uri_split[1:]
        return self._find(uri_split, 0, list(), self.root)

    def _find(self, uri_split, idx, args: list, _node: _Node):
        if idx == len(uri_split):
            if not _node or not _node.is_leaf:
                return None, None

            return (_node.cb, args)

        key = uri_split[idx]
        next_node = _node.ptrs.get(key)

        if next_node is None:
            next_node = _node.ptrs.get(_Node._default_key)

            if next_node is None:
                return None, None

            cast = _cast_registry.get(_node.cast_name, _default_cast)
            args.append(cast(key))

        return self._find(uri_split, idx + 1, args, next_node)

    def merge(self, prefix: str, o: "Router"):
        prefix_split = prefix.split("/")
        if prefix_split[0] == "":
            prefix_split = prefix_split[1:]

        self.root = self._merge(prefix_split, 0, o, self.root)

    def _merge(self, prefix_split, idx, o: "Router", _node: _Node):
        if idx == len(prefix_split):
            _node.ptrs.update(o.root.ptrs)
            _node.is_leaf = o.root.is_leaf
            _node.cast_name = o.root.cast_name
            _node.cb = o.root.cb

        else:
            split = str(prefix_split[idx])
            key, cast_name = self._parse_split(split)

            _node.cast_name = cast_name
            _node.ptrs[key] = self._merge(
                prefix_split,
                idx + 1,
                o,
                _node.ptrs.get(key, _Node()),
            )

        return _node


def register_cast(name: str, cast: t.Callable):
    _cast_registry[name] = cast
