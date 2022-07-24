from datetime import datetime
from tarantino.types import CastType


class DatetimeCast(CastType):
    pattern = r"^[-+]?[1-9][0-9]*$"

    def parse(ts: str):
        return datetime.utcfromtimestamp(int(ts))

    def to_str(dt: datetime):
        return str(dt.timestamp() * 1000)
