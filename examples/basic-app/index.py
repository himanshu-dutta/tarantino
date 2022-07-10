import login
import salutation
import chat.index as chat
import blog.index as blog

from tarantino import Tarantino
from tarantino.authentication import authenticate
from tarantino.middleware import default_middlewares, cors
from tarantino.http import (
    HTTP200Response,
    HTTPRequest,
    JSONResponse,
    HTTPResponse,
    HTTPStatusCode,
)

app = Tarantino(
    "basic",
    middlewares=default_middlewares
    + [
        cors.Cors(
            allow_origins=["http://localhost:8080"],
            allow_headers=["*"],
            allow_credentials=True,
        )
    ],
)


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


@app.post("/")
@authenticate
async def index(request: HTTPRequest):
    body = await request.body(as_str=True)
    print("POST BODY: ", body)
    return HTTP200Response(f"PING BACK THE BODY: {body}")


@app.get("/user/profile/{username}")
@authenticate
async def profile(request: HTTPRequest, username: str):
    creds = request.credentials
    if not hasattr(creds, "username") or getattr(creds, "username") != username:
        return HTTPResponse("", status=HTTPStatusCode.STATUS_401_UNAUTHORIZED)

    body = f"""
    <!doctype html>
    <html>
    <body>
    <h1> Hello {username}!! </h1>
    <h2> This is Profile Page </h2>
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
