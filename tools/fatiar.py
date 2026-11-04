#!/usr/bin/env python3
"""Fotos do site a partir das imagens geradas no ChatGPT (assets/src/geradas/).

- Grades de catálogo (3x2, calhas brancas): acha as calhas, corta os 6 quadros
  e salva assets/img/produtos/<slug>-<lado>.webp.
- Cenas: salva assets/img/fotos/<nome>-<largura>.webp nas larguras do site.

    python3 tools/fatiar.py
"""
from pathlib import Path
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
GER = RAIZ / "assets/src/geradas"
PROD = RAIZ / "assets/img/produtos"
FOTOS = RAIZ / "assets/img/fotos"

GRADES = {
    "ricardo-grade-a.png": ["manga", "uva", "banana", "mamao", "abacaxi", "coco-verde"],
    "ricardo-grade-b.png": ["melancia", "melao", "laranja", "limao", "maracuja", "goiaba"],
    "ricardo-grade-c.png": ["acerola", "caju", "pinha", "graviola", "abacate", "tangerina"],
    "ricardo-grade-d.png": ["alface", "coentro", "cebolinha", "couve", "repolho", "hortela"],
    "ricardo-grade-e.png": ["tomate", "pimentao", "pepino", "chuchu", "jerimum", "quiabo"],
    "ricardo-grade-f.png": ["batata", "batata-doce", "macaxeira", "inhame", "cebola", "cenoura"],
    "ricardo-grade-g.png": ["alho", "maca", "pera", "beterraba", "milho-verde", "feijao-verde"],
}
CENAS = {   # arquivo gerado: (nome no site, larguras)
    "ricardo-01-hero.png": ("campo", (1000, 1672)),
    "ricardo-02-hero-m.png": ("campo-m", (700, 1122)),
    "ricardo-03-ceasa.png": ("ceasa", (1000, 1672)),
    "ricardo-04-porto.png": ("porto", (1000, 1672)),
    "ricardo-05-origem.png": ("origem", (800, 1122)),
    "ricardo-06-pomar.png": ("pomar", (1000, 1672)),
    "ricardo-07-carga.png": ("carga", (1000, 1672)),
    "ricardo-08-packing.png": ("packing", (1000, 1672)),
    "ricardo-09-ceasa-m.png": ("ceasa-m", (700, 1122)),
    "ricardo-10-porto-m.png": ("porto-m", (700, 1122)),
}
LADOS = (320, 560)


def faixas(claro, minimo):
    """Intervalos [a, b) de índices onde `claro` é verdadeiro por pelo menos `minimo` seguidos."""
    out, ini = [], None
    for i, v in enumerate(list(claro) + [False]):
        if v and ini is None:
            ini = i
        elif not v and ini is not None:
            if i - ini >= minimo:
                out.append((ini, i))
            ini = None
    return out


def quadros(img):
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    branco = (a > 243).all(axis=2)
    col = branco.mean(axis=0) > 0.97
    lin = branco.mean(axis=1) > 0.97

    def cortes(mask, total):
        calhas = faixas(mask, 3)
        bordas = [0] + [x for c in calhas for x in c] + [total]
        segs = [(bordas[i], bordas[i + 1]) for i in range(0, len(bordas), 2)]
        return [s for s in segs if s[1] - s[0] > total * 0.15]

    xs, ys = cortes(col, img.width), cortes(lin, img.height)
    if len(xs) != 3 or len(ys) != 2:      # sem calhas visíveis: divide em partes iguais
        xs = [(round(i * img.width / 3), round((i + 1) * img.width / 3)) for i in range(3)]
        ys = [(round(i * img.height / 2), round((i + 1) * img.height / 2)) for i in range(2)]
    return [(x0, y0, x1, y1) for (y0, y1) in ys for (x0, x1) in xs]


def quadrado(img, caixa, folga=6):
    x0, y0, x1, y1 = caixa
    x0, y0, x1, y1 = x0 + folga, y0 + folga, x1 - folga, y1 - folga
    lado = min(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    return img.crop((cx - lado // 2, cy - lado // 2, cx - lado // 2 + lado, cy - lado // 2 + lado))


def main():
    PROD.mkdir(parents=True, exist_ok=True); FOTOS.mkdir(parents=True, exist_ok=True)
    feitos = 0
    for arq, slugs in GRADES.items():
        p = GER / arq
        if not p.exists():
            continue
        img = Image.open(p).convert("RGB")
        for slug, caixa in zip(slugs, quadros(img)):
            q = quadrado(img, caixa)
            for lado in LADOS:
                q.resize((lado, lado), Image.LANCZOS).save(PROD / f"{slug}-{lado}.webp", "WEBP", quality=80, method=6)
            feitos += 1
    for arq, (nome, larguras) in CENAS.items():
        p = GER / arq
        if not p.exists():
            continue
        img = Image.open(p).convert("RGB")
        for w in larguras:
            h = round(img.height * w / img.width)
            img.resize((w, h), Image.LANCZOS).save(FOTOS / f"{nome}-{w}.webp", "WEBP", quality=74, method=6)
    print(f"  {feitos} produtos, cenas: {sorted({n for a, (n, _) in CENAS.items() if (GER / a).exists()})}")


if __name__ == "__main__":
    main()
