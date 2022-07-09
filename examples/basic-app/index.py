import os
from pathlib import Path

import blog.index as blog
import chat.index as chat
import login
import salutation

from tarantino import Tarantino
from tarantino.authentication import authenticate
from tarantino.http import HTTP200Response, HTTPRequest, JSONResponse

app = Tarantino("basic")

curr_dir = Path(os.path.dirname(__file__))


app.register_subapp(salutation.subapp)
app.register_subapp(login.subapp)
app.register_subapp(blog.subapp)
app.register_subapp(chat.subapp)


@app.get("/")
@authenticate
async def index(request: HTTPRequest):

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


@app.get("/json_response/{user_id:str}/records/{record_id:str}")
async def api_response(request: HTTPRequest, user_id: str, record_id: str):

    resp = {
        "params": {"user": user_id, "record": record_id},
        "query": dict(request.query_params),
        "data": {"foo": "bar"},
    }

    return JSONResponse(resp)
