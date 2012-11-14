# -*- coding: utf-8 -*-

# pyramid entry point: semantic name
from __future__ import absolute_import

from ddbmock.router import router
from ddbmock.errors import DDBError
from pyramid.response import Response
import json

# wrap routing logic
def pyramid_router(request):
    # extract action
    target = request.headers.get('x-amz-target')
    action = target.split('.', 2)[1] if target is not None else ""

    post = request.json

    # do the job
    try:
        body = router(action, post)
        status = '200 OK'
    except DDBError as e:
        body = e.to_dict()
        status = '{} {}'.format(e.status, e.status_str)

    # prepare output
    response = Response()
    response.body = json.dumps(body)
    response.status = status
    response.content_type = 'application/x-amz-json-1.0'
    response.headers['x-amzn-RequestId'] = post['request_id']  # added by router

    # done
    return response
