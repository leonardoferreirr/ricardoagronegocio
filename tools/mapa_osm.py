#!/usr/bin/env python3
"""Desenha o Ceasa-PE e as ruas do Curado (OpenStreetMap) em SVG para "Onde estamos".

Lê tools/osm-ceasa.json (Overpass, `out geom`) e devolve o miolo do SVG em
viewBox 0 0 600 600, com o centro do Ceasa em (300,300). Os galpões aparecem
como blocos; a BR-101 em traço mais forte.
Dados © OpenStreetMap contributors (ODbL): o crédito fica embaixo do mapa.
"""
import json, math
from pathlib import Path

ARQ = Path(__file__).with_name("osm-ceasa.json")
CEASA = (-8.0727405, -34.9458817)       # centro da área "Ceasa" (OSM way 114690727)
MEIO_LAT, MEIO_LON = 0.0115, 0.0116     # meia altura e meia largura do recorte
X0, X1 = 20, 580

MAIORES = {"motorway", "trunk", "primary", "secondary", "trunk_link", "primary_link"}
FORA = {"footway", "path", "steps", "cycleway", "pedestrian", "track"}


def proj(lat, lon):
    x = X0 + (lon - (CEASA[1] - MEIO_LON)) / (2 * MEIO_LON) * (X1 - X0)
    y = X0 + ((CEASA[0] + MEIO_LAT) - lat) / (2 * MEIO_LAT) * (X1 - X0)
    return x, y


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    (ax, ay), (bx, by) = pts[0], pts[-1]
    dx, dy = bx - ax, by - ay
    n = math.hypot(dx, dy) or 1e-9
    i, dmax = 0, 0.0
    for k in range(1, len(pts) - 1):
        px, py = pts[k]
        d = abs(dy * px - dx * py + bx * ay - by * ax) / n
        if d > dmax:
            i, dmax = k, d
    if dmax <= eps:
        return [pts[0], pts[-1]]
    return rdp(pts[:i + 1], eps)[:-1] + rdp(pts[i:], eps)


def caminho(geom, fechar=False, eps=.6):
    pts = [proj(p["lat"], p["lon"]) for p in geom]
    # anel fechado (primeiro = último) colapsa no Douglas-Peucker: polígono vai sem simplificar
    pts = pts[:-1] if fechar and pts[0] == pts[-1] else rdp(pts, eps)
    if len(pts) < 2:
        return ""
    d = "M" + " ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return d + ("Z" if fechar else "")


def mapa():
    d = json.loads(ARQ.read_text())
    ruas, grandes, galpoes, agua, area = [], [], [], [], ""
    for el in d["elements"]:
        t, g = el.get("tags", {}), el.get("geometry")
        if not g:
            continue
        if el["id"] == 114690727:
            area = caminho(g, True, .3)
        elif "building" in t:
            galpoes.append(caminho(g, True, .3))
        elif "waterway" in t:
            agua.append(caminho(g))
        elif t.get("highway") in MAIORES:
            grandes.append(caminho(g))
        elif "highway" in t and t["highway"] not in FORA:
            ruas.append(caminho(g))
    j = lambda xs: " ".join(x for x in xs if x)
    return (f'<g clip-path="url(#quadro)">'
            f'<path class="m-agua" d="{j(agua)}"/>'
            f'<path class="m-rua" d="{j(ruas)}"/>'
            f'<path class="m-via" d="{j(grandes)}"/>'
            f'<path class="m-area" d="{area}"/>'
            f'<path class="m-galpao" d="{j(galpoes)}"/>'
            f'</g>')


if __name__ == "__main__":
    s = mapa()
    print(len(s), "bytes")
