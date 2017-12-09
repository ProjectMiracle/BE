from django.shortcuts import render
from django.http import HttpResponse
from urllib.parse import quote, unquote
import json
import logging
import sys
import traceback

# Create your views here.


def decode_speech(request, *args, **kwargs):
    """
    A decoder that translate a speech into operation code and arguments

    :param request:  text speech
    :return:  operation code and arguments
    """

    _ERROR_POST = {'oper': 99, 'args': []}
    _CT_JSON = "application/json"
    logger = logging.getLogger('django.request')
    errorlog = logging.getLogger('django')
    try:
        logger.debug("POST: " + json.dumps(request.POST))
        if request.method == 'POST':
            value = ["text", unquote(request.POST.get("text"))]
            logger.debug("text: " + value[1])
            response_data = {'oper': 1, 'args': value}
            return HttpResponse(json.dumps(response_data), _CT_JSON)
        else:
            return HttpResponse(json.dumps(_ERROR_POST), _CT_JSON)
    except:
        errorlog.error(sys.exc_info()[0])
        return HttpResponse(json.dumps(_ERROR_POST), _CT_JSON)
