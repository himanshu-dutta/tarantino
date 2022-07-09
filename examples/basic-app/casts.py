from datetime import datetime


class DatetimeCast:
    pattern = r"^[-+]?[1-9][0-9]*$"

    @classmethod
    def parse(ts: str):
        return datetime.utcfromtimestamp(int(ts))
