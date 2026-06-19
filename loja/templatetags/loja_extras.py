"""Filtros de template do Mundo Mágico CM."""

from django import template

register = template.Library()


@register.filter
def moeda(valor):
    """Formata um número como moeda brasileira: 1234.5 -> 1.234,50."""
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return valor
    inteiro, decimal = f"{v:,.2f}".split(".")
    inteiro = inteiro.replace(",", ".")
    return f"{inteiro},{decimal}"
