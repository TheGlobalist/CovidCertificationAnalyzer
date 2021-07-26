from starter import json_response
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
import logging
import sys
import zlib
import pprint
import io
import PIL.Image
import pyzbar.pyzbar
import base45
import cbor2
from dateutil import parser
from dateutil.relativedelta import relativedelta

from sanic_cors import cross_origin


LOGGER = logging.getLogger('python-logstash-logger')

logging.basicConfig(filename='GreenPassAnalyzer.log', filemode='a')


bp = Blueprint("GreenPassAnalyzer", url_prefix="/analyzer/greenPass/")

@bp.route("/analysis/perform", methods=['POST', 'OPTIONS'])
@cross_origin(bp, automatic_options=False, vary_header=False)
async def perform_analysis(req: Request) -> HTTPResponse:
    """
    Recovers a specific dataset
    :param req: the received request
    :return: an HTTPResponse containing the requested info
    """
    img = PIL.Image.open(io.BytesIO(req.files.get('image').body))
    data = pyzbar.pyzbar.decode(img)
    cert = data[0].data.decode()

    b45data = cert.replace("HC1:", "")

    zlibdata = base45.b45decode(b45data)

    cbordata = zlib.decompress(zlibdata)

    decoded = cbor2.loads(cbordata)

    parsed = cbor2.loads(decoded.value[2])

    last_dose_timestamp = parser.parse(parsed[-260][1]['v'][0]['dt'])

    expiration_if_patient_got_covid = last_dose_timestamp + relativedelta(months=6)

    standard_expiration = last_dose_timestamp + relativedelta(months=9)


    vaccine_name = __detect_vacine_name(parsed[-260][1]['v'][0]['mp'])

    return json_response({'status': 200,
                          'message': 'Success!',
                          'data': {
                              'firstName': parsed[-260][1]['nam']['gnt'],
                              'lastName': parsed[-260][1]['nam']['fnt'],
                              'birthDate': parsed[-260][1]['dob'],
                              'doseNumber': parsed[-260][1]['v'][0]['dn'],
                              'expectedDosesToDo':parsed[-260][1]['v'][0]['sd'],
                              'vaccineName': vaccine_name,
                              'lastDoseTimestamp': parsed[-260][1]['v'][0]['dt'],
                         
                          }})



def __detect_vacine_name(vaccine_code: str):
    """
    Detects the vaccine name
    :param vaccine_code: the received vaccine codename. Possible values are:
            EU/1/21/1529 for Astrazeneca
            EU/1/20/1525 for Johnson & Johnson
            EU/1/20/1528 for Pfizer
            EU/1/20/1507 for Moderna
    :return the code, "translated" to a more human friendly language :). If the code is not in one of these mappings, the code itself is returned
    """
    if vaccine_code == "EU/1/21/1529":
        return "Astrazeneca"
    elif vaccine_code == "EU/1/20/1525":
        return "Johnson & Johnson"
    elif vaccine_code == "EU/1/20/1528":
        return "Pfizer"
    elif vaccine_code == "EU/1/20/1507":
        return "Moderna"
    else:
        return vaccine_code