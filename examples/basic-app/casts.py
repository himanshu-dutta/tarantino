from datetime import datetime


def to_datetime(ts: str):
    return datetime.utcfromtimestamp(int(ts))
