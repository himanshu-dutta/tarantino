from tarantino.imports import t
from tarantino.types import CastType


class IntCast(CastType):
    pattern = r"[-+]?[0-9]+"

    @staticmethod
    def parse(value: str) -> int:
        return int(value)

    @staticmethod
    def to_str(value: int) -> str:
        return str(value)


class FloatCast(CastType):
    pattern = r"[+-]?([0-9]*[.])?[0-9]+"

    @staticmethod
    def parse(value: str) -> float:
        return float(value)

    @staticmethod
    def to_str(value: float) -> str:
        return str(value)


class BoolCast(CastType):
    pattern = r"(true|false)"

    @staticmethod
    def parse(value: str) -> bool:
        return value == "true"

    @staticmethod
    def to_str(value: bool) -> str:
        return "true" if value else "false"


class StrCast(CastType):
    pattern = r"[^/]+"

    @staticmethod
    def parse(value: str) -> str:
        return value

    @staticmethod
    def to_str(value: str) -> str:
        return value


class _CastRegistry:
    """`CastRegistry` is a utility which consists of various casts that can be
    applied to the variable path segments."""

    def __init__(self):
        self.casts: t.Dict[str, CastType] = dict()
        self.setup_default_casts()
        self.default_cast_name = "str"

    def setup_default_casts(self):
        self.register_cast("int", IntCast)
        self.register_cast("float", FloatCast)
        self.register_cast("bool", BoolCast)
        self.register_cast("str", StrCast)

    def register_cast(self, cast_name: str, cast: CastType):
        assert issubclass(cast, CastType)
        self.casts[cast_name] = cast

    def __getitem__(self, name: str):
        return self.casts[name]

    def __setitem__(self, name: str, cast: CastType):
        self.casts[name] = cast

    def get(self, cast_name: str, default: t.Any = None):
        return self.casts.get(cast_name, default)


CastRegistry = _CastRegistry()
