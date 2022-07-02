import os
from pathlib import Path

from tarantino import Tarantino, register_cast
from tarantino.http import (
    HTTPRequest,
    HTTP200Response,
    HTTP404Response,
    JSONResponse,
    HTTPMethods,
)
from tarantino.authentication import authenticate


import salutation, login, casts
import blog.index as blog
import chat.index as chat

app = Tarantino("basic")

curr_dir = Path(os.path.dirname(__file__))

register_cast("date", casts.to_datetime)

app.register_subapp(salutation.subapp)
app.register_subapp(login.subapp)
app.register_subapp(blog.subapp)
app.register_subapp(chat.subapp)


@app.register_route("/")
@authenticate
async def index(request: HTTPRequest):

    if request.method == HTTPMethods.GET:

        creds = request.credentials
        name = getattr(creds, "name", "Anonymous User")

        body = f"""
        <!doctype html>
        <html>
        <body>
        <h1> Hello {name}!! </h1>
        <h2> This is Index Page </h2>
        </body>
        </html>
        """

        return HTTP200Response(body)

    return HTTP404Response("")


@app.register_route("/json_response/{user_id:str}/records/{record_id:str}")
async def api_response(request: HTTPRequest, user_id: str, record_id: str):

    resp = {
        "params": {"user": user_id, "record": record_id},
        "query": dict(request.query_params),
        "data": {"foo": "bar"},
    }

    return JSONResponse(resp)
