from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from urllib.parse import quote, unquote
import json
import logging
import traceback

# Create your views here.


def decode_speech(request, *args, **kwargs):
    """
    A decoder that translate a speech into operation code and arguments

    :param request:  text speech
    :return:  operation code and arguments
    """

    _ERROR_POST = {"oper": 0, "args": []}
    _CT_JSON = "application/json"
    logger = logging.getLogger('django.request')
    errorlog = logging.getLogger('django')
    try:
        logger.debug("POST: " + json.dumps(request.POST))
        if request.method == 'POST':
            value = settings.SSA.processSentence(unquote(request.POST.get("text")))
            oper = value[0]
            args = value[1:]
            if len(args) > 0:
                args[0] = quote(args[0])
            logger.debug("oper: " + str(oper))
            response_data = {"oper": oper, "args": args}
            return HttpResponse(json.dumps(response_data), _CT_JSON)
        else:
            return HttpResponse(json.dumps(_ERROR_POST), _CT_JSON)
    except:
        errorlog.error(traceback.format_exc())
        return HttpResponse(json.dumps(_ERROR_POST), _CT_JSON)
