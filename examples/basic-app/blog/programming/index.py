import os
from pathlib import Path

from tarantino import SubApp
from tarantino.http import HTTP200Response

subapp = SubApp("/programming")

curr_dir = Path(os.path.dirname(__file__))


def slug_to_title(slug: str):
    splits = slug.split("-")
    splits = [split.capitalize() for split in splits]
    return " ".join(splits)


@subapp.get("/")
async def index(request):
    with open(curr_dir / "index.html") as fl:
        body = fl.read()

    return HTTP200Response(body)


@subapp.get("/{slug:str}")
async def blog(request, slug: str):
    title = slug_to_title(slug)

    body = f"""
    <html>
    <head>
    <title>
    {title}
    </title>
    </head>
    <body>
    <h1>
    {title}
    </h1>
    </body>
    </html>
    """

    return HTTP200Response(body)
