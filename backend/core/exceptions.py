from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.views import set_rollback


class Http400(Exception):
    pass


def custom_exception_handler(exc, context):
    response = exception_handler(exc=exc, context=context)
    if isinstance(exc, Http400):
        exc = ValidationError()
        data = {"errors": exc.detail}
        set_rollback()
        return Response(
            data,
            status=exc.status_code,
        )
    return response
