from tarantino.casts import CastRegistry
from tarantino.endpoint import Endpoint
from tarantino.imports import re, t
from tarantino.types import CastType

PARAM_PATTERN = re.compile(r"{([a-zA-Z_][a-zA-Z0-9_]*)(:[a-zA-Z_][a-zA-Z0-9_]*)?}")


def compile_path(path: str) -> t.Tuple[re.Pattern[str], str, t.Dict[str, CastType]]:
    path_pattern = "^"
    path_format = ""
    param_casts = dict()
    duplicated_params = set()

    idx = 0

    for match in PARAM_PATTERN.finditer(path):
        param_name, cast_name = match.groups(CastRegistry.default_cast_name)
        cast_name = cast_name.strip(":")

        assert (
            CastRegistry.get(cast_name) is not None
        ), f"Unknown cast name: {cast_name}"
        if param_name in param_casts:
            duplicated_params.add(param_name)

        cast = CastRegistry[cast_name]
        param_casts[param_name] = cast

        path_pattern += re.escape(path[idx : match.start()])
        path_pattern += f"(?P<{param_name}>{cast.pattern})"

        path_format += path[idx : match.start()]
        path_format += f"{param_name}"

        idx = match.end()

    if duplicated_params:
        names = ", ".join(sorted(duplicated_params))
        raise ValueError(f"Found duplicated params: {names} in path: {path}")

    path_pattern += re.escape(path[idx:]) + "$"
    path_format += path[idx:]

    return (
        re.compile(path_pattern),
        path_format,
        param_casts,
    )


class Route:
    def __init__(self, path: str):
        self.path = path
        self._endpoint = None
        self.setup_route()

    @property
    def endpoint(self) -> Endpoint:
        return self._endpoint

    @endpoint.setter
    def endpoint(self, endpoint: Endpoint):
        if self._endpoint is not None:
            assert hasattr(
                self._endpoint, "extend"
            ), "Invalid reassignment of non-extensible endpoint"
            self._endpoint.extend(endpoint)
        else:
            self._endpoint = endpoint

    def setup_route(self):
        (
            self.path_pattern,
            self.path_format,
            self.param_casts,
        ) = compile_path(self.path)

    def append_path(
        self,
        path: str,
        path_pattern: re.Pattern[str],
        path_format: str,
        param_casts: t.Dict[str, CastType],
        suffix: bool = False,
    ):
        """Default behavior is to append prefix."""

        if suffix:
            prefix_path, prefix_path_pattern, prefix_path_format, prefix_param_casts = (
                self.path,
                self.path_pattern,
                self.path_format,
                self.param_casts,
            )
            suffix_path, suffix_path_pattern, suffix_path_format, suffix_param_casts = (
                path,
                path_pattern,
                path_format,
                param_casts,
            )
        else:
            prefix_path, prefix_path_pattern, prefix_path_format, prefix_param_casts = (
                path,
                path_pattern,
                path_format,
                param_casts,
            )
            suffix_path, suffix_path_pattern, suffix_path_format, suffix_param_casts = (
                self.path,
                self.path_pattern,
                self.path_format,
                self.param_casts,
            )

        path_pattern = prefix_path_pattern.pattern.rstrip(
            "$"
        ) + suffix_path_pattern.pattern.lstrip("^")
        path_format = prefix_path_format + suffix_path_format

        param_casts = prefix_param_casts.copy()

        for name, cast in suffix_param_casts.items():
            if name in param_casts:
                raise ValueError(f"Found duplicated params: {name} in param_casts")
            param_casts[name] = cast

        self.path = prefix_path + suffix_path
        self.path_pattern = re.compile(path_pattern)
        self.path_format = path_format
        self.param_casts = param_casts

    def match_uri(
        self, uri: str
    ) -> t.Tuple[Endpoint, t.Dict[str, t.Any]] | t.Tuple[None, None]:
        match = self.path_pattern.match(uri)
        if not match:
            return None, None

        params = match.groupdict()
        for name, value in params.items():
            params[name] = self.param_casts[name].parse(value)

        return self.endpoint, params


class Router:
    def __init__(self):
        self.routes: t.Dict[str, Route] = dict()

    def add_endpoint(self, path: str, endpoint: Endpoint):
        route = self.routes.setdefault(path, Route(path))
        route.endpoint = endpoint

    def get_endpoint(self, path: str, default=None):
        try:
            return self.routes[path].endpoint
        except:
            return default

    def setdefault_endpoint(self, path: str, default: Endpoint = None):
        try:
            return self.routes[path].endpoint
        except:
            self.add_endpoint(path, default)
            return default

    def _add_route(self, route: Route):
        if route.path in self.routes:
            self.routes[route.path].endpoint = route.endpoint
        else:
            self.routes[route.path] = route

    def match_uri(
        self, uri: str
    ) -> t.Tuple[Endpoint, t.Dict[str, t.Any]] | t.Tuple[None, None]:
        for route in self.routes.values():
            endpoint, kwargs = route.match_uri(uri)
            if endpoint:
                return endpoint, kwargs

        return None, None

    def merge_router(self, path_prefix: str, o: "Router"):
        assert not path_prefix.endswith("/")

        (
            prefix_pattern,
            prefix_format,
            prefix_casts,
        ) = compile_path(path_prefix)

        for route in o.routes.values():
            route.append_path(
                path_prefix,
                prefix_pattern,
                prefix_format,
                prefix_casts,
            )
            self._add_route(route)
