from ..imports import warnings


class _WSStatusCode:
    _deprecation_changes = {
        "STATUS_1004_NO_STATUS_RCVD": "STATUS_1005_NO_STATUS_RCVD",
        "STATUS_1005_ABNORMAL_CLOSURE": "STATUS_1006_ABNORMAL_CLOSURE",
    }
    _deprecated = {
        "STATUS_1004_NO_STATUS_RCVD": 1004,
        "STATUS_1005_ABNORMAL_CLOSURE": 1005,
    }

    STATUS_1000_NORMAL_CLOSURE = 1000
    STATUS_1001_GOING_AWAY = 1001
    STATUS_1002_PROTOCOL_ERROR = 1002
    STATUS_1003_UNSUPPORTED_DATA = 1003
    STATUS_1005_NO_STATUS_RCVD = 1005
    STATUS_1006_ABNORMAL_CLOSURE = 1006
    STATUS_1007_INVALID_FRAME_PAYLOAD_DATA = 1007
    STATUS_1008_POLICY_VIOLATION = 1008
    STATUS_1009_MESSAGE_TOO_BIG = 1009
    STATUS_1010_MANDATORY_EXT = 1010
    STATUS_1011_INTERNAL_ERROR = 1011
    STATUS_1012_SERVICE_RESTART = 1012
    STATUS_1013_TRY_AGAIN_LATER = 1013
    STATUS_1014_BAD_GATEWAY = 1014
    STATUS_1015_TLS_HANDSHAKE = 1015

    def __getattr__(self, name: str):
        status = self._deprecated.get(name)
        if status:
            warnings.warn(
                f"'{name}' is deprecated. Use '{self._deprecation_changes[name]}' instead.",
                category=DeprecationWarning,
                stacklevel=3,
            )
            return status
        raise AttributeError(f"Invalid status code: {name}")


WSStatusCode = _WSStatusCode()
