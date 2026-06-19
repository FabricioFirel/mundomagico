from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sobre-nos/", views.sobre, name="sobre"),
    path("contato/", views.contato, name="contato"),
    path("carrinho/", views.carrinho, name="carrinho"),
    path("depoimentos/", views.depoimentos, name="depoimentos"),

    # API
    path("api/brinquedos/", views.api_brinquedos, name="api_brinquedos"),
    path("api/disponibilidade/", views.api_disponibilidade, name="api_disponibilidade"),
    path("api/reservas/", views.api_reservas, name="api_reservas"),

    # Login / painel
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("painel/", views.painel, name="painel"),
    path("painel/agenda/", views.agenda, name="agenda"),

    # Ações do painel
    path("painel/brinquedos/criar/", views.brinquedo_criar, name="brinquedo_criar"),
    path("painel/brinquedos/<int:bid>/editar/", views.brinquedo_editar, name="brinquedo_editar"),
    path("painel/brinquedos/<int:bid>/excluir/", views.brinquedo_excluir, name="brinquedo_excluir"),
    path("painel/reservas/<uuid:rid>/status/", views.reserva_status, name="reserva_status"),
    path("painel/depoimentos/<int:did>/aprovar/", views.depoimento_aprovar, name="depoimento_aprovar"),
    path("painel/depoimentos/<int:did>/excluir/", views.depoimento_excluir, name="depoimento_excluir"),
    path("painel/bloqueios/criar/", views.bloqueio_criar, name="bloqueio_criar"),
    path("painel/bloqueios/<int:bid>/excluir/", views.bloqueio_excluir, name="bloqueio_excluir"),
]
