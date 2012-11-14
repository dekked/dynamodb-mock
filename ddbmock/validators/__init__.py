# -*- coding: utf-8 -*-

from onctuous import Schema, Invalid
from importlib import import_module
from ddbmock.errors import ValidationException

def dynamodb_api_validate(action, post):
    """ Find validator for ``action`` and run it on ``post``. If no validator
        are found, return False.

        :action: name of the route after translation to underscores
        :post: data to validate
        :return: False when no validator found, True on success
        :raises: any onctuous exception
    """
    try:
        mod = import_module('.{}'.format(action), __name__)
        schema = getattr(mod, 'post')
    except (ImportError, AttributeError):
        return post  # Fixme: should log

    # ignore the 'request_id' key but propagate it
    schema['request_id'] = str

    try:
        validate = Schema(schema, required=True)
        return validate(post)
    except Invalid as e:
        raise ValidationException(str(e.errors))
