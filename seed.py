"""Popula o banco com o catálogo inicial do Mundo Mágico CM.

Os preços e descrições são valores iniciais de demonstração — o dono ajusta
depois pelo painel administrativo. As imagens são o acervo real da empresa.

Uso:
    python seed.py          # popula apenas se o banco estiver vazio
    python seed.py --force  # apaga e recria o catálogo
"""

import sys

from app import app
from models import db, Categoria, Brinquedo, Depoimento

CATEGORIAS = [
    ("Infláveis", "inflaveis", 1),
    ("Mesa", "mesa", 2),
    ("Digitais", "digitais", 3),
]

# (nome, imagem, preço/hora, destaque, descrição) por categoria (slug)
# Catálogo real do Mundo Mágico CM (nomes, preços e descrições originais).
CATALOGO = {
    "inflaveis": [
        ("Castelo", "castelo.jpg", 70.00, True, "O Castelo Inflável transforma a festa em um reino de diversão. Colorido, seguro e super animado para pular e brincar."),
        ("Tobogã Premium", "tobogapremium.jpg", 380.00, True, "Diversão em grande estilo. Gigante, colorido e cheio de emoção, ideal para garantir muita aventura, risadas e momentos inesquecíveis."),
        ("Toboágua", "toboagua.jpg", 180.00, True, "A diversão mais refrescante da festa, sucesso garantido nos dias de calor. As crianças adoram escorregar e curtir essa aventura."),
        ("Futebol de Sabão", "futebolsabao.jpg", 150.00, True, "Diversão e adrenalina garantidas. Escorregue, ria e dispute partidas cheias de diversão e muita bagunça boa."),
        ("Tobogã Piscina", "tobogapiscina.jpg", 160.00, False, "Diversão em dobro. O Mini Tobogã com Piscina de Bolinhas une o melhor dos dois mundos: escorregar e mergulhar em um mar de bolinhas."),
        ("Mult Play Tigrinho", "multplaytigrinho.jpg", 140.00, False, "Aventura e diversão em um só brinquedo. Combina escorregador, obstáculos e muita animação."),
        ("Kid Play Piu-Piu", "kidplaypiupiu.jpg", 130.00, False, "Um espaço inflável cheio de cores, desafios e muita diversão, com escorregador, obstáculos e personagens."),
        ("Alpinismo", "alpinismo.jpg", 110.00, False, "O Alpinismo Inflável é diversão radical. As crianças podem escalar e viver a sensação de uma verdadeira aventura com total segurança."),
        ("Mini Kid Play", "minikidplay.jpg", 95.00, False, "Um espaço inflável cheio de cores e desafios, feito sob medida para os pequenos. Seguro e perfeito para crianças menores."),
        ("Guerra de Cotonete", "guerracontonete.jpg", 90.00, False, "Pura diversão e desafio. Dois participantes duelam em uma base inflável usando cotonetes gigantes."),
        ("Cama Elástica 366", "camaelastica366.jpg", 85.00, False, "Cama Elástica Profissional de 3,66m de diâmetro. Máxima diversão e espaço para pular em segurança."),
        ("Bolão", "bolao.jpg", 80.00, False, "O Bolão Inflável é pura energia. Colorido e gigante, garante muitas risadas enquanto as crianças correm, chutam e brincam."),
        ("Mini Tobogã Jacaré", "minitobogajacare.jpg", 80.00, False, "Diversão que escorrega de alegria. Colorido, seguro e cheio de emoção, garante muitas risadas e momentos inesquecíveis."),
        ("Tombo Legal", "tombolegal.jpg", 75.00, False, "Quem será o próximo a cair? O Tombo Legal é pura diversão e gargalhada. Desafie os amigos e teste o equilíbrio."),
        ("Chute ao Gol", "chuteaogol.jpg", 60.00, False, "Brinquedo inflável que garante diversão e desafios, testando a pontaria dos participantes chutando a bola nos alvos."),
        ("Cama Elástica 244", "camaelastica244.jpg", 60.00, False, "Cama Elástica de 2,44m de diâmetro. Diversão garantida com segurança para todas as idades."),
        ("Piscina de Bolinha Leão", "piscinabolinhaleao.jpg", 60.00, False, "Diversão com o rei da selva. Piscina de Bolinhas Inflável que encanta com cores vibrantes e formato divertido."),
        ("Pula-Pula", "pulapula.jpg", 50.00, False, "Pura energia e diversão. O Mini Pula-Pula Inflável é perfeito para os pequenos se divertirem com segurança, colorido e cheio de alegria."),
        ("Cama Elástica", "camaelastica.jpg", 45.00, False, "A atração que não pode faltar. Diversão garantida com segurança, onde as crianças podem pular e gastar energia."),
        ("Piscina de Bolinha Tradicional", "piscinabolinhatrad.jpg", 40.00, False, "Piscina de bolinha simples, mas essencial para a diversão dos pequenos, segura e colorida."),
    ],
    "mesa": [
        ("Ping-Pong", "pingpong.jpg", 65.00, False, "Diversão e desafios para todas as idades. Com a mesa de Ping Pong do Mundo Mágico, a brincadeira é garantida."),
        ("Air Game", "airgame.jpg", 55.00, False, "O Air Game é pura diversão e desafio. Mesa de aero hockey interativa, onde dois jogadores disputam quem marca mais pontos."),
        ("Mini Sinuca", "minisinuca.jpg", 50.00, False, "Diversão em miniatura. A Sinuquinha do Mundo Mágico é perfeita para as crianças se sentirem verdadeiros campeões de sinuca."),
        ("Totó", "toto.jpg", 45.00, False, "Diversão clássica que nunca sai de moda. O Pebolim do Mundo Mágico garante partidas cheias de risadas e muita disputa saudável."),
        ("Tamancobol", "tamancobol.jpg", 40.00, False, "Tamancobol é um jogo de mesa para duas ou quatro pessoas que simula um jogo de golfe, testando a pontaria."),
        ("Jogo de Argolas", "jogoargolas.jpg", 35.00, False, "Um clássico que nunca sai de moda. As crianças se divertem tentando acertar as argolas no alvo, estimulando a coordenação motora e a concentração."),
    ],
    "digitais": [
        ("Fliperama", "fliperama.jpg", 95.00, True, "Diversão garantida para todas as idades. Leve o Fliperama do Mundo Mágico para o seu evento e reviva os clássicos com muitos jogos, competição e risadas."),
    ],
}

DEPOIMENTOS = [
    ("Ana Carolina", "Alugamos o castelo e o tobogã para o aniversário do meu filho. As crianças amaram e a equipe foi super pontual!", "cliente1.jpg"),
    ("Marcos Vinícius", "Atendimento excelente e brinquedos muito limpos e conservados. Recomendo demais!", "cliente2.jpg"),
    ("Juliana Prado", "Fechamos o pacote pelo WhatsApp em minutos. Festa perfeita, voltaremos a contratar!", "cliente3.jpg"),
]


def seed(force=False):
    with app.app_context():
        if force:
            db.drop_all()  # recria o schema (suporta mudanças de colunas)
        db.create_all()
        if not force and Brinquedo.query.first():
            print("Banco já populado. Use --force para recriar.")
            return

        cats = {}
        for nome, slug, ordem in CATEGORIAS:
            c = Categoria(nome=nome, slug=slug, ordem=ordem)
            db.session.add(c)
            cats[slug] = c
        db.session.flush()

        total = 0
        for slug, itens in CATALOGO.items():
            for nome, img, preco, destaque, desc in itens:
                db.session.add(Brinquedo(
                    nome=nome, descricao=desc, valor_ate_4h=preco,
                    imagem_url=f"img/{img}", categoria_id=cats[slug].id,
                    destaque=destaque, ativo=True,
                ))
                total += 1

        for nome, texto, img in DEPOIMENTOS:
            db.session.add(Depoimento(nome=nome, texto=texto,
                                      imagem_url=f"img/{img}", aprovado=True))

        db.session.commit()
        print(f"Seed concluído: {len(cats)} categorias, {total} brinquedos, {len(DEPOIMENTOS)} depoimentos.")


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
