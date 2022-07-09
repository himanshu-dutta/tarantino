class _HTTPStatusCode:
    STATUS_100_CONTINUE = 100
    STATUS_101_SWITCHING_PROTOCOLS = 101
    STATUS_102_PROCESSING = 102
    STATUS_103_EARLY_HINTS = 103
    STATUS_200_OK = 200
    STATUS_201_CREATED = 201
    STATUS_202_ACCEPTED = 202
    STATUS_203_NON_AUTHORITATIVE_INFORMATION = 203
    STATUS_204_NO_CONTENT = 204
    STATUS_205_RESET_CONTENT = 205
    STATUS_206_PARTIAL_CONTENT = 206
    STATUS_207_MULTI_STATUS = 207
    STATUS_208_ALREADY_REPORTED = 208
    STATUS_226_IM_USED = 226
    STATUS_300_MULTIPLE_CHOICES = 300
    STATUS_301_MOVED_PERMANENTLY = 301
    STATUS_302_FOUND = 302
    STATUS_303_SEE_OTHER = 303
    STATUS_304_NOT_MODIFIED = 304
    STATUS_305_USE_PROXY = 305
    STATUS_306_RESERVED = 306
    STATUS_307_TEMPORARY_REDIRECT = 307
    STATUS_308_PERMANENT_REDIRECT = 308
    STATUS_400_BAD_REQUEST = 400
    STATUS_401_UNAUTHORIZED = 401
    STATUS_402_PAYMENT_REQUIRED = 402
    STATUS_403_FORBIDDEN = 403
    STATUS_404_NOT_FOUND = 404
    STATUS_405_METHOD_NOT_ALLOWED = 405
    STATUS_406_NOT_ACCEPTABLE = 406
    STATUS_407_PROXY_AUTHENTICATION_REQUIRED = 407
    STATUS_408_REQUEST_TIMEOUT = 408
    STATUS_409_CONFLICT = 409
    STATUS_410_GONE = 410
    STATUS_411_LENGTH_REQUIRED = 411
    STATUS_412_PRECONDITION_FAILED = 412
    STATUS_413_REQUEST_ENTITY_TOO_LARGE = 413
    STATUS_414_REQUEST_URI_TOO_LONG = 414
    STATUS_415_UNSUPPORTED_MEDIA_TYPE = 415
    STATUS_416_REQUESTED_RANGE_NOT_SATISFIABLE = 416
    STATUS_417_EXPECTATION_FAILED = 417
    STATUS_418_IM_A_TEAPOT = 418
    STATUS_421_MISDIRECTED_REQUEST = 421
    STATUS_422_UNPROCESSABLE_ENTITY = 422
    STATUS_423_LOCKED = 423
    STATUS_424_FAILED_DEPENDENCY = 424
    STATUS_425_TOO_EARLY = 425
    STATUS_426_UPGRADE_REQUIRED = 426
    STATUS_428_PRECONDITION_REQUIRED = 428
    STATUS_429_TOO_MANY_REQUESTS = 429
    STATUS_431_REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    STATUS_451_UNAVAILABLE_FOR_LEGAL_REASONS = 451
    STATUS_500_INTERNAL_SERVER_ERROR = 500
    STATUS_501_NOT_IMPLEMENTED = 501
    STATUS_502_BAD_GATEWAY = 502
    STATUS_503_SERVICE_UNAVAILABLE = 503
    STATUS_504_GATEWAY_TIMEOUT = 504
    STATUS_505_HTTP_VERSION_NOT_SUPPORTED = 505
    STATUS_506_VARIANT_ALSO_NEGOTIATES = 506
    STATUS_507_INSUFFICIENT_STORAGE = 507
    STATUS_508_LOOP_DETECTED = 508
    STATUS_510_NOT_EXTENDED = 510
    STATUS_511_NETWORK_AUTHENTICATION_REQUIRED = 511

    def get_status_message(self, status_code: int):
        status_codes = [
            attr_name for attr_name in dir(self) if attr_name.startswith("STATUS_")
        ]

        for attr_name in status_codes:
            if getattr(HTTPStatusCode, attr_name) == status_code:
                status = attr_name.split("_")
                status = status[2:]
                return " ".join(status)

        raise ValueError(f"Invalid status code: {status_code}")


class _HTTPMethods:
    _methods = [
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "DELETE",
        "CONNECT",
        "OPTIONS",
        "TRACE",
        "PATCH",
    ]
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    CONNECT = "CONNECT"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    PATCH = "PATCH"

    def __dir__(self):
        return [method.lower() for method in self._methods]


HTTPStatusCode = _HTTPStatusCode()
HTTPMethods = _HTTPMethods()
