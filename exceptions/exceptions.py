from http import HTTPStatus

class ApiException(Exception):
    """
    Base exception for any API unexpected behaviour.
    """

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_message = "An unknown error occurred."
    error_code = 500
