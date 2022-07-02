import os
from pathlib import Path

from tarantino import SubApp
from tarantino.http import HTTP200Response

from .programming import index as programming
from .technology import index as technology


subapp = SubApp("/blogs")

subapp.register_subapp(programming.subapp)
subapp.register_subapp(technology.subapp)


curr_dir = Path(os.path.dirname(__file__))


@subapp.register_route("/")
async def index(request):
    with open(curr_dir / "index.html") as fl:
        body = fl.read()

    return HTTP200Response(body)
