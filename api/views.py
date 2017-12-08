from django.shortcuts import render
from django.http import HttpResponse
import json
import logging
from urllib import quote, unquote

# Create your views here.


def decode_speech(request, *args, **kwargs):
    """
    A decoder that translate a speech into operation code and arguments

    :param request:  text speech
    :return:  operation code and arguments
    """

    _ERROR_POST = {'oper': 99}
    _CT_JSON = "application/json"
    logger = logging.getLogger('django.request')
    errorlog = logging.getLogger('django')
    try:
        logger.debug("POST: " + json.dumps(request.POST))
        if request.method == 'POST':
            value = unquote(request.POST.get("text"))
            logger.debug("text: " + value)
            response_data = {'oper': 1, 'arg1': quote(value)}
            return HttpResponse(json.dumps(response_data), _CT_JSON)
        else:
            return HttpResponse(json.dumps(_ERROR_POST), _CT_JSON)
    except Exception, e:
        errorlog.error(e)
        return HttpResponse(json.dumps(_ERROR_POST), _CT_JSON)
