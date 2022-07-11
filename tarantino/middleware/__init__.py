from tarantino.middleware.error_response import ErrorResponse

default_middlewares = [
    (ErrorResponse()),
]
