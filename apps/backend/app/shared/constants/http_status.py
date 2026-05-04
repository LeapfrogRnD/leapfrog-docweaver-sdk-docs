"""HTTP status codes for consistent responses."""

from http import HTTPStatus as _HTTPStatus


class HTTPStatus:
    """Standard HTTP status codes - wrapper around Python's http.HTTPStatus."""

    OK = _HTTPStatus.OK.value
    CREATED = _HTTPStatus.CREATED.value
    ACCEPTED = _HTTPStatus.ACCEPTED.value
    NO_CONTENT = _HTTPStatus.NO_CONTENT.value

    BAD_REQUEST = _HTTPStatus.BAD_REQUEST.value
    UNAUTHORIZED = _HTTPStatus.UNAUTHORIZED.value
    FORBIDDEN = _HTTPStatus.FORBIDDEN.value
    NOT_FOUND = _HTTPStatus.NOT_FOUND.value
    METHOD_NOT_ALLOWED = _HTTPStatus.METHOD_NOT_ALLOWED.value
    CONFLICT = _HTTPStatus.CONFLICT.value
    PAYLOAD_TOO_LARGE = _HTTPStatus.REQUEST_ENTITY_TOO_LARGE.value
    UNPROCESSABLE_ENTITY = _HTTPStatus.UNPROCESSABLE_ENTITY.value
    TOO_MANY_REQUESTS = _HTTPStatus.TOO_MANY_REQUESTS.value

    INTERNAL_SERVER_ERROR = _HTTPStatus.INTERNAL_SERVER_ERROR.value
    NOT_IMPLEMENTED = _HTTPStatus.NOT_IMPLEMENTED.value
    BAD_GATEWAY = _HTTPStatus.BAD_GATEWAY.value
    SERVICE_UNAVAILABLE = _HTTPStatus.SERVICE_UNAVAILABLE.value
    GATEWAY_TIMEOUT = _HTTPStatus.GATEWAY_TIMEOUT.value
