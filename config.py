"""Configuração do Mundo Mágico CM (versão Python).

Os valores sensíveis vêm de variáveis de ambiente, com padrões seguros para
desenvolvimento local. Para escalar (ex.: produção com PostgreSQL), basta
definir DATABASE_URL — o restante do código não muda.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "mundo-magico-dev-secret")

    # SQLite local por padrão; troque para postgresql://... em produção.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{DATA_DIR / 'mundomagico.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Dados do negócio (configuráveis sem mexer no código).
    WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "5561991540133")
    EMPRESA_NOME = "Mundo Mágico CM"
    EMPRESA_CIDADE = "Brasília - DF"
    INSTAGRAM_URL = os.environ.get("INSTAGRAM_URL", "https://instagram.com/")

    # Acesso ao painel administrativo (defina ADMIN_PASSWORD em produção).
    ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "mundomagico123")

    # Quantos eventos (locais) a empresa atende no mesmo dia.
    MAX_EVENTOS_DIA = int(os.environ.get("MAX_EVENTOS_DIA", "3"))

    # Horas inclusas no valor base de cada brinquedo.
    HORAS_BASE = 4
