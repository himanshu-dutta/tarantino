from tarantino import SubApp
from tarantino.authentication import AuthenticationResponse, Credentials
from tarantino.http import HTTPResponse, HTTPStatusCode

subapp = SubApp(prefix="/login")


@subapp.get("/")
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
        return HTTPResponse("", status=HTTPStatusCode.STATUS_400_BAD_REQUEST)

    creds = Credentials(username=username, name=name, password=password)
    return AuthenticationResponse(request, creds, redirect="/")
