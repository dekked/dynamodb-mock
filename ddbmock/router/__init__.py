# -*- coding: utf-8 -*-

from importlib import import_module
from ddbmock.utils import req_logger
from ddbmock.errors import InternalFailure
from ddbmock.validators import dynamodb_api_validate
import re, itertools

request_counter = itertools.count()  # atomic counter

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def action_to_route(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()

def router(action, post):
    request_id = str(request_counter.next())  # register the id in the post for it to be accessible in case of exception
    post['request_id'] = request_id
    req_logger.debug("request_id=%s action=%s body=%s", request_id, action, post)

    # Find route
    try:
        target = action_to_route(action)
        mod = import_module('ddbmock.operations.{}'.format(target))
        func = getattr(mod, target)
    except ImportError:
        req_logger.error('request_id=%s action=%s No such action', request_id, action)
        raise InternalFailure("Method: {} does not exist".format(action))

    # Validate the input
    try:
        post = dynamodb_api_validate(target, post)
    except Exception as e:
        req_logger.error('request_id=%s action=%s exception=%s body=%s', request_id, action, type(e).__name__, str(e.args))
        raise

    # Run request and translate engine errors to DynamoDB errors
    try:
        answer = func(post)
        #req_logger.debug("request_id=%s action=%s answer=%s", post['request_id'], action, answer)
        return answer
    except (TypeError, ValueError, KeyError) as e:
        req_logger.error('request_id=%s action=%s exception=%s body=%s', request_id, action, type(e).__name__, str(e.args))
        raise InternalFailure("{}: {}".format(type(e).__name__, str(e.args)))
