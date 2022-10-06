from django.core.exceptions import PermissionDenied
from django.db import connections
from django.http import Http404
from rest_framework import exceptions
from rest_framework.exceptions import APIException
from rest_framework.response import Response


class Http400(APIException):
    status_code = 400
    default_detail = "Ошибка операции."


def set_rollback():
    for db in connections.all():
        if db.settings_dict["ATOMIC_REQUESTS"] and db.in_atomic_block:
            db.set_rollback(True)


def custom_exception_handler(exc, context):
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    elif isinstance(exc, Http400):
        headers = {}
        if isinstance(exc, exceptions.APIException):
            headers = {}
            if getattr(exc, "auth_header", None):
                headers["WWW-Authenticate"] = exc.auth_header
            if getattr(exc, "wait", None):
                headers["Retry-After"] = "%d" % exc.wait

            if isinstance(exc.detail, (list, dict)):
                data = exc.detail
            else:
                data = {"errors": exc.detail}
        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)
    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait

        if isinstance(exc.detail, (list, dict)):
            data = exc.detail
        else:
            data = {"detail": exc.detail}

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)
