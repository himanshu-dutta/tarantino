from datetime import datetime


class DatetimeCast:
    pattern = r"^[-+]?[1-9][0-9]*$"

    @staticmethod
    def parse(ts: str):
        return datetime.utcfromtimestamp(int(ts))
