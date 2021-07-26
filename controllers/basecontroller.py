from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
import logging

from sanic_cors import cross_origin


LOGGER = logging.getLogger('python-logstash-logger')

logging.basicConfig(filename='GreenPassAnalyzer.log', filemode='a')


bp = Blueprint("BaseController")

@bp.route("/", methods=['GET', 'OPTIONS'])
async def perform_analysis(req: Request) -> HTTPResponse:
    return response.html("../index.html")

