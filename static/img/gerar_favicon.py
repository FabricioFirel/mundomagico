"""Gera favicons nitidos a partir da mascote.

Recorta a margem transparente, centraliza num fundo branco arredondado
(pra dar contraste na aba escura do navegador) e exporta nos tamanhos
usados por navegadores e celulares.

Uso: python gerar_favicon.py
Saida: favicon.ico (16/32/48), favicon-32.png, apple-touch-icon.png (180)
"""

import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "mundomagicomascote.png")
PAD_RATIO = 0.03           # margem interna minima (mascote quase cheia)


def montar(tamanho: int) -> Image.Image:
    base = Image.open(SRC).convert("RGBA")
    recorte = base.crop(base.getbbox())  # tira a margem transparente

    # Mantem apenas o globo + a cartola: corta os bracos (laterais) e as
    # perninhas/corpo de baixo, deixando so a parte de cima bem grande.
    w, h = recorte.size
    corte_lado = int(w * 0.21)
    corte_baixo = int(h * 0.34)
    recorte = recorte.crop((corte_lado, 0, w - corte_lado, h - corte_baixo))

    # Canvas transparente, mascote preenchendo (cobre o quadro)
    canvas = Image.new("RGBA", (tamanho, tamanho), (0, 0, 0, 0))
    area = int(tamanho * (1 - 2 * PAD_RATIO))
    w, h = recorte.size
    escala = max(area / w, area / h)  # cobre: preenche o maior lado
    novo = recorte.resize((max(1, int(w * escala)), max(1, int(h * escala))), Image.LANCZOS)
    pos = ((tamanho - novo.width) // 2, (tamanho - novo.height) // 2)
    canvas.paste(novo, pos, novo)

    return canvas


def main():
    montar(32).save(os.path.join(HERE, "favicon-32.png"))
    montar(180).save(os.path.join(HERE, "apple-touch-icon.png"))
    # .ico com varios tamanhos (o navegador escolhe o melhor pra aba)
    montar(48).save(
        os.path.join(HERE, "favicon.ico"),
        sizes=[(16, 16), (32, 32), (48, 48)],
    )
    print("Favicons gerados em", HERE)


if __name__ == "__main__":
    main()
