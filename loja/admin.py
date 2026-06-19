from django.contrib import admin

from .models import Categoria, Brinquedo, Reserva, Depoimento, Bloqueio

admin.site.site_header = "Mundo Mágico CM"
admin.site.site_title = "Mundo Mágico CM"
admin.site.index_title = "Administração"


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug", "ordem")
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(Brinquedo)
class BrinquedoAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "valor_ate_4h", "destaque", "ativo")
    list_filter = ("categoria", "destaque", "ativo")
    list_editable = ("valor_ate_4h", "destaque", "ativo")
    search_fields = ("nome",)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("nome_cliente", "data_evento", "hora_inicio", "local_evento", "valor_total", "status")
    list_filter = ("status", "data_evento")
    list_editable = ("status",)
    search_fields = ("nome_cliente", "telefone_cliente", "local_evento")
    readonly_fields = ("criado_em",)


@admin.register(Depoimento)
class DepoimentoAdmin(admin.ModelAdmin):
    list_display = ("nome", "aprovado", "created_at")
    list_filter = ("aprovado",)
    list_editable = ("aprovado",)
    search_fields = ("nome", "texto")


@admin.register(Bloqueio)
class BloqueioAdmin(admin.ModelAdmin):
    list_display = ("data", "dia_inteiro", "slots", "hora_inicio", "hora_fim", "motivo")
    list_filter = ("dia_inteiro", "data")
