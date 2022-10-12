from rest_framework.validators import ValidationError
import io
from app.models import RecipeIngridient
from core.exceptions import Http400
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.db.models import F, Sum


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


def get_pdf(user, cart):

    buffer = io.BytesIO()
    page = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf'))
    textobject = page.beginText()
    textobject.setTextOrigin(cm, cm)
    textobject.setFont('DejaVuSerif', 14)

    lines = [
        cart.__str__(),
    ]
    cartitems = cart.cart_items.all()
    
    ingridients = RecipeIngridient.objects.filter(
        recipe__cart_items__cart=cart
    ).values(
        ingredient_in=F('ingridient__name'),
        measure=F('ingridient__measurement_unit')
    ).annotate(
        amount=Sum('amount')
    )
    

    for cartitem in cartitems:
        lines.append(cartitem.__str__())
    lines.append('Cписок покупок:')
    
    for ingridient in ingridients:
        lines.append(
            f'{ingridient["ingredient_in"]}: {ingridient["amount"]} {ingridient["measure"]}'
        )

    for line in lines:
        textobject.textLine(line)

    page.drawText(textobject)

    page.showPage()

    page.save()

    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='shopping-cart.pdf',)