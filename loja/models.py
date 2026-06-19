"""Modelos do Mundo Mágico CM (locação de brinquedos)."""

import uuid

from django.db import models

HORAS_BASE = 4


def calcular_total(valores_base, horas):
    """Total pela regra do negócio: o valor base cobre até 4h; cada hora extra
    custa (valor_base / 4). O desconto é dado manualmente no atendimento."""
    try:
        horas = max(1, int(horas))
    except (TypeError, ValueError):
        horas = 1
    soma = sum(float(v or 0) for v in valores_base)
    extra = max(0, horas - HORAS_BASE)
    return round(soma + extra * (soma / HORAS_BASE), 2)


class Categoria(models.Model):
    nome = models.CharField("nome", max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    ordem = models.IntegerField(default=0)

    class Meta:
        ordering = ["ordem"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def __str__(self):
        return self.nome


class Brinquedo(models.Model):
    HORAS_BASE = HORAS_BASE
    nome = models.CharField(max_length=120)
    descricao = models.TextField("descrição", blank=True, default="")
    valor_ate_4h = models.DecimalField("valor até 4h", max_digits=10, decimal_places=2, default=0)
    imagem_url = models.CharField("imagem (caminho)", max_length=255, blank=True, default="")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True,
                                  blank=True, related_name="brinquedos")
    destaque = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["-valor_ate_4h"]
        verbose_name = "brinquedo"
        verbose_name_plural = "brinquedos"

    def __str__(self):
        return self.nome

    @property
    def valor(self):
        return float(self.valor_ate_4h or 0)

    @property
    def valor_hora_extra(self):
        return round(self.valor / self.HORAS_BASE, 2)


class Reserva(models.Model):
    STATUS = [("pendente", "Pendente"), ("pago", "Pago"), ("cancelado", "Cancelado")]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome_cliente = models.CharField(max_length=120)
    telefone_cliente = models.CharField(max_length=40)
    data_evento = models.DateField()
    hora_inicio = models.TimeField()
    qtd_horas = models.IntegerField(default=1)
    local_evento = models.CharField(max_length=255)
    itens = models.JSONField(default=list)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mensagem_whatsapp = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS, default="pendente")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "reserva"
        verbose_name_plural = "reservas"

    def __str__(self):
        return f"{self.nome_cliente} — {self.data_evento}"


class Depoimento(models.Model):
    nome = models.CharField(max_length=120)
    texto = models.TextField()
    imagem_url = models.CharField(max_length=255, blank=True, default="")
    aprovado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "depoimento"
        verbose_name_plural = "depoimentos"

    def __str__(self):
        return self.nome


class Bloqueio(models.Model):
    """Bloqueio manual de disponibilidade feito pelo administrador."""
    data = models.DateField()
    dia_inteiro = models.BooleanField("dia inteiro", default=True)
    slots = models.IntegerField("locais bloqueados", default=0)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fim = models.TimeField(null=True, blank=True)
    motivo = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["data"]
        verbose_name = "bloqueio"
        verbose_name_plural = "bloqueios"

    def __str__(self):
        return f"Bloqueio {self.data}"
