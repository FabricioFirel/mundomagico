# Mundo Mágico CM — versão Python

Reescrita em **Python (Flask)** do site de locação de brinquedos para festas
infantis do Mundo Mágico CM (Brasília-DF). Catálogo por categoria, carrinho com
orçamento por hora, reserva enviada ao WhatsApp, depoimentos e painel
administrativo. Esta é uma **cópia de trabalho**, independente do repositório
original.

## Tecnologias

- Python 3 + Flask
- Flask-SQLAlchemy (banco relacional)
- SQLite local por padrão — pronto para PostgreSQL em produção (basta definir `DATABASE_URL`)
- HTML (Jinja2), CSS moderno e JavaScript

## Estrutura

```text
MundoMagicoCM-Python/
├── app.py            # aplicação Flask e rotas
├── models.py         # modelos (Categoria, Brinquedo, Reserva, Depoimento)
├── config.py         # configuração via variáveis de ambiente
├── seed.py           # popula o catálogo real e depoimentos
├── requirements.txt
├── templates/        # base, index, carrinho, sobre, contato, depoimentos, login, admin
├── static/
│   ├── css/style.css
│   ├── js/           # carrinho.js, pagina-carrinho.js
│   └── img/          # acervo de imagens dos brinquedos
└── data/             # banco SQLite (gerado em tempo de execução)
```

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python seed.py                # popula o catálogo (use --force para recriar)
python app.py                 # abre em http://127.0.0.1:5000
```

## Painel administrativo

- Acesse `/login`. Usuário e senha padrão: `admin` / `mundomagico123`
  (defina `ADMIN_USER` e `ADMIN_PASSWORD` em variáveis de ambiente para produção).
- No painel é possível: gerenciar o catálogo (CRUD de brinquedos), acompanhar e
  mudar o status das reservas (pendente / pago / cancelado) e aprovar depoimentos.

## Configuração (variáveis de ambiente)

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | SQLite local | Troque por `postgresql://...` para escalar |
| `SECRET_KEY` | dev | Chave de sessão (defina em produção) |
| `WHATSAPP_NUMBER` | 5561991540133 | Número que recebe os pedidos |
| `ADMIN_USER` / `ADMIN_PASSWORD` | admin / mundomagico123 | Acesso ao painel |
| `INSTAGRAM_URL` | — | Link do Instagram no rodapé |

## Melhorias em relação à versão original

- Backend próprio em Python (antes era só front-end + Supabase).
- Catálogo, reservas e depoimentos em banco relacional, com painel administrativo funcional.
- Cálculo do orçamento **revalidado no servidor** (não confia no valor enviado pelo navegador).
- Template modernizado e responsivo.
- Pronto para escalar: troca de SQLite para PostgreSQL apenas por variável de ambiente.

> Catálogo (nomes, preços e descrições) recuperado da versão original do projeto.
