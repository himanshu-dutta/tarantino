from tarantino import SubApp
from tarantino.http import HTTP404Response
from tarantino.authentication import Credentials, AuthenticationResponse

subapp = SubApp(prefix="/login")


@subapp.register_route("")
async def login(request):
    username = request.query_params.get("username")
    password = request.query_params.get("password")
    name = request.query_params.get("name")

    if isinstance(username, list):
        username = username[0]
    if isinstance(name, list):
        name = name[0]
    if isinstance(password, list):
        password = password[0]

    if not username or not password:
        return HTTP404Response("Invalid Login Credentials")

    creds = Credentials(username=username, name=name, password=password)
    return AuthenticationResponse(request, creds, redirect="/")
