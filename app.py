"""Mundo Mágico CM — aplicação Flask.

Locação de brinquedos para festas infantis: catálogo por categoria, carrinho
com orçamento por hora, reserva com envio para o WhatsApp, depoimentos e painel
administrativo. Backend em Python/Flask + SQLAlchemy.
"""

import calendar as cal
from datetime import date, datetime
from functools import wraps
from urllib.parse import quote

from flask import (
    Flask, render_template, request, redirect, url_for, session,
    jsonify, flash, abort,
)

from config import Config
from models import (
    db, Categoria, Brinquedo, Reserva, Depoimento, Bloqueio, Usuario,
    calcular_total, HORAS_BASE,
)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    with app.app_context():
        db.create_all()
        garantir_admin_inicial()

    register_routes(app)
    return app


def garantir_admin_inicial():
    """Cria um usuário admin inicial no banco se ainda não existir nenhum.

    A senha é gravada com hash. As credenciais padrão vêm da configuração e
    devem ser trocadas em produção (ou pelo painel, ao implementar a gestão
    de usuários).
    """
    if Usuario.query.first() is None:
        admin = Usuario(usuario=Config.ADMIN_USER, nome="Administrador", ativo=True)
        admin.definir_senha(Config.ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()


# ---------------------------------------------------------------------------
# Autenticação simples do painel administrativo
# ---------------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def whatsapp_link(mensagem: str) -> str:
    numero = Config.WHATSAPP_NUMBER
    return f"https://wa.me/{numero}?text={quote(mensagem)}"


def eventos_no_dia(data_str: str) -> int:
    """Quantos eventos (locais) já estão marcados para a data (sem cancelados)."""
    return Reserva.query.filter(
        Reserva.data_evento == data_str, Reserva.status != "cancelado"
    ).count()


def slots_bloqueados(data_str: str) -> int:
    """Locais bloqueados manualmente pelo admin na data."""
    total = 0
    for b in Bloqueio.query.filter_by(data=data_str).all():
        total += Config.MAX_EVENTOS_DIA if b.dia_inteiro else (b.slots or 0)
    return total


def slots_livres(data_str: str) -> int:
    ocupados = eventos_no_dia(data_str) + slots_bloqueados(data_str)
    return max(0, Config.MAX_EVENTOS_DIA - ocupados)


def register_routes(app):
    # -------------------- Site público --------------------
    @app.route("/")
    def index():
        categorias = Categoria.query.order_by(Categoria.ordem).all()
        destaques = Brinquedo.query.filter_by(destaque=True, ativo=True).all()
        vitrines = []
        for cat in categorias:
            itens = [b for b in cat.brinquedos if b.ativo]
            if itens:
                vitrines.append((cat, itens))
        depoimentos = (
            Depoimento.query.filter_by(aprovado=True)
            .order_by(Depoimento.created_at.desc()).limit(6).all()
        )
        return render_template("index.html", destaques=destaques,
                               vitrines=vitrines, depoimentos=depoimentos)

    @app.route("/sobre-nos")
    def sobre():
        return render_template("sobre.html")

    @app.route("/contato")
    def contato():
        return render_template("contato.html")

    @app.route("/carrinho")
    def carrinho():
        return render_template("carrinho.html")

    @app.route("/depoimentos", methods=["GET", "POST"])
    def depoimentos():
        if request.method == "POST":
            nome = (request.form.get("nome") or "").strip()
            texto = (request.form.get("texto") or "").strip()
            if not nome or not texto:
                flash("Preencha seu nome e o depoimento.", "erro")
            else:
                db.session.add(Depoimento(nome=nome, texto=texto, aprovado=False))
                db.session.commit()
                flash("Obrigado! Seu depoimento será publicado após aprovação.", "ok")
            return redirect(url_for("depoimentos"))

        aprovados = (
            Depoimento.query.filter_by(aprovado=True)
            .order_by(Depoimento.created_at.desc()).all()
        )
        return render_template("depoimentos.html", depoimentos=aprovados)

    # -------------------- API (catálogo / reserva) --------------------
    @app.route("/api/brinquedos")
    def api_brinquedos():
        itens = Brinquedo.query.filter_by(ativo=True).all()
        return jsonify([
            {"id": b.id, "nome": b.nome, "descricao": b.descricao,
             "valor_ate_4h": b.valor, "valor_hora_extra": b.valor_hora_extra,
             "imagem_url": b.imagem_url,
             "categoria": b.categoria.nome if b.categoria else None,
             "destaque": b.destaque}
            for b in itens
        ])

    @app.route("/api/disponibilidade")
    def api_disponibilidade():
        data_str = (request.args.get("data") or "").strip()
        if not data_str:
            return jsonify({"error": "Informe a data."}), 400
        livres = slots_livres(data_str)
        return jsonify({
            "data": data_str, "capacidade": Config.MAX_EVENTOS_DIA,
            "ocupados": eventos_no_dia(data_str),
            "bloqueados": slots_bloqueados(data_str),
            "livres": livres, "disponivel": livres > 0,
        })

    @app.route("/api/reservas", methods=["POST"])
    def api_reservas():
        dados = request.get_json(force=True, silent=True) or {}
        obrig = ["nome_cliente", "telefone_cliente", "data_evento", "hora_inicio", "qtd_horas"]
        faltando = [c for c in obrig if not str(dados.get(c, "")).strip()]
        itens = dados.get("itens") or []

        # Aceita 1 a 3 locais no mesmo dia (necessidade do locador/locatário).
        locais = dados.get("locais")
        if not locais:
            locais = [dados.get("local_evento", "")]
        locais = [str(l).strip() for l in locais if str(l).strip()]
        locais = locais[:Config.MAX_EVENTOS_DIA]

        if faltando or not itens or not locais:
            return jsonify({"error": "Preencha todos os dados, escolha ao menos um brinquedo e informe o local."}), 400

        data_evento = dados["data_evento"].strip()
        try:
            qtd_horas = max(1, int(dados.get("qtd_horas", 1)))
        except (TypeError, ValueError):
            qtd_horas = 1

        # Verifica a disponibilidade do dia (capacidade de eventos simultâneos).
        livres = slots_livres(data_evento)
        if len(locais) > livres:
            return jsonify({
                "error": f"Sem disponibilidade para {len(locais)} local(is) em {data_evento}. "
                         f"Restam {livres} horário(s) nesse dia.",
                "livres": livres,
            }), 409

        # Total por local, recalculado no servidor (regra de 4h + horas extras).
        valor_local = calcular_total((i.get("valor_ate_4h", 0) for i in itens), qtd_horas)
        valor_total = round(valor_local * len(locais), 2)

        mensagem = montar_mensagem_whatsapp(dados, itens, qtd_horas, locais, valor_local, valor_total)

        ids = []
        for local in locais:
            reserva = Reserva(
                nome_cliente=dados["nome_cliente"].strip(),
                telefone_cliente=dados["telefone_cliente"].strip(),
                data_evento=data_evento,
                hora_inicio=dados["hora_inicio"].strip(),
                qtd_horas=qtd_horas,
                local_evento=local,
                itens=itens,
                valor_total=valor_local,
                mensagem_whatsapp=mensagem,
                status="pendente",
            )
            db.session.add(reserva)
            ids.append(reserva)
        db.session.commit()

        return jsonify({
            "ids": [r.id for r in ids],
            "locais": len(locais),
            "valor_total": valor_total,
            "whatsapp_url": whatsapp_link(mensagem),
        }), 201

    # -------------------- Login / Admin --------------------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            user_input = (request.form.get("usuario") or "").strip()
            pwd = request.form.get("senha") or ""
            usuario = Usuario.query.filter_by(usuario=user_input, ativo=True).first()
            if usuario and usuario.checar_senha(pwd):
                session["admin"] = True
                session["usuario_nome"] = usuario.nome or usuario.usuario
                return redirect(request.args.get("next") or url_for("admin"))
            flash("Usuário ou senha inválidos.", "erro")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.pop("admin", None)
        return redirect(url_for("index"))

    @app.route("/admin")
    @login_required
    def admin():
        brinquedos = Brinquedo.query.order_by(Brinquedo.nome).all()
        reservas = Reserva.query.order_by(Reserva.criado_em.desc()).all()
        pendentes = Depoimento.query.filter_by(aprovado=False).all()
        categorias = Categoria.query.order_by(Categoria.ordem).all()
        receita = sum(float(r.valor_total) for r in reservas if r.status == "pago")
        return render_template("admin.html", brinquedos=brinquedos, reservas=reservas,
                               depoimentos_pendentes=pendentes, categorias=categorias,
                               receita=receita)

    @app.route("/admin/agenda")
    @login_required
    def admin_agenda():
        hoje = date.today()
        try:
            ano = int(request.args.get("ano", hoje.year))
            mes = int(request.args.get("mes", hoje.month))
        except (TypeError, ValueError):
            ano, mes = hoje.year, hoje.month

        prefixo = f"{ano:04d}-{mes:02d}"
        reservas = (
            Reserva.query.filter(Reserva.data_evento.like(prefixo + "%"))
            .order_by(Reserva.hora_inicio).all()
        )
        por_dia = {}
        for r in reservas:
            por_dia.setdefault(r.data_evento, []).append(r)

        bloqueios = Bloqueio.query.filter(Bloqueio.data.like(prefixo + "%")).all()
        bloq_por_dia = {}
        for b in bloqueios:
            bloq_por_dia.setdefault(b.data, []).append(b)

        semanas = cal.Calendar(firstweekday=6).monthdatescalendar(ano, mes)
        nav = {
            "ano_ant": ano - 1 if mes == 1 else ano,
            "mes_ant": 12 if mes == 1 else mes - 1,
            "ano_prox": ano + 1 if mes == 12 else ano,
            "mes_prox": 1 if mes == 12 else mes + 1,
        }
        return render_template(
            "agenda.html", ano=ano, mes=mes, mes_nome=NOMES_MES[mes - 1],
            semanas=semanas, por_dia=por_dia, bloq_por_dia=bloq_por_dia,
            capacidade=Config.MAX_EVENTOS_DIA, hoje=hoje, nav=nav,
            dias_semana=DIAS_SEMANA,
        )

    @app.route("/admin/bloqueios", methods=["POST"])
    @login_required
    def admin_bloqueio_criar():
        data_b = (request.form.get("data") or "").strip()
        if not data_b:
            flash("Informe a data do bloqueio.", "erro")
            return redirect(url_for("admin_agenda"))
        tipo = request.form.get("tipo", "dia")
        dia_inteiro = tipo == "dia"
        try:
            slots = max(1, int(request.form.get("slots", 1)))
        except (TypeError, ValueError):
            slots = 1
        db.session.add(Bloqueio(
            data=data_b,
            dia_inteiro=dia_inteiro,
            slots=0 if dia_inteiro else slots,
            hora_inicio=(request.form.get("hora_inicio") or "").strip(),
            hora_fim=(request.form.get("hora_fim") or "").strip(),
            motivo=(request.form.get("motivo") or "").strip(),
        ))
        db.session.commit()
        flash("Bloqueio adicionado à agenda.", "ok")
        ano_b, mes_b = (data_b.split("-") + ["", ""])[:2]
        return redirect(url_for("admin_agenda", ano=ano_b, mes=mes_b))

    @app.route("/admin/bloqueios/<int:bid>/excluir", methods=["POST"])
    @login_required
    def admin_bloqueio_excluir(bid):
        b = db.session.get(Bloqueio, bid) or abort(404)
        data_b = b.data
        db.session.delete(b)
        db.session.commit()
        flash("Bloqueio removido.", "ok")
        ano_b, mes_b = (data_b.split("-") + ["", ""])[:2]
        return redirect(url_for("admin_agenda", ano=ano_b, mes=mes_b))

    @app.route("/admin/brinquedos", methods=["POST"])
    @login_required
    def admin_brinquedo_criar():
        b = Brinquedo(
            nome=(request.form.get("nome") or "").strip(),
            descricao=(request.form.get("descricao") or "").strip(),
            valor_ate_4h=_num(request.form.get("valor_ate_4h")),
            imagem_url=(request.form.get("imagem_url") or "").strip(),
            categoria_id=_int(request.form.get("categoria_id")),
            destaque=bool(request.form.get("destaque")),
            ativo=True,
        )
        if not b.nome:
            flash("Informe o nome do brinquedo.", "erro")
        else:
            db.session.add(b)
            db.session.commit()
            flash("Brinquedo adicionado.", "ok")
        return redirect(url_for("admin"))

    @app.route("/admin/brinquedos/<int:bid>/editar", methods=["POST"])
    @login_required
    def admin_brinquedo_editar(bid):
        b = db.session.get(Brinquedo, bid) or abort(404)
        b.nome = (request.form.get("nome") or b.nome).strip()
        b.descricao = (request.form.get("descricao") or "").strip()
        b.valor_ate_4h = _num(request.form.get("valor_ate_4h"))
        b.imagem_url = (request.form.get("imagem_url") or "").strip()
        b.categoria_id = _int(request.form.get("categoria_id"))
        b.destaque = bool(request.form.get("destaque"))
        b.ativo = bool(request.form.get("ativo"))
        db.session.commit()
        flash("Brinquedo atualizado.", "ok")
        return redirect(url_for("admin"))

    @app.route("/admin/brinquedos/<int:bid>/excluir", methods=["POST"])
    @login_required
    def admin_brinquedo_excluir(bid):
        b = db.session.get(Brinquedo, bid) or abort(404)
        db.session.delete(b)
        db.session.commit()
        flash("Brinquedo removido.", "ok")
        return redirect(url_for("admin"))

    @app.route("/admin/reservas/<rid>/status", methods=["POST"])
    @login_required
    def admin_reserva_status(rid):
        r = db.session.get(Reserva, rid) or abort(404)
        novo = request.form.get("status")
        if novo in {"pendente", "pago", "cancelado"}:
            r.status = novo
            db.session.commit()
            flash("Status da reserva atualizado.", "ok")
        return redirect(url_for("admin"))

    @app.route("/admin/depoimentos/<int:did>/aprovar", methods=["POST"])
    @login_required
    def admin_depoimento_aprovar(did):
        d = db.session.get(Depoimento, did) or abort(404)
        d.aprovado = True
        db.session.commit()
        flash("Depoimento aprovado.", "ok")
        return redirect(url_for("admin"))

    @app.route("/admin/depoimentos/<int:did>/excluir", methods=["POST"])
    @login_required
    def admin_depoimento_excluir(did):
        d = db.session.get(Depoimento, did) or abort(404)
        db.session.delete(d)
        db.session.commit()
        flash("Depoimento removido.", "ok")
        return redirect(url_for("admin"))

    # Disponibiliza dados da empresa em todos os templates.
    @app.context_processor
    def inject_empresa():
        return {
            "empresa": {
                "nome": Config.EMPRESA_NOME,
                "cidade": Config.EMPRESA_CIDADE,
                "whatsapp": Config.WHATSAPP_NUMBER,
                "instagram": Config.INSTAGRAM_URL,
            }
        }


NOMES_MES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
DIAS_SEMANA = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]


def montar_mensagem_whatsapp(dados, itens, qtd_horas, locais, valor_local, valor_total):
    data = dados.get("data_evento", "")
    data_fmt = "/".join(reversed(data.split("-"))) if "-" in data else data
    horas_extra = max(0, qtd_horas - HORAS_BASE)
    linhas = [
        "*NOVO PEDIDO - MUNDO MÁGICO CM*", "",
        f"*Cliente:* {dados.get('nome_cliente','')}",
        f"*Telefone:* {dados.get('telefone_cliente','')}",
        f"*Data:* {data_fmt}",
        f"*Início:* {dados.get('hora_inicio','')} ({qtd_horas}h de evento)",
    ]
    if len(locais) == 1:
        linhas.append(f"*Local:* {locais[0]}")
    else:
        linhas.append(f"*Locais ({len(locais)}) no mesmo dia:*")
        for i, local in enumerate(locais, 1):
            linhas.append(f"  {i}. {local}")
    linhas += ["", "*BRINQUEDOS SELECIONADOS:*"]
    for i in itens:
        base = float(i.get("valor_ate_4h", 0))
        linhas.append(f"• {i.get('nome','')} (R$ {base:.2f} até 4h)")
    linhas.append("")
    if horas_extra:
        linhas.append(f"_Inclui {horas_extra}h extra(s) além das 4h._")
    if len(locais) > 1:
        linhas.append(f"_Valor por local: R$ {valor_local:.2f} x {len(locais)} locais._")
    linhas.append(f"*VALOR ESTIMADO: R$ {valor_total:.2f}*")
    linhas.append("_Valor final pode ter desconto, combinado no atendimento._")
    return "\n".join(linhas)


def _num(value):
    try:
        return round(float(str(value).replace(",", ".")), 2)
    except (TypeError, ValueError):
        return 0


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


app = create_app()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", host="0.0.0.0", port=port)
