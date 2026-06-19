"""Disponibiliza os dados da empresa em todos os templates."""

from django.conf import settings


def empresa(request):
    return {"empresa": settings.EMPRESA}
