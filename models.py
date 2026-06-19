"""Modelos de dados do Mundo Mágico CM.

Espelha o modelo original (categorias, brinquedos, reservas, depoimentos),
agora em SQLAlchemy para rodar sobre SQLite localmente ou PostgreSQL em
produção, sem mudar o código.
"""

from datetime import datetime, timezone
import uuid

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Categoria(db.Model):
    __tablename__ = "categorias"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    ordem = db.Column(db.Integer, default=0)

    brinquedos = db.relationship("Brinquedo", back_populates="categoria")


class Brinquedo(db.Model):
    __tablename__ = "brinquedos"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, default="")
    # Valor fixo que cobre o uso por até 4 horas (regra do negócio).
    valor_ate_4h = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    imagem_url = db.Column(db.String(255), default="")
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"))
    destaque = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)

    categoria = db.relationship("Categoria", back_populates="brinquedos")

    # Horas inclusas no valor base.
    HORAS_BASE = 4

    @property
    def valor(self) -> float:
        return float(self.valor_ate_4h or 0)

    @property
    def valor_hora_extra(self) -> float:
        """Cada hora além das 4 inclusas custa o valor base dividido por 4."""
        return round(self.valor / self.HORAS_BASE, 2)


class Reserva(db.Model):
    __tablename__ = "reservas"
    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    nome_cliente = db.Column(db.String(120), nullable=False)
    telefone_cliente = db.Column(db.String(40), nullable=False)
    data_evento = db.Column(db.String(20), nullable=False)
    hora_inicio = db.Column(db.String(10), nullable=False)
    qtd_horas = db.Column(db.Integer, nullable=False, default=1)
    local_evento = db.Column(db.String(255), nullable=False)
    itens = db.Column(db.JSON, default=list)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    mensagem_whatsapp = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="pendente")  # pendente | pago | cancelado
    criado_em = db.Column(db.DateTime, default=_now)


HORAS_BASE = 4


def calcular_total(valores_base, horas):
    """Total do pedido pela regra do negócio.

    Cada brinquedo tem um valor fixo que cobre até 4 horas. Cada hora além
    das 4 custa (valor_base / 4). O desconto final é dado manualmente no
    atendimento, então não é aplicado aqui.
    """
    try:
        horas = max(1, int(horas))
    except (TypeError, ValueError):
        horas = 1
    soma = sum(float(v or 0) for v in valores_base)
    extra = max(0, horas - HORAS_BASE)
    return round(soma + extra * (soma / HORAS_BASE), 2)


class Depoimento(db.Model):
    __tablename__ = "depoimentos"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    imagem_url = db.Column(db.String(255), default="")
    aprovado = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=_now)


class Usuario(db.Model):
    """Usuário administrativo, autenticado pelo banco (senha com hash)."""
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(120), default="")
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=_now)

    def definir_senha(self, senha: str) -> None:
        self.senha_hash = generate_password_hash(senha)

    def checar_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha or "")


class Bloqueio(db.Model):
    """Bloqueio manual de disponibilidade feito pelo administrador.

    Pode bloquear o dia inteiro (folga/feriado) ou apenas alguns locais/horários
    daquele dia (ex.: equipe já comprometida em parte do dia).
    """
    __tablename__ = "bloqueios"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(20), nullable=False)
    dia_inteiro = db.Column(db.Boolean, default=True)
    slots = db.Column(db.Integer, default=0)        # locais bloqueados (se não for dia inteiro)
    hora_inicio = db.Column(db.String(10), default="")
    hora_fim = db.Column(db.String(10), default="")
    motivo = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=_now)
