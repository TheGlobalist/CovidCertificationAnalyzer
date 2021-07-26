from sanic import Sanic, Blueprint
from sanic.exceptions import SanicException
from typing import Iterable, Any, Optional, Dict
from http import HTTPStatus
import json
from controllers import gpcontroller, basecontroller
from exceptions import exceptions
from sanic.request import Request
from sanic.response import HTTPResponse
import logging
from datetime import date, datetime
import yaml

LOGGER = logging.getLogger(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    """
    JSON encoder class to serialize objects not serializable with the default JSON serializer.
    """

    def default(self, o: Any) -> Any:
        """
        Default serialization of this encoder.
        :param o: the object to be serialized.
        :return: the serialized object.
        """
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        if isinstance(o, Iterable):
            return list(o)
        return super().default(o)


def create_app(blueprints: Iterable[Blueprint] = None) -> Sanic:
    """
    Creates the Sanic application.
    :param blueprints: the Sanic blueprints to register.
    :return: the created Sanic application.
    """

    app = Sanic(__name__)


    @app.exception(exceptions.ApiException)
    async def handle_exception(request: Request, exception: exceptions.ApiException) -> HTTPResponse:
        LOGGER.exception(exception)
        return json_response(
            body={"error_code": exception.error_code, "message": exception.error_message},
            status=exception.status_code,
        )

    @app.exception(SanicException)
    async def handle_unknown_exception(request: Request, exception: SanicException) -> HTTPResponse:
        LOGGER.exception(exception)
        return json_response(
            body={"error_code": exceptions.ApiException.error_code, "message": exceptions.ApiException.error_message},
            status=HTTPStatus(exception.status_code),
        )

    @app.exception(Exception)
    async def handle_bare_exception(request: Request, exception: Exception) -> HTTPResponse:
        LOGGER.exception(exception)
        return json_response(
            body={"error_code": exceptions.ApiException.error_code, "message": exceptions.ApiException.error_message},
            status=exceptions.ApiException.status_code,
        )

    if blueprints is not None:
        if isinstance(blueprints, Iterable):
            for blueprint in blueprints:
                app.blueprint(blueprint)
        else:
            app.blueprint(blueprints)

    return app

def json_response(
    body: Any,
    status: HTTPStatus = HTTPStatus.OK,
    headers: Optional[Dict] = None,
    content_type: str = "application/json; charset=utf-8",
) -> HTTPResponse:
    """
    Creates a JSON to return to the caller with the given arguments.
    :param body: the response body.
    :param status: the response HTTP status.
    :param headers: the response HTTP headers.
    :param content_type: the response content type.
    :return: the resulting HTTPResponse object.
    """
    return HTTPResponse(
        body="" if body is None else json.dumps(body, cls=CustomJSONEncoder),
        status=status.value,
        headers=headers,
        content_type=content_type,
    )

def run_app(sanic_app: Sanic) -> None:
    """
    Utility function to run the sanic application during development.
    :param sanic_app: the Sanic application to run.
    """
    sanic_app.run(
        host="0.0.0.0",
        port="8072"
    )

if __name__ == "__main__":
    sanic_app = create_app(
        blueprints=(gpcontroller.bp)
    )
    sanic_app.static("/", "index.html")
    run_app(sanic_app)
