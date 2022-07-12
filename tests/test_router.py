from tarantino.router import Router
from tarantino.endpoint import Endpoint


def test_absolute_route():
    test_cases = [
        {
            "path": "/user/{user_id:int}",
            "uri": "/user/92342340",
            "kwargs": {"user_id": 92342340},
        },
        {
            "path": "/user/{user_id}",
            "uri": "/user/92342340",
            "kwargs": {"user_id": "92342340"},
        },
        {
            "path": "/abcd/{efg:bool}/hij/{klm:str}/nop/{qrst:int}",
            "uri": "/abcd/false/hij/nmnwerwemnrew/nop/1234",
            "kwargs": {"efg": False, "klm": "nmnwerwemnrew", "qrst": 1234},
        },
    ]

    for test_case in test_cases:
        router = Router()
        path = test_case["path"]
        uri = test_case["uri"]
        kwargs = test_case["kwargs"]
        route = Endpoint(path)

        router.add_endpoint(path, route)

        matched_route, matched_kwargs = router.match_uri(uri)

        assert matched_route == route

        for arg_name in kwargs:
            assert kwargs[arg_name] == matched_kwargs[arg_name]
