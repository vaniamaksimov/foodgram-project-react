from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler, set_rollback


class Http400Error(Exception):
    pass


def custom_exception_handler(exc, context):
    if isinstance(exc, Http400Error):
        exc = ValidationError()
        data = {"errors": exc.detail}
        set_rollback()
        return Response(
            data,
            status=exc.status_code,
        )
    return exception_handler(exc=exc, context=context)
