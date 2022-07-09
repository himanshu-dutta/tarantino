from ._types import CastType, HTTPCallback, WSCallback
from .casts import CastRegistry
from .http import HTTPMethods, HTTPRequest, HTTPResponse, HTTPStatusCode
from .imports import t
from .websocket import WSConnection


class Route:
    """`Route` consists of mapping between the `HTTP` methods and their
    respective handlers.

    It also maps `websocket` request to a handler.
    """

    method_names = dir(HTTPMethods) + ["websocket"]

    def __init__(self, path: str):
        self.path = path
        self.handlers: t.Dict[str, HTTPCallback | WSCallback] = dict()

    def __setattr__(self, name, value):
        if name in self.method_names:
            self.handlers[name] = value
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name):
        if name in self.method_names:
            return self.handlers.get(name)
        else:
            raise AttributeError(
                f"Invalid method name: {name}. Allowed methods are:"
                f" {self.method_names}"
            )

    async def not_allowed_handler(self, status_code: int):
        http_method_not_allowed_response = HTTPResponse("", status_code, [])
        return http_method_not_allowed_response

    async def default_options_handler(self):
        headers = list()
        allowed_methods = []

        for method in dir(HTTPMethods):
            if getattr(self, method) is not None:
                allowed_methods.append(method.upper())

        headers = [(b"allow", ", ".join(allowed_methods).encode())]

        return HTTPResponse("", HTTPStatusCode.STATUS_204_NO_CONTENT, headers)

    async def default_handler(
        self, conn_request: HTTPRequest | WSConnection, **kwargs
    ) -> t.Awaitable[HTTPResponse]:
        scope_type = conn_request.scope["type"]
        method_name = conn_request.scope.get("method", "").lower()

        if scope_type == "http":
            if method_name == "options":
                return await self.default_options_handler()
            return await self.not_allowed_handler(
                HTTPStatusCode.STATUS_405_METHOD_NOT_ALLOWED
            )

        elif scope_type == "websocket":
            return await self.not_allowed_handler(HTTPStatusCode.STATUS_403_FORBIDDEN)

        else:
            raise ValueError(f"Invalid scope type: {scope_type}")

    async def __call__(self, conn_request: HTTPRequest | WSConnection, **kwargs):
        method = str(getattr(conn_request, "method", "websocket")).lower()
        handler = getattr(self, method)
        if not handler:
            handler = self.default_handler

        return await handler(conn_request, **kwargs)


class RouterNode:
    """A `RouterNode` consists of three attributes: a `Route` and two dicts.

    The first dict matches the an absolute path segment name, such as,
    `user` in `/api/user/profile`, to a `RouterNode`. The second dict
    maps of `cast` names to `RouterNode`. Example of variable path
    segment is `{user_id:int}` in `/api/user/{user_id:int}`.
    """

    def __init__(self, cast_registry: CastRegistry):
        self.absolute_path_segment_pointers: t.Dict[str, "RouterNode"] = dict()
        self.variable_path_segment_pointers: t.Dict[
            str, t.Tuple[str, "RouterNode"]
        ] = dict()

        self.route: Route | None = None
        self.cast_registry = cast_registry

    @property
    def has_route(self):
        return self.route is not None

    def add_absolute_path_segment(self, segment: str, node: "RouterNode"):
        if self.get_absolute_path_segment(segment):
            raise ValueError(
                f"Already have a node mapped to the path segment: {segment}"
            )

        self.absolute_path_segment_pointers[segment] = node

    def add_variable_path_segment(self, segment: str, node: "RouterNode"):
        var_name, var_cast_name = self.parse_variable_path_segment(segment)

        if self.cast_registry.get(var_cast_name) is None:
            raise ValueError(f"Invalid cast: {var_cast_name}")

        if self.variable_path_segment_pointers.get(var_cast_name):
            raise ValueError(f"Already have a node mapped to the cast: {var_cast_name}")

        self.variable_path_segment_pointers[var_cast_name] = (var_name, node)

    def get_absolute_path_segment(self, segment: str):
        return self.absolute_path_segment_pointers.get(segment)

    def get_variable_path_segment(self, segment: str):
        _, var_cast_name = self.parse_variable_path_segment(segment)
        return self.variable_path_segment_pointers.get(var_cast_name, (None, None))[1]

    def setdefault_absolute_path_segment(self, segment: str, node: "RouterNode"):
        matched_node = self.get_absolute_path_segment(segment)
        if not matched_node:
            matched_node = node
            self.add_absolute_path_segment(segment, node)
        return matched_node

    def setdefault_variable_path_segment(self, segment: str, node: "RouterNode"):
        matched_node = self.get_variable_path_segment(segment)
        if not matched_node:
            matched_node = node
            self.add_variable_path_segment(segment, node)
        return matched_node

    def setdefault(self, segment: str, node: "RouterNode"):
        if self.is_variable_segment(segment):
            return self.setdefault_variable_path_segment(segment, node)
        else:
            return self.setdefault_absolute_path_segment(segment, node)

    def get_path_segment(self, segment: str):
        if self.is_variable_segment(segment):
            return self.get_variable_path_segment(segment)
        else:
            return self.get_absolute_path_segment(segment)

    def match_absolute_path_segment(self, segment: str) -> t.Optional["RouterNode"]:
        return self.absolute_path_segment_pointers.get(segment)

    def match_variable_path_segment(
        self, segment: str
    ) -> t.Tuple[str, t.Any, "RouterNode"] | t.Tuple[None, None, None]:
        for cast_name, (
            var_name,
            node,
        ) in self.variable_path_segment_pointers.items():
            cast = self.cast_registry.get(cast_name)
            if cast.pattern.match(segment):
                var_value = cast.parse(segment)
                return (var_name, var_value, node)

        return (None, None, None)

    def parse_variable_path_segment(self, segment: str) -> t.Tuple[str, str]:
        if not segment.startswith("{") or not segment.endswith("}"):
            raise ValueError(f"Invalid variable path segment: {segment}")
        segment = segment[1:-1]
        segment_splits = segment.split(":")

        if len(segment_splits) == 1:
            var_name, var_cast_name = (
                segment_splits[0],
                self.cast_registry.default_cast_name,
            )
        elif len(segment_splits) == 2:
            var_name, var_cast_name = segment_splits
        else:
            raise ValueError(
                f"Invalid path segment with more than one `:`(colon): {segment}"
            )
        return var_name, var_cast_name

    def is_variable_segment(self, segment: str):
        return (
            segment.startswith("{")
            and segment.endswith("}")
            and len(segment.split(":")) <= 2
        )


class Router:
    def __init__(self):
        self.cast_registry = CastRegistry()
        self.root_node: RouterNode = RouterNode(self.cast_registry)

    def add_route(self, path: str, route: Route):
        path_segments = self.parse_path(path)
        node = self.root_node

        for segment in path_segments:
            node = node.setdefault(segment, RouterNode(self.cast_registry))
        node.route = route

    def get_route(self, path: str):
        path_segments = self.parse_path(path)
        node = self.root_node

        for segment in path_segments:
            node = node.get_path_segment(segment)
            if not node:
                return None

        return node.route

    def setdefault_route(self, path: str, route: Route):
        matched_route = self.get_route(path)
        if not matched_route:
            matched_route = route
            self.add_route(path, route)
        return matched_route

    def match_uri(
        self, uri: str
    ) -> t.Tuple[t.Optional[Route], t.Dict[t.Optional[str], t.Any]] | t.Tuple[
        None, None
    ]:
        uri_segments = self.parse_path(uri)
        node = self.root_node
        kwargs: t.Dict[t.Optional[str], t.Any] = dict()

        for segment in uri_segments:
            next_node = node.match_absolute_path_segment(segment)
            if next_node:
                node = next_node
                continue

            var_name, var_value, next_node = node.match_variable_path_segment(segment)
            if next_node:
                kwargs[var_name] = var_value
                node = next_node
                continue

            return None, None

        return node.route, kwargs

    def merge_router(self, path_prefix: str, o: "Router"):
        path_prefix_segments = self.parse_path(path_prefix)
        node = self.root_node

        for segment in path_prefix_segments[:-1]:
            node = node.setdefault(segment, RouterNode(self.cast_registry))
        node.setdefault(path_prefix_segments[-1], o.root_node)

        self.cast_registry.merge(o.cast_registry)

    def parse_path(self, path: str):
        if path == "":
            return []

        if path.startswith("/"):
            path = path[1:]
        return path.split("/")

    def register_cast(self, cast_name: str, cast: CastType):
        self.cast_registry.register_cast(cast_name, cast)
