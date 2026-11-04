#!/usr/bin/env python3
"""Recorta a logo do Ricardo (arte com fundo quase preto) sem redesenhar nada.

A transparência vem do brilho do pixel (fundo escuro some, folha e prata ficam)
e a cor das bordas é recuperada dividindo pelo alfa (fundo era preto). Máscaras
do círculo e da faixa do nome descartam as folhas decorativas dos cantos.

    python3 tools/logo.py
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "assets/src/logo-original.jpg"
OUT = RAIZ / "assets/img"

CENTRO, RAIO = (632, 362), 345          # emblema (R + aro + folhas)
NOME = (80, 668, 1124, 921)             # RICARDO + AGRONEGÓCIO com os traços


def recorte(img, mascara):
    a = np.asarray(img).astype(np.float32) / 255
    v = a.max(axis=2)
    alfa = np.clip((v - 0.17) / (0.40 - 0.17), 0, 1)
    alfa = alfa * alfa * (3 - 2 * alfa)                     # smoothstep
    alfa *= np.asarray(mascara).astype(np.float32) / 255
    cor = np.clip(a / np.maximum(alfa[..., None], 1e-3), 0, 1)
    cor = np.where(alfa[..., None] > 0.02, cor, 0)
    rgba = np.dstack([cor, alfa])
    return Image.fromarray((rgba * 255).round().astype(np.uint8), "RGBA")


def salvar(im, nome, alturas):
    caixa = im.getbbox()
    im = im.crop(caixa)
    for h in alturas:
        w = round(im.width * h / im.height)
        im.resize((w, h), Image.LANCZOS).save(OUT / f"{nome}-{h}.webp", "WEBP", quality=92, method=6)
    im.save(RAIZ / f"assets/src/{nome}.png")
    return im


def main():
    img = Image.open(SRC).convert("RGB")
    W, H = img.size

    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    cx, cy = CENTRO
    d.ellipse((cx - RAIO, cy - RAIO, cx + RAIO, cy + RAIO), fill=255)
    d.rectangle((0, NOME[1] - 8, W, H), fill=0)          # o círculo encosta no topo do RICARDO: corta ali
    emblema = salvar(recorte(img, m.filter(ImageFilter.GaussianBlur(2))), "logo-emblema", [96, 192, 512])

    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rectangle(NOME, fill=255)
    palavra = salvar(recorte(img, m.filter(ImageFilter.GaussianBlur(2))), "logo-nome", [64, 128])

    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.ellipse((cx - RAIO, cy - RAIO, cx + RAIO, cy + RAIO), fill=255)
    d.rectangle(NOME, fill=255)
    salvar(recorte(img, m.filter(ImageFilter.GaussianBlur(2))), "logo-completa", [240, 480])

    # favicon e ícone: emblema sobre o verde-escuro da marca
    for lado, nome in ((64, "favicon.png"), (180, "apple-touch-icon.png")):
        fundo = Image.new("RGBA", (lado, lado), (8, 26, 15, 255))
        e = emblema.copy(); e.thumbnail((round(lado * .86), round(lado * .86)), Image.LANCZOS)
        fundo.alpha_composite(e, ((lado - e.width) // 2, (lado - e.height) // 2))
        fundo.convert("RGB").save(OUT / nome)
    print("ok", emblema.size, palavra.size)


if __name__ == "__main__":
    main()
