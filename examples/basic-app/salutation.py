from datetime import datetime

from casts import DatetimeCast
from tarantino import SubApp
from tarantino.authentication import authenticate
from tarantino.http import HTTP200Response

subapp = SubApp(prefix="/salutations")

subapp.register_cast("date", DatetimeCast)


@subapp.get("/hello/{name:str}")
@authenticate
async def hello(request, name: str):

    creds = request.credentials
    username = getattr(creds, "name", "Anonymous User")

    body = f"""
    <!doctype html>
    <html>
    <body>
    <h1> {username} says hello to {name}!! </h1>
    </body>
    </html>
    """
    return HTTP200Response(body)


@subapp.get("/hello/{from:str}/{to:str}/{on:date}")
async def hello(request, f: str, t: str, on: datetime):

    body = f"""
    <!doctype html>
    <html>
    <body>
    <h1> {f} said to {t} on {on.strftime('%Y-%m-%d')}!! </h1>
    </body>
    </html>
    """

    return HTTP200Response(body)


@subapp.get("/goodbye/{name}")
async def goodbye(request, name: str):

    body = f"""
    <!doctype html>
    <html>
    <body>
    <h1> Goodbye {name}!! </h1>
    </body>
    </html>
    """

    return HTTP200Response(body)
