from tarantino.imports import re, t
from tarantino.types import CastType


class IntCast:
    pattern = r"^[-+]?[1-9][0-9]*$"

    @staticmethod
    def parse(segment: str) -> int:
        return int(segment)


class FloatCast:
    pattern = r"^[-+]?(?:\d*\.\d+|\d+)$"

    @staticmethod
    def parse(segment: str) -> float:
        return float(segment)


class BoolCast:
    pattern = r"^(true|false)$"

    @staticmethod
    def parse(segment: str) -> bool:
        return segment == "true"


class StrCast:
    pattern = r".*"

    @staticmethod
    def parse(segment: str):
        return segment


class CastRegistry:
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
        assert hasattr(cast, "pattern"), "Cast doesn't have attribute `pattern`"
        assert hasattr(cast, "parse"), "Cast doesn't have attribute `parse`"
        if isinstance(cast.pattern, str):
            cast.pattern = re.compile(cast.pattern)
        self.casts[cast_name] = cast

    def get(self, cast_name: str):
        return self.casts.get(cast_name)

    def merge(self, o: "CastRegistry"):
        self.casts.update(o.casts)
