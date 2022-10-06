from rest_framework.validators import ValidationError

from core.exceptions import Http400


def get_queryset(klass):
    if hasattr(klass, "_default_manager"):
        return klass._default_manager.all()
    return klass


def get_object_or_400(klass, *args, **kwargs):
    queryset = get_queryset(klass)
    if not hasattr(queryset, "get"):
        klass__name = (
            klass.__name__
            if isinstance(klass, type)
            else klass.__class__.__name__
        )
        raise ValueError(
            "First argument to get_object_or_400() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist or (
        TypeError,
        ValueError,
        ValidationError,
    ):
        raise Http400
