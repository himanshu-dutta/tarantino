from .error_response import ErrorResponse

default_middlewares = [
    (ErrorResponse()),
]
