from tarantino import SubApp
from tarantino.http import HTTP200Response, HTTP404Response, HTTPMethods
from tarantino.authentication import authenticate

from datetime import datetime

subapp = SubApp(prefix="/salutations")


@subapp.register_route("/hello/{name:str}")
@authenticate
async def hello(request, name: str):

    if request.method == HTTPMethods.GET:
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

    return HTTP404Response("")


@subapp.register_route("/hello/{from:str}/{to:str}/{on:date}")
async def hello(request, f: str, t: str, on: datetime):

    if request.method == HTTPMethods.GET:
        body = f"""
        <!doctype html>
        <html>
        <body>
        <h1> {f} said to {t} on {on.strftime('%Y-%m-%d')}!! </h1>
        </body>
        </html>
        """

        return HTTP200Response(body)

    return HTTP404Response("Bad Request")


@subapp.register_route("/goodbye/{name}")
async def goodbye(request, name: str):

    if request.method == HTTPMethods.GET:
        body = f"""
        <!doctype html>
        <html>
        <body>
        <h1> Goodbye {name}!! </h1>
        </body>
        </html>
        """

        return HTTP200Response(body)

    return HTTP404Response("")
