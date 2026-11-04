#!/usr/bin/env python3
"""Monta o site da Ricardo Agronegócio (início, empresa, produtos com lista de cotação, atacado,
comércio exterior, parcerias, contato, privacidade) e a ponte /obrigado para o WhatsApp.

    python3 build.py

A copy segue a estrutura que a Karla mandou (OCR em _src/estrutura-ocr.txt). Catálogo e FAQ em
_src/produtos.json e _src/faq.json. Safra = calendário de comercialização do Ceasa-PE.
O CSS vai minificado para dentro do <head>; o site.js leva o hash do conteúdo no nome.
"""
import hashlib, json, re
from datetime import date
from html import escape as e
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).parent
DOMINIO = "https://ricardoagronegocio.vercel.app"
INDEXAR = False                  # True depois da aprovação e do domínio oficial
WHATSAPP = "5561993973723"       # PROVISÓRIO: número da Karla (Plancenter) até o Ricardo passar o comercial
TEL_VER = "+55 61 99397-3723"
CSS, JS = RAIZ / "assets/css/site.css", RAIZ / "assets/js/site.js"
GEO = (-8.0727405, -34.9458817)  # Ceasa-PE (OpenStreetMap)
ENDERECO = "BR-101 Sul, km 70, Curado, Recife, PE"
MAPS = "https://www.google.com/maps/search/?api=1&query=CEASA+Pernambuco+BR-101+Sul+km+70+Curado+Recife"
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

# ------------------------------------------------------------------ ícones (traço fino, 24x24)
I = {
    "folha": '<path d="M5 19c0-8 5-14 15-15-1 10-7 15-15 15z"/><path d="M5 19l8-8"/>',
    "galpao": '<path d="M3 21V9l9-5 9 5v12"/><path d="M7 21v-7h10v7M7 17h10"/>',
    "caminhao": '<path d="M2 6h11v10H2zM13 10h4l4 4v2h-8z"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    "globo": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    "carrinho": '<path d="M3 4h2l2.5 11h11L21 7H6.5"/><circle cx="9" cy="19" r="1.5"/><circle cx="17" cy="19" r="1.5"/>',
    "loja": '<path d="M4 10v10h16V10M3 5h18l-1 5H4z"/><path d="M9 20v-5h6v5"/>',
    "talheres": '<path d="M7 3v8M5 3v5a2 2 0 0 0 4 0V3M7 11v10M17 3c-2 2-2 6 0 8v10"/>',
    "cama": '<path d="M3 18V8M3 14h18v4M21 14v-2a3 3 0 0 0-3-3h-7v5"/><circle cx="7" cy="11" r="1.6"/>',
    "caixas": '<path d="M3 13h8v8H3zM13 13h8v8h-8zM8 3h8v8H8z"/>',
    "predio": '<path d="M4 21V5l8-2v18M12 9l8 2v10M8 8v.01M8 12v.01M8 16v.01M16 14v.01M16 17v.01"/>',
    "lista": '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    "zapbalao": '<path d="M4 20l1.3-3.9A8 8 0 1 1 8 19z"/><path d="M9 10h6M9 13h4"/>',
    "lupa": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "sol": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5"/>',
    "aperto": '<path d="M3 12l4-4 4 2 4-2 6 6-6 4-3-2-3 2-6-6z"/><path d="M11 10l3 3"/>',
    "doc": '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 15h5M10 18h3"/>',
    "pino": '<path d="M12 21s-7-6.5-7-12a7 7 0 0 1 14 0c0 5.5-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    "fechar": '<path d="M6 6l12 12M18 6L6 18"/>',
    "mais": '<path d="M12 5v14M5 12h14"/>',
    "menos": '<path d="M5 12h14"/>',
}


def ic(nome):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{I[nome]}</svg>'


SETA = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2 8h11M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5"/></svg>'
ZAP = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.4.8 3.2.6a2.8 2.8 0 0 0 1.8-1.3 2.3 2.3 0 0 0 .2-1.3c-.1-.1-.3-.2-.6-.3z"/></svg>')


# ------------------------------------------------------------------ utilidades
def minificar(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s*\n\s*", "\n", css)
    css = re.sub(r"\s*([{}:;,>])\s*", r"\1", css)
    css = re.sub(r";}", "}", css)
    return re.sub(r"\n+", "", css).replace("../fonts/", "/assets/fonts/").strip()


def hash_de(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:10] if p.exists() else "0"


def dim(caminho, padrao):
    try:
        from PIL import Image
        with Image.open(RAIZ / caminho) as im:
            return im.size
    except Exception:
        print(f"  ! imagem faltando: {caminho}")
        return padrao


def foto(nome, alt, sizes="100vw", lazy=True, larguras=(1000, 1672), celular=None):
    """<img> (ou <picture> com a versão vertical do celular) a partir de assets/img/fotos/<nome>-<largura>.webp."""
    w, h = dim(f"assets/img/fotos/{nome}-{larguras[-1]}.webp", (larguras[-1], round(larguras[-1] * 9 / 16)))
    srcset = ", ".join(f"/assets/img/fotos/{nome}-{x}.webp {x}w" for x in larguras)
    lz = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    img = (f'<img src="/assets/img/fotos/{nome}-{larguras[-1]}.webp" srcset="{srcset}" sizes="{sizes}" alt="{e(alt)}" '
           f'width="{w}" height="{h}"{lz} decoding="async">')
    if not celular:
        return img
    nm, lm = celular
    dim(f"assets/img/fotos/{nm}-{lm[-1]}.webp", (lm[-1], round(lm[-1] * 1.25)))
    src_m = ", ".join(f"/assets/img/fotos/{nm}-{x}.webp {x}w" for x in lm)
    return f'<picture><source media="(max-width:760px)" srcset="{src_m}" sizes="100vw">{img}</picture>'


def foto_prod(slug, alt, sizes="(max-width:760px) 44vw, 260px", lazy=True):
    return (f'<img src="/assets/img/produtos/{slug}-320.webp" srcset="/assets/img/produtos/{slug}-320.webp 320w, '
            f'/assets/img/produtos/{slug}-560.webp 560w" sizes="{sizes}" alt="{e(alt)}" width="560" height="560"'
            f'{" loading=lazy" if lazy else ""} decoding="async">')


def carregar_json(nome, padrao):
    p = RAIZ / "_src" / nome
    try:
        return json.loads(p.read_text())
    except Exception:
        print(f"  ! sem {nome}")
        return padrao


def btn(txt, href, tipo="verde", seta=True, extra=""):
    return f'<a class="btn btn--{tipo}" href="{href}"{extra}>{e(txt)}{" " + SETA if seta else ""}</a>'


def lista_meses(ms):
    """[1,2,3,9,10] -> 'jan a mar, set e out' (meses seguidos viram intervalo)."""
    if not ms:
        return ""
    ms = sorted(set(ms))
    blocos, ini, ant = [], ms[0], ms[0]
    for m in ms[1:] + [None]:
        if m is not None and m == ant + 1:
            ant = m
            continue
        a, b = MESES[ini - 1][:3], MESES[ant - 1][:3]
        blocos.append(a if ini == ant else (f"{a} e {b}" if ant == ini + 1 else f"{a} a {b}"))
        if m is not None:
            ini = ant = m
    if len(blocos) == 1:
        return blocos[0]
    return ", ".join(blocos[:-1]) + " e " + blocos[-1]


# ------------------------------------------------------------------ copy (estrutura enviada pela Karla em 03/11, 20:03 a 20:47)
MENU = [("Início", "/"), ("Empresa", "/empresa"), ("Produtos", "/produtos"), ("Atacado", "/atacado"),
        ("Comércio Exterior", "/comercio-exterior"), ("Parcerias", "/parcerias"), ("Contato", "/contato")]
SLOGAN = "Do campo para o mercado. Do Brasil para o mundo."
HERO_P = "Conectando produtores, fornecedores, compradores e mercados por meio do agronegócio."
CATS = [  # slug, nome, foto de capa, frase
    ("frutas", "Frutas frescas", "manga", "Da manga do Vale às frutas da estação."),
    ("verduras", "Verduras e folhosas", "alface", "Folhas colhidas para chegar viçosas."),
    ("legumes", "Legumes e hortaliças", "tomate", "O básico de toda cozinha, em volume."),
    ("raizes", "Raízes, tubérculos e bulbos", "macaxeira", "Macaxeira, inhame, batata e cebola."),
    ("complementares", "Produtos agrícolas complementares", "milho-verde", "Milho verde, feijão verde e afins."),
    ("importados", "Importados", "maca", "Maçã, pera e alho de outros mercados."),
]
PERCURSO = [  # foto, título, texto, link
    ("pomar", "Origem", "Qualidade começa na origem.",
     "Relacionamento com produtores e fornecedores, valorizando a procedência e o cuidado de cada colheita.", ("Produção e parcerias", "/parcerias")),
    ("ceasa", "CEASA Pernambuco", "Comercialização no centro do abastecimento.",
     "Atuação na CEASA Pernambuco, com atacado e varejo para diferentes perfis de compradores.", ("Conheça os produtos", "/produtos")),
    ("carga", "Distribuição", "Abastecimento para quem não pode parar.",
     "Fornecimento para mercados, restaurantes, hotéis, distribuidores e compradores empresariais.", ("Atacado e distribuição", "/atacado")),
    ("porto", "Mundo", "Negócios que conectam mercados.",
     "Importação e exportação com cotação, documentação e parceiros, conforme as exigências de cada destino.", ("Comércio exterior", "/comercio-exterior")),
]
COMPRADORES = [("loja", "Mercados e supermercados"), ("talheres", "Restaurantes"), ("cama", "Hotéis"),
               ("caminhao", "Distribuidores"), ("predio", "Compradores empresariais")]
EMPRESA_TXT = [
    "A Ricardo Agronegócio nasce com a proposta de conectar a produção agrícola às oportunidades do mercado, integrando comercialização, distribuição e canais digitais, com visão de expansão para o comércio internacional.",
    "Com presença comercial planejada na CEASA Pernambuco e atuação voltada a diferentes perfis de compradores, a empresa busca desenvolver relações de confiança entre produtores, fornecedores, clientes empresariais e parceiros comerciais.",
    "Nossa visão é construir uma operação de agronegócio preparada para atender o mercado nacional e desenvolver oportunidades de negócios internacionais, de acordo com as capacidades operacionais, os produtos comercializados e as exigências aplicáveis a cada mercado.",
    "Nosso compromisso: qualidade, transparência, responsabilidade comercial e construção de relações duradouras.",
]
POSICIONAMENTO = "Uma trading de negócios do agronegócio, com atuação integrada na comercialização, distribuição, abastecimento e conexão entre mercados."
DIMENSOES = ["Comercialização de produtos agrícolas", "Distribuição e abastecimento de mercados",
             "Desenvolvimento de fornecedores e parcerias produtivas", "Comércio eletrônico e negócios digitais",
             "Importação, exportação e conexões comerciais internacionais"]
VISAO = [
    "Ser uma empresa de referência no agronegócio brasileiro, reconhecida pela excelência comercial, capacidade de conectar produtores e mercados, desenvolvimento de soluções de abastecimento e construção de oportunidades de negócios nacionais e internacionais.",
    "Almejamos construir uma organização sólida, inovadora e sustentável, com presença estratégica na cadeia de valor do agronegócio, ampliando nossa atuação do mercado regional para o nacional e internacional.",
    "Nossa visão é participar ativamente do desenvolvimento do agronegócio, contribuindo para aproximar a produção agrícola dos mercados consumidores e conectar o potencial produtivo brasileiro às oportunidades do mundo.",
]
MISSAO = [
    "Conectar a produção agrícola aos mercados consumidores, desenvolvendo soluções comerciais eficientes e confiáveis por meio da comercialização, distribuição, abastecimento e integração de negócios nacionais e internacionais.",
    "Trabalhamos para aproximar produtores, fornecedores, compradores e parceiros estratégicos, valorizando a origem dos produtos, promovendo relações comerciais transparentes e contribuindo para o desenvolvimento da cadeia produtiva do agronegócio.",
    "Buscamos transformar oportunidades em negócios sustentáveis, oferecendo soluções que agreguem valor aos produtos, fortaleçam os relacionamentos comerciais e ampliem o acesso aos mercados.",
]
VALORES_INTRO = "Na Ricardo Agronegócio, acreditamos que o crescimento sustentável é construído sobre princípios sólidos. Nossos valores orientam nossas decisões, fortalecem nossas relações comerciais e direcionam nossa atuação em toda a cadeia do agronegócio."
VALORES = [
    ("Integridade", "Agimos com ética, honestidade e responsabilidade, conduzindo nossos negócios com respeito aos princípios legais e aos compromissos assumidos."),
    ("Transparência", "Valorizamos a clareza nas informações, a honestidade nas negociações e a comunicação objetiva, construindo relações comerciais pautadas na confiança e na responsabilidade."),
    ("Compromisso com a origem", "Reconhecemos o valor de quem produz. Valorizamos os produtores, fornecedores e todos os envolvidos na cadeia produtiva, respeitando a procedência, o cuidado e a qualidade dos produtos."),
    ("Confiança", "Construímos relacionamentos duradouros por meio da credibilidade, do cumprimento dos compromissos e da segurança em nossas relações comerciais."),
    ("Qualidade", "Buscamos excelência em nossos produtos, serviços e processos, valorizando cada etapa, da origem à entrega ao mercado consumidor."),
    ("Inovação", "Acompanhamos as transformações do agronegócio e buscamos novas tecnologias, soluções e oportunidades para modernizar processos e ampliar nossa competitividade."),
    ("Eficiência", "Trabalhamos com planejamento, organização e responsabilidade para otimizar recursos, aprimorar processos e oferecer soluções comerciais eficientes."),
    ("Empreendedorismo", "Identificamos oportunidades, desenvolvemos soluções e transformamos ideias em negócios por meio de iniciativa, planejamento e capacidade de realização."),
    ("Sustentabilidade e responsabilidade", "Valorizamos o uso consciente dos recursos naturais, a redução de desperdícios e práticas responsáveis que contribuam para o desenvolvimento sustentável do agronegócio."),
    ("Parceria e cooperação", "Acreditamos na força das conexões. Desenvolvemos relações de cooperação com produtores, fornecedores, clientes, colaboradores e parceiros estratégicos, buscando crescimento mútuo."),
    ("Respeito às pessoas", "Reconhecemos o valor das pessoas que fazem parte da cadeia do agronegócio e cultivamos relações pautadas no respeito, na valorização humana e na responsabilidade."),
    ("Visão global", "Pensamos além das fronteiras. Acompanhamos as oportunidades e transformações dos mercados, buscando conectar o potencial do agronegócio brasileiro às possibilidades do comércio internacional."),
]
RICARDO = [
    "Ricardo Romão está à frente do projeto empresarial Ricardo Agronegócio, uma iniciativa voltada ao desenvolvimento de negócios no setor do agronegócio, com perspectiva de atuação na comercialização, distribuição, abastecimento e conexão entre mercados.",
    "Sua proposta empresarial está fundamentada na construção de uma organização capaz de aproximar produtores, fornecedores e compradores, valorizando a qualidade dos produtos e desenvolvendo oportunidades comerciais.",
    "À frente da Ricardo Agronegócio, sua direção está voltada à consolidação de uma estrutura empresarial que integre a presença comercial na CEASA Pernambuco, os canais digitais, a expansão nacional e o desenvolvimento de negócios internacionais.",
    "Sua visão é contribuir para a construção de uma empresa sólida, com capacidade de crescimento, relacionamento estratégico e participação nas oportunidades que movimentam o agronegócio brasileiro.",
]
RICARDO_FRASE = "A Ricardo Agronegócio representa esse propósito: conectar a origem dos produtos aos mercados, desenvolver parcerias e transformar oportunidades comerciais em negócios."
ASSUNTOS = ["Compra na CEASA", "Compra no atacado", "Compra pelo e-commerce", "Fornecimento de produtos",
            "Importação", "Exportação", "Parcerias comerciais"]
COMEX_ITENS = [
    ("caixas", "Categorias de produtos de interesse", "Frutas, hortaliças e produtos agrícolas avaliados conforme a demanda de cada mercado."),
    ("globo", "Compra e venda internacional", "Conexão entre compradores e fornecedores do Brasil e do exterior."),
    ("doc", "Propostas comerciais", "Solicitação de cotações e propostas para importação e exportação."),
    ("aperto", "Negociação", "Negociação com fornecedores e compradores, do primeiro contato ao fechamento."),
    ("lista", "Origem e especificações", "Informações sobre origem, especificações e documentação aplicável a cada destino."),
    ("zapbalao", "Canal dedicado", "Atendimento para negócios internacionais, em português e em inglês."),
]
COMEX_AVISO = ("Os produtos oferecidos para exportação são aqueles que a empresa consegue fornecer e documentar conforme os "
               "requisitos do país de destino. Cada operação é avaliada caso a caso.")
ORIGENS = [  # contexto regional de Pernambuco (Conab, IBGE/PAM 2024), não origem declarada de produto
    ("Vale do São Francisco", "Manga e uva de mesa, polo exportador de Petrolina."),
    ("Vale do Ipojuca e Brejo", "Tomate, com Camocim de São Félix entre os maiores do país."),
    ("Vitória de Santo Antão", "Alface e folhosas para as centrais de abastecimento."),
    ("Mata Norte", "Banana de Vicência e São Vicente Férrer."),
    ("Sertão de Itaparica", "Cebola e melancia de Floresta, Cabrobó e Petrolina."),
    ("Agreste e Zona da Mata", "Abacaxi de Gravatá e Pombos, goiaba e hortaliças."),
]


# ------------------------------------------------------------------ dados
def produtos():
    return carregar_json("produtos.json", [])


def safra_agora(lista, mes):
    return [p for p in lista if mes in (p.get("safra") or [])]


def dados_js(lista):
    """O mínimo que o site.js precisa: nome, unidades, categoria e safra de cada produto."""
    enxuto = [{"s": p["slug"], "n": p["nome"], "u": p.get("unidades") or ["Unidade"], "c": p["categoria"],
               "m": p.get("safra") or []} for p in lista]
    return f'<script type="application/json" id="dados-produtos">{json.dumps(enxuto, ensure_ascii=False, separators=(",", ":"))}</script>'


# ------------------------------------------------------------------ casca
def ld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False, separators=(",", ":"))}</script>'


def org_schema():
    return ld({
        "@context": "https://schema.org", "@type": "LocalBusiness", "name": "Ricardo Agronegócio",
        "slogan": SLOGAN, "description": "Trading do agronegócio na CEASA Pernambuco: frutas, verduras, legumes e hortaliças no atacado e no varejo, distribuição, catálogo com cotação pelo WhatsApp, importação e exportação.",
        "url": DOMINIO + "/", "logo": DOMINIO + "/assets/img/logo-completa-480.webp", "image": DOMINIO + "/assets/img/og-image.jpg",
        "address": {"@type": "PostalAddress", "streetAddress": "BR-101 Sul, km 70, CEASA Pernambuco", "addressLocality": "Recife",
                    "addressRegion": "PE", "postalCode": "50790-640", "addressCountry": "BR"},
        "geo": {"@type": "GeoCoordinates", "latitude": GEO[0], "longitude": GEO[1]},
        "areaServed": ["Recife", "Pernambuco", "Nordeste", "BR"],
        "founder": {"@type": "Person", "name": "Ricardo Romão", "jobTitle": "CEO"},
        "knowsAbout": ["hortifrúti", "frutas", "verduras", "legumes", "atacado", "distribuição", "importação", "exportação"],
    })


def faq_ld(faq):
    if not faq:
        return ""
    return ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q["p"], "acceptedAnswer": {"@type": "Answer", "text": q["r"]}} for q in faq]})


def migalhas(rota, nome):
    if rota == "/":
        return ""
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Início", "item": DOMINIO + "/"},
        {"@type": "ListItem", "position": 2, "name": nome, "item": DOMINIO + rota}]})


def marca(cls="marca"):
    return (f'<a class="{cls}" href="/" aria-label="Ricardo Agronegócio, início">'
            f'<img class="marca__r" src="/assets/img/logo-emblema-96.webp" srcset="/assets/img/logo-emblema-96.webp 1x, /assets/img/logo-emblema-192.webp 2x" alt="" width="{dim("assets/img/logo-emblema-96.webp", (108, 96))[0]}" height="96">'
            f'<img class="marca__nome" src="/assets/img/logo-nome-64.webp" srcset="/assets/img/logo-nome-64.webp 1x, /assets/img/logo-nome-128.webp 2x" alt="Ricardo Agronegócio" width="{dim("assets/img/logo-nome-64.webp", (268, 64))[0]}" height="64"></a>')


def pagina(titulo, desc, corpo, rota="/", preload="", robots=None, casca=True, extra_ld="", nome_rota="", lista=None):
    robots = robots or ("index,follow" if INDEXAR else "noindex,nofollow")
    itens = "".join(f'<a href="{h}"{" aria-current=page" if h == rota or (h != "/" and rota.startswith(h)) else ""}>{n}</a>' for n, h in MENU)
    topo = f'''<header class="top"><div class="wrap top__in">
  {marca()}
  <nav class="nav" id="nav" aria-label="Principal">{itens}<a class="btn btn--verde" href="/contato#cotacao">Solicitar cotação</a></nav>
  <button class="burger" type="button" aria-label="Abrir menu" aria-expanded="false" aria-controls="nav"><span></span><span></span></button>
</div></header>''' if casca else ""
    rodape = f'''<footer class="rod"><div class="wrap">
  <div class="rod__grid">
    <div class="rod__marca"><img src="/assets/img/logo-completa-240.webp" srcset="/assets/img/logo-completa-240.webp 1x, /assets/img/logo-completa-480.webp 2x" alt="Ricardo Agronegócio" width="{dim("assets/img/logo-completa-240.webp", (300, 240))[0]}" height="240" loading="lazy">
      <p class="rod__frase">{SLOGAN}</p></div>
    <div class="rod__col"><h2>Navegue</h2>{"".join(f'<a href="{h}">{n}</a>' for n, h in MENU[1:])}</div>
    <div class="rod__col"><h2>Atendimento</h2><a href="/obrigado?c=rodape">WhatsApp {TEL_VER}</a><a href="{MAPS}" target="_blank" rel="noopener">CEASA Pernambuco<br>{ENDERECO}</a><a href="/privacidade">Política de privacidade</a></div>
  </div>
  <p class="rod__fim">© {date.today().year} Ricardo Agronegócio. Todos os direitos reservados.</p>
</div></footer>
<a class="zap" href="/obrigado?c=flutuante" aria-label="Falar pelo WhatsApp">{ZAP}</a>''' if casca else ""
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(titulo)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{DOMINIO}{rota}">
<meta name="theme-color" content="#07160D">
<meta property="og:type" content="website"><meta property="og:locale" content="pt_BR"><meta property="og:site_name" content="Ricardo Agronegócio">
<meta property="og:title" content="{e(titulo)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{DOMINIO}{rota}">
<meta property="og:image" content="{DOMINIO}/assets/img/og-image.jpg"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/img/favicon.png" type="image/png"><link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/poppins-300.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/poppins-500.woff2" as="font" type="font/woff2" crossorigin>
{preload}
<script>document.documentElement.classList.add('js')</script>
<style>{minificar(CSS.read_text())}</style>
{org_schema() if rota == "/" else ""}{migalhas(rota, nome_rota)}{extra_ld}
</head>
<body>
{topo}
<main>
{corpo}
</main>
{rodape}
{dados_js(lista) if lista else ""}
<script src="/assets/js/site.js?v={hash_de(JS)}" defer></script>
</body>
</html>'''


def preload_foto(nome, celular=None):
    desk = (f'<link rel="preload" as="image" media="(min-width:761px)" imagesrcset="/assets/img/fotos/{nome}-1000.webp 1000w, '
            f'/assets/img/fotos/{nome}-1672.webp 1672w" imagesizes="100vw" fetchpriority="high">')
    if not celular:
        return desk.replace(' media="(min-width:761px)"', "")
    return desk + (f'\n<link rel="preload" as="image" media="(max-width:760px)" imagesrcset="/assets/img/fotos/{celular}-700.webp 700w, '
                   f'/assets/img/fotos/{celular}-1122.webp 1122w" imagesizes="100vw" fetchpriority="high">')


def pag_topo(titulo, texto, img, ctas="", celular=None):
    p = f"<p>{e(texto)}</p>" if texto else ""
    return (f'<section class="pagtopo"><div class="pagtopo__bg">{foto(img, "", lazy=False, celular=celular)}</div>'
            f'<div class="wrap"><div class="pagtopo__txt"><h1>{titulo}</h1>{p}{ctas}</div></div></section>')


def cta_final(titulo="Qual o próximo pedido do seu negócio?", texto="Consulte disponibilidade, volumes e condições comerciais com a nossa equipe."):
    return f'''<section class="final" id="fale"><div class="final__bg">{foto("campo", "")}</div><div class="wrap"><div class="final__txt rv">
  <h2>{titulo}</h2><p>{e(texto)}</p>
  <div class="ctas">{btn("Solicitar cotação", "/contato#cotacao")}{btn("Falar no WhatsApp", "/obrigado?c=cta", "linha", False)}</div>
</div></div></section>'''


def faq_sec(faq):
    if not faq:
        return ""
    itens = "".join(f'<details class="faq__item"><summary>{e(q["p"])}<span aria-hidden="true">{ic("mais")}</span></summary><p>{e(q["r"])}</p></details>' for q in faq)
    return f'''<section class="sec sec--creme" id="duvidas"><div class="wrap faq">
  <div class="faq__cab rv"><h2>Perguntas frequentes</h2></div>
  <div class="faq__lista rv" data-d="1">{itens}</div>
</div></section>'''


def onde_sec():
    import sys
    sys.path.insert(0, str(RAIZ / "tools"))
    from mapa_osm import mapa
    return f'''<section class="sec onde" id="onde-estamos"><div class="wrap onde__grid">
  <div class="onde__mapa rv"><svg viewBox="0 0 600 600" role="img" aria-label="Mapa da CEASA Pernambuco, no Curado, com os galpões e a BR-101">
    <defs><clipPath id="quadro"><rect x="20" y="20" width="560" height="560" rx="18"/></clipPath>
    <radialGradient id="vinheta" cx="300" cy="300" r="300" gradientUnits="userSpaceOnUse"><stop offset=".6" stop-color="#07160D" stop-opacity="0"/><stop offset="1" stop-color="#07160D" stop-opacity=".9"/></radialGradient></defs>
    {mapa()}
    <rect x="20" y="20" width="560" height="560" rx="18" fill="url(#vinheta)"/>
    <g class="m-pino" transform="translate(300 290)"><circle class="m-pulso" r="26"/><circle class="m-pulso" r="26"/><circle r="7"/></g>
  </svg><p class="onde__credito">Mapa: © colaboradores do OpenStreetMap</p></div>
  <div class="onde__txt rv" data-d="1">
    <h2>Onde estamos</h2>
    <p class="onde__lugar">CEASA Pernambuco</p>
    <p>{ENDERECO}, CEP 50790-640.</p>
    <p>Atendimento comercial para compradores, fornecedores, importadores e exportadores. Consulte o horário e a localização do box pelo WhatsApp antes de ir.</p>
    <div class="ctas">{btn("Como chegar", MAPS, "verde", True, ' target="_blank" rel="noopener"')}{btn("Falar no WhatsApp", "/obrigado?c=onde", "linha", False)}</div>
  </div>
</div></section>'''


def form_campos(campos, assunto_padrao=""):
    """campos: (tipo, nome, rótulo, extras). tipo: txt, tel, mail, area, sel:<op1|op2>."""
    out = []
    for i, (tipo, nome, rot, ext) in enumerate(campos):
        cid = f"f-{re.sub(r'[^a-z0-9]', '', nome.lower())[:10]}{i}"
        cheio = " campo--cheio" if "cheio" in ext else ""
        req = " required" if "req" in ext else ""
        if tipo == "area":
            ctl = f'<textarea id="{cid}" name="{e(nome)}" rows="3"{req}></textarea>'
        elif tipo.startswith("sel:"):
            ops = "".join(f'<option{" selected" if o == assunto_padrao else ""}>{e(o)}</option>' for o in tipo[4:].split("|"))
            ctl = f'<select id="{cid}" name="{e(nome)}"{req}><option value=""{"" if assunto_padrao else " selected"} disabled>Escolha</option>{ops}</select>'
        else:
            t = {"txt": "text", "tel": "tel", "mail": "email"}[tipo]
            extra = ' inputmode="tel" autocomplete="tel"' if tipo == "tel" else (' autocomplete="email"' if tipo == "mail" else "")
            ctl = f'<input id="{cid}" name="{e(nome)}" type="{t}"{extra}{req}>'
        out.append(f'<div class="campo{cheio}"><label for="{cid}">{e(rot)}</label>{ctl}</div>')
    return "".join(out)


def formulario(campos, abertura, rotulo="Enviar pelo WhatsApp", assunto=""):
    return f'''<form class="form" data-form data-abertura="{e(abertura)}" novalidate>
    {form_campos(campos, assunto)}
    <div class="form__mel" aria-hidden="true"><input name="site" tabindex="-1" autocomplete="off"></div>
    <label class="aceite"><input type="checkbox" name="aceite" required> Concordo com o uso dos meus dados para receber o retorno da Ricardo Agronegócio, conforme a <a href="/privacidade">Política de Privacidade</a> (LGPD).</label>
    <button class="btn btn--verde" type="submit">{e(rotulo)} {SETA}</button>
  </form>'''


# ------------------------------------------------------------------ peças da home
def percurso_sec():
    fotos = "".join(f'<div class="perc__foto{" on" if i == 0 else ""}" data-foto="{i}">{foto(f, "", "100vw")}</div>' for i, (f, *_r) in enumerate(PERCURSO))
    etapas = "".join(f'''<article class="perc__etapa{" on" if i == 0 else ""}" data-etapa="{i}">
      <div class="perc__m">{foto(f, "", "92vw", larguras=(1000,))}</div>
      <p class="perc__n">{i + 1:02d}</p><h3>{e(t)}</h3><p class="perc__frase">{e(fr)}</p><p>{e(tx)}</p>{btn(lk[0], lk[1], "linha")}
    </article>''' for i, (f, t, fr, tx, lk) in enumerate(PERCURSO))
    marcos = "".join(f'<li data-marco="{i}"><span></span>{e(t)}</li>' for i, (_, t, *_r) in enumerate(PERCURSO))
    return f'''<section class="perc" id="percurso" data-perc>
  <div class="perc__palco">
    <div class="perc__fotos" aria-hidden="true">{fotos}</div>
    <div class="wrap perc__in">
      <h2 class="perc__titulo">Do campo para o mercado.<br><span>Do Brasil para o mundo.</span></h2>
      <div class="perc__etapas">{etapas}</div>
      <ol class="perc__trilha" aria-hidden="true"><i><b></b></i>{marcos}</ol>
    </div>
  </div>
</section>'''


def safra_faixa(lista, mes):
    """Faixa abaixo do topo: o que está em boa oferta no mês (o JS troca se o mês do visitante for outro)."""
    ag = safra_agora(lista, mes) or lista[:10]
    itens = "".join(f'<a class="safra__item" href="/produtos#{p["slug"]}">{foto_prod(p["slug"], "", "64px")}<span>{e(p["nome"])}</span></a>' for p in ag)
    return f'''<section class="safra" aria-label="Produtos em boa oferta neste mês" data-safra-faixa>
  <div class="safra__rot"><span>Na safra em</span><b data-mes>{MESES[mes - 1]}</b></div>
  <div class="safra__trilho"><div class="safra__t" data-safra-t>{itens * 2}</div></div>
</section>'''


def categorias_sec(lista):
    cont = {c: sum(1 for p in lista if p["categoria"] == c) for c, *_ in CATS}
    cards = "".join(f'''<a class="cat rv" data-d="{i % 3}" href="/produtos#cat-{c}">
      <div class="cat__foto">{foto_prod(f, "", "(max-width:760px) 92vw, 30vw")}</div>
      <div class="cat__txt"><h3>{e(n)}</h3><p>{e(fr)}</p><span class="cat__n">{cont.get(c, 0)} produtos {SETA}</span></div>
    </a>''' for i, (c, n, f, fr) in enumerate(CATS))
    return f'''<section class="sec sec--creme" id="produtos"><div class="wrap">
  <div class="cab rv"><h2>Produtos frescos para o seu negócio.</h2></div>
  <div class="cats">{cards}</div>
  <div class="fim">{btn("Ver o catálogo completo", "/produtos", "escuro")}</div>
</div></section>'''


def calendario_sec(lista, mes, cab=True):
    abas = "".join(f'<button type="button" role="tab" data-mes-aba="{i + 1}" aria-selected="{"true" if i + 1 == mes else "false"}">{m[:3]}</button>' for i, m in enumerate(MESES))
    ag = safra_agora(lista, mes)
    itens = "".join(f'<a class="cal__item" href="/produtos#{p["slug"]}">{foto_prod(p["slug"], "", "96px")}<span>{e(p["nome"])}</span></a>' for p in ag)
    titulo = '<div class="cab rv"><h2>O que está na safra.</h2><p>Época de boa oferta e preço mais baixo de cada produto no Ceasa-PE.</p></div>' if cab else ""
    return f'''<section class="sec cal" id="safra" data-cal><div class="wrap">
  {titulo}
  <div class="cal__abas" role="tablist" aria-label="Meses">{abas}</div>
  <div class="cal__grade" data-cal-grade aria-live="polite">{itens}</div>
  <p class="cal__fonte">Fonte: calendário de comercialização da CEASA Pernambuco. A oferta real varia com o clima e a colheita de cada ano.</p>
</div></section>'''


def home(lista, faq, mes):
    compradores = "".join(f'<li>{ic(i)}<span>{e(t)}</span></li>' for i, t in COMPRADORES)
    origens = "".join(f'<li class="rv" data-d="{i % 3}"><h3>{e(r)}</h3><p>{e(t)}</p></li>' for i, (r, t) in enumerate(ORIGENS))
    lista_demo = "".join(f'<li>{foto_prod(s, "", "40px")}<span>{n}</span><b>{q}</b></li>' for s, n, q in
                         [("manga", "Manga", "10 caixas"), ("tomate", "Tomate", "8 caixas"), ("alface", "Alface", "30 unidades"), ("macaxeira", "Macaxeira", "2 sacos")])
    corpo = f'''
<section class="capa">
  <div class="capa__bg" data-paralaxe>{foto("campo", "Plantação de hortaliças ao amanhecer no Nordeste", lazy=False, celular=("campo-m", (700, 1122)))}</div>
  <div class="wrap"><div class="capa__txt">
    <h1>Do campo<br>para o mundo.</h1>
    <p>{e(HERO_P)}</p>
    <div class="ctas">{btn("Solicitar cotação", "/contato#cotacao")}{btn("Conheça nossos produtos", "/produtos", "linha", False)}</div>
  </div></div>
</section>
{safra_faixa(lista, mes)}
{percurso_sec()}
{categorias_sec(lista)}

<section class="sec atac" id="atacado"><div class="atac__bg">{foto("ceasa", "Corredor do Ceasa com caixas de frutas e verduras de madrugada")}</div><div class="wrap atac__in">
  <div class="atac__txt rv">
    <h2>Atacado, varejo e distribuição.</h2>
    <p>Seu negócio precisa de um bom fornecedor? Consulte disponibilidade, volumes, condições comerciais e possibilidades de fornecimento.</p>
    <ul class="compradores">{compradores}</ul>
    <div class="ctas">{btn("Solicitar cotação para minha empresa", "/atacado")}</div>
  </div>
</div></section>

<section class="sec sec--escuro2" id="loja"><div class="wrap loja">
  <div class="loja__txt rv">
    <h2>Monte sua lista. Receba a cotação no WhatsApp.</h2>
    <ol class="passos">
      <li><b>01</b><div><h3>Escolha no catálogo</h3><p>Frutas, verduras, legumes e raízes, com foto, unidade de venda e época de safra.</p></div></li>
      <li><b>02</b><div><h3>Informe quantidade e unidade</h3><p>Caixa, quilo, maço, saco ou unidade, do jeito que o seu negócio compra.</p></div></li>
      <li><b>03</b><div><h3>Envie e receba o preço do dia</h3><p>A lista chega pronta no nosso WhatsApp e respondemos com preço e disponibilidade.</p></div></li>
    </ol>
    <div class="ctas">{btn("Montar minha lista", "/produtos")}</div>
  </div>
  <div class="loja__demo rv" data-d="1" aria-hidden="true">
    <div class="demo"><div class="demo__topo">{ic("lista")}<span>Lista de cotação</span><b>4 itens</b></div>
      <ul class="demo__itens">{lista_demo}</ul>
      <div class="demo__btn">{ZAP}<span>Enviar pelo WhatsApp</span></div></div>
  </div>
</div></section>

<section class="mundo" id="mundo"><div class="mundo__bg">{foto("porto", "Porto com contêineres refrigerados ao entardecer")}</div><div class="wrap"><div class="mundo__txt rv">
  <h2>Negócios que conectam mercados.</h2>
  <p>Importação e exportação de produtos do agronegócio, com cotação, negociação e documentação conforme as exigências de cada destino.</p>
  <div class="ctas">{btn("Comércio exterior", "/comercio-exterior")}{btn("For international buyers", "/comercio-exterior#international", "linha", False)}</div>
  <p class="mundo__dado">Pernambuco lidera a exportação de manga do Brasil e responde por cerca de metade da uva de mesa exportada pelo país.<small>Fontes: Abrafrutas e Governo de Pernambuco, 2024 e 2026.</small></p>
</div></div></section>

<section class="sec sec--creme origem" id="origem"><div class="wrap">
  <div class="origem__topo">
    <div class="origem__foto rv">{foto("origem", "Mãos de produtor segurando mangas recém-colhidas", "(max-width:760px) 92vw, 40vw", larguras=(800, 1122))}</div>
    <div class="origem__txt rv" data-d="1">
      <h2>Qualidade começa na origem.</h2>
      <p>Valorizamos quem produz e a procedência de cada produto. Pernambuco é um dos grandes celeiros de frutas e hortaliças do Nordeste, e cada região tem a sua vocação.</p>
      <ul class="origens">{origens}</ul>
      <p class="origem__fonte">Regiões produtoras segundo Conab e IBGE. A origem de cada lote é informada na cotação, quando comprovada.</p>
    </div>
  </div>
</div></section>
{calendario_sec(lista, mes)}

<section class="sec lider" id="lideranca"><div class="wrap lider__in">
  <img class="lider__marca" src="/assets/img/logo-emblema-512.webp" alt="" width="{dim("assets/img/logo-emblema-512.webp", (580, 512))[0]}" height="512" loading="lazy">
  <div class="lider__txt rv">
    <h2>Ricardo Romão</h2>
    <p class="lider__cargo">CEO da Ricardo Agronegócio</p>
    <blockquote>{e(RICARDO_FRASE)}</blockquote>
    <div class="ctas">{btn("Conheça a empresa", "/empresa", "linha")}</div>
  </div>
</div></section>
{onde_sec()}
{faq_sec(faq)}
{cta_final()}'''
    return pagina("Ricardo Agronegócio | Do campo para o mundo. Hortifrúti na CEASA Pernambuco",
                  "Frutas, verduras, legumes e raízes no atacado e no varejo na CEASA Pernambuco, em Recife. Catálogo com cotação pelo WhatsApp, distribuição, importação e exportação.",
                  corpo, "/", preload_foto("campo", "campo-m"), extra_ld=faq_ld(faq), lista=lista)


# ------------------------------------------------------------------ páginas internas
def empresa():
    txt = "".join(f"<p>{e(p)}</p>" for p in EMPRESA_TXT)
    dims = "".join(f'<li class="rv" data-d="{i % 3}"><b>{i + 1:02d}</b><span>{e(d)}</span></li>' for i, d in enumerate(DIMENSOES))
    valores = "".join(f'<article class="valor rv" data-d="{i % 3}"><span>{i + 1:02d}</span><h3>{e(t)}</h3><p>{e(d)}</p></article>' for i, (t, d) in enumerate(VALORES))
    marquee = "".join(f"<span>{e(t)}</span><i></i>" for t, _ in VALORES)
    corpo = f'''{pag_topo("A empresa", SLOGAN, "pomar")}
<section class="sec"><div class="wrap par">
  <div class="par__cab rv"><h2>Ricardo Agronegócio</h2></div>
  <div class="texto rv" data-d="1">{txt}</div>
</div></section>
<section class="sec sec--escuro2"><div class="wrap">
  <div class="cab rv"><h2>{e(POSICIONAMENTO)}</h2></div>
  <ol class="dims">{dims}</ol>
</div></section>
<section class="sec sec--creme"><div class="wrap mv">
  <article class="mv__item rv"><h2>Nossa missão</h2>{"".join(f"<p>{e(p)}</p>" for p in MISSAO)}</article>
  <article class="mv__item rv" data-d="1"><h2>Nossa visão</h2>{"".join(f"<p>{e(p)}</p>" for p in VISAO)}</article>
</div></section>
<section class="sec" id="valores"><div class="wrap">
  <div class="cab rv"><h2>Os princípios que orientam nossas relações e negócios.</h2><p>{e(VALORES_INTRO)}</p></div>
  <div class="valores">{valores}</div>
</div>
<div class="marq" aria-hidden="true"><div class="marq__t">{marquee * 2}</div></div></section>
<section class="sec sec--escuro2 lider lider--pag" id="lideranca"><div class="wrap lider__in">
  <img class="lider__marca" src="/assets/img/logo-emblema-512.webp" alt="" width="{dim("assets/img/logo-emblema-512.webp", (580, 512))[0]}" height="512" loading="lazy">
  <div class="lider__txt rv">
    <h2>Ricardo Romão</h2><p class="lider__cargo">CEO e responsável pela Ricardo Agronegócio</p>
    {"".join(f"<p>{e(p)}</p>" for p in RICARDO)}
    <blockquote>{e(RICARDO_FRASE)}</blockquote>
  </div>
</div></section>
{cta_final()}'''
    return pagina("A empresa | Ricardo Agronegócio", "História, posicionamento, missão, visão, valores e liderança da Ricardo Agronegócio, trading do agronegócio na CEASA Pernambuco.",
                  corpo, "/empresa", preload_foto("pomar"), nome_rota="A empresa")


def card_produto(p):
    var = ", ".join(p.get("variedades") or [])
    un = " ou ".join(u.lower() for u in (p.get("unidades") or []))
    safra = lista_meses(p.get("safra") or [])
    busca = " ".join([p["nome"]] + (p.get("variedades") or []) + (p.get("busca") or [])).lower()
    return f'''<article class="prod" id="{p["slug"]}" data-slug="{p["slug"]}" data-cat="{p["categoria"]}" data-safra="{",".join(map(str, p.get("safra") or []))}" data-busca="{e(busca)}">
  <div class="prod__foto">{foto_prod(p["slug"], p["nome"])}<span class="prod__selo" hidden>Na safra</span></div>
  <div class="prod__txt">
    <h3>{e(p["nome"])}</h3>{f'<p class="prod__var">{e(var)}</p>' if var else ""}
    <p class="prod__desc">{e(p.get("descricao", ""))}</p>
    <dl class="prod__info"><div><dt>Venda</dt><dd>{e(un.capitalize())}</dd></div>{f'<div><dt>Boa oferta</dt><dd>{e(safra)}</dd></div>' if safra else ""}<div><dt>Conservação</dt><dd>{e(p.get("conservacao", ""))}</dd></div></dl>
  </div>
  <button class="prod__add" type="button" data-add="{p["slug"]}" aria-label="Adicionar {e(p["nome"])} à lista de cotação">{ic("mais")}<span>Adicionar à lista</span></button>
</article>'''


def produtos_pag(lista, faq, mes):
    filtros = '<button type="button" class="on" data-filtro="todos">Todos</button>' + "".join(
        f'<button type="button" data-filtro="{c}">{e(n)}</button>' for c, n, *_ in CATS) + '<button type="button" data-filtro="safra">Na safra agora</button>'
    blocos = ""
    for c, n, _f, fr in CATS:
        ps = [p for p in lista if p["categoria"] == c]
        if not ps:
            continue
        blocos += f'''<section class="catal__bloco" id="cat-{c}" data-bloco="{c}">
  <div class="catal__cab"><h2>{e(n)}</h2><p>{e(fr)}</p></div>
  <div class="prods">{"".join(card_produto(p) for p in ps)}</div>
</section>'''
    itens_ld = ld({"@context": "https://schema.org", "@type": "ItemList", "name": "Catálogo Ricardo Agronegócio", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "item": {"@type": "Product", "name": p["nome"], "description": p.get("descricao", ""),
                                                          "category": dict((c, n) for c, n, *_ in CATS).get(p["categoria"], ""),
                                                          "image": f"{DOMINIO}/assets/img/produtos/{p['slug']}-560.webp",
                                                          "url": f"{DOMINIO}/produtos#{p['slug']}"}} for i, p in enumerate(lista)]})
    corpo = f'''{pag_topo("Produtos e loja", "Frutas, verduras, legumes, raízes e produtos agrícolas. Monte sua lista e receba a cotação do dia pelo WhatsApp.", "ceasa")}
<section class="catal" id="catalogo"><div class="wrap">
  <div class="catal__barra">
    <label class="busca">{ic("lupa")}<input type="search" placeholder="Buscar produto (ex.: macaxeira, manga)" aria-label="Buscar produto" data-busca></label>
    <div class="filtros" role="group" aria-label="Categorias">{filtros}</div>
  </div>
  <p class="catal__vazio" data-vazio hidden>Nenhum produto encontrado. Peça pelo WhatsApp que a gente procura para você.</p>
  {blocos}
  <p class="catal__nota">Preço e disponibilidade mudam todos os dias de mercado. As fotos são ilustrativas. Unidades, volumes e condições de entrega são confirmados no atendimento.</p>
</div></section>
{calendario_sec(lista, mes)}
<aside class="cesta" data-cesta aria-label="Lista de cotação">
  <button class="cesta__abre" type="button" data-cesta-abre aria-expanded="false">{ic("lista")}<span>Lista de cotação</span><b data-cesta-n>0</b></button>
  <div class="cesta__painel" data-cesta-painel hidden>
    <div class="cesta__topo"><h2>Sua lista de cotação</h2><button type="button" data-cesta-fecha aria-label="Fechar">{ic("fechar")}</button></div>
    <ul class="cesta__itens" data-cesta-itens></ul>
    <p class="cesta__vazia" data-cesta-vazia>Adicione produtos do catálogo para montar a sua lista.</p>
    <form class="cesta__form" data-cesta-form novalidate>
      <div class="campo"><label for="c-nome">Seu nome</label><input id="c-nome" name="Nome" autocomplete="name" required></div>
      <div class="campo"><label for="c-emp">Empresa (se houver)</label><input id="c-emp" name="Empresa" autocomplete="organization"></div>
      <div class="campo"><label for="c-cid">Cidade e estado</label><input id="c-cid" name="Cidade/UF" autocomplete="address-level2" required></div>
      <div class="campo"><label for="c-tipo">Como quer comprar</label><select id="c-tipo" name="Tipo de compra" required><option value="" disabled selected>Escolha</option><option>Retirar na CEASA</option><option>Atacado para minha empresa</option><option>Entrega (combinar)</option></select></div>
      <div class="form__mel" aria-hidden="true"><input name="site" tabindex="-1" autocomplete="off"></div>
      <button class="btn btn--verde" type="submit">{ZAP} Enviar lista pelo WhatsApp</button>
    </form>
  </div>
</aside>
{faq_sec(faq)}'''
    return pagina("Produtos e loja: frutas, verduras e legumes na CEASA-PE | Ricardo Agronegócio",
                  "Catálogo de frutas, verduras, legumes, raízes e produtos agrícolas da Ricardo Agronegócio, na CEASA Pernambuco. Monte sua lista e peça a cotação do dia pelo WhatsApp.",
                  corpo, "/produtos", preload_foto("ceasa"), extra_ld=itens_ld + faq_ld(faq), nome_rota="Produtos", lista=lista)


def atacado():
    compradores = "".join(f'<li class="rv" data-d="{i % 3}">{ic(i_)}<h3>{e(t)}</h3></li>' for i, (i_, t) in enumerate(COMPRADORES))
    campos = [("txt", "Empresa", "Empresa", "req"), ("txt", "CNPJ", "CNPJ (quando aplicável)", ""),
              ("txt", "Seu nome", "Seu nome", "req"), ("tel", "WhatsApp", "WhatsApp", "req"),
              ("txt", "Cidade/UF", "Cidade e estado", "req"),
              ("sel:Semanal|Duas ou mais vezes por semana|Quinzenal|Mensal|Pedido pontual", "Frequência de compra", "Frequência de compra", "req"),
              ("area", "Produtos de interesse", "Produtos de interesse", "cheio req"),
              ("txt", "Volume estimado", "Volume estimado por pedido (ex.: 20 caixas de tomate)", "cheio")]
    corpo = f'''{pag_topo("Seu negócio precisa de um bom fornecedor?", "Entre em contato com a Ricardo Agronegócio para consultar disponibilidade, volumes, condições comerciais e possibilidades de fornecimento.", "carga",
                         f'<div class="ctas">{btn("Solicitar cotação para minha empresa", "#cotacao-empresa")}</div>')}
<section class="sec"><div class="wrap">
  <div class="cab rv"><h2>Fornecimento para quem compra todo dia de mercado.</h2></div>
  <ul class="quem">{compradores}</ul>
</div></section>
<section class="sec sec--creme"><div class="wrap como">
  <div class="como__cab rv"><h2>Como funciona o atendimento.</h2></div>
  <ol class="passos passos--claro rv" data-d="1">
    <li><b>01</b><div><h3>Você conta o que precisa</h3><p>Produtos, volume estimado e frequência de compra.</p></div></li>
    <li><b>02</b><div><h3>Consultamos disponibilidade</h3><p>Avaliamos a oferta do dia e as possibilidades de fornecimento.</p></div></li>
    <li><b>03</b><div><h3>Combinamos as condições</h3><p>Preço, retirada ou entrega e periodicidade, por escrito no WhatsApp.</p></div></li>
  </ol>
</div></section>
<section class="sec" id="cotacao-empresa"><div class="wrap"><div class="caixa">
  <div class="caixa__txt"><h2>Solicitar cotação para minha empresa</h2><p>Preencha e a mensagem chega pronta no nosso WhatsApp. Regiões e condições de entrega são combinadas no atendimento.</p></div>
  {formulario(campos, "Olá! Quero uma cotação de atacado para a minha empresa.", "Solicitar cotação", "")}
</div></div></section>
{cta_final()}'''
    return pagina("Atacado e distribuição de hortifrúti em Recife | Ricardo Agronegócio",
                  "Fornecimento de frutas, verduras e legumes para mercados, restaurantes, hotéis, distribuidores e compradores empresariais a partir da CEASA Pernambuco.",
                  corpo, "/atacado", preload_foto("carga"), nome_rota="Atacado e distribuição")


def comex():
    itens = "".join(f'<article class="bloco rv" data-d="{i % 3}">{ic(ic_)}<h3>{e(t)}</h3><p>{e(d)}</p></article>' for i, (ic_, t, d) in enumerate(COMEX_ITENS))
    campos = [("txt", "Empresa", "Empresa", "req"), ("txt", "País", "País", "req"),
              ("txt", "Seu nome", "Seu nome", "req"), ("tel", "WhatsApp", "WhatsApp com DDI", "req"),
              ("mail", "E-mail", "E-mail", "req"), ("sel:Importação|Exportação", "Operação", "Operação", "req"),
              ("area", "Produtos e especificações", "Produtos, especificações e volume estimado", "cheio req")]
    corpo = f'''{pag_topo("Negócios que conectam mercados.", "Importação e exportação de produtos do agronegócio, do primeiro contato à proposta comercial.", "porto")}
<section class="sec"><div class="wrap">
  <div class="cab rv"><h2>Comércio exterior com o pé no chão.</h2><p>{e(COMEX_AVISO)}</p></div>
  <div class="blocos">{itens}</div>
</div></section>
<section class="sec sec--escuro2"><div class="wrap par par--centro">
  <div class="par__cab rv"><h2>O potencial de Pernambuco.</h2></div>
  <div class="texto rv" data-d="1">
    <p>O Vale do São Francisco, em Petrolina, é o principal polo de manga e uva de mesa do país. Pernambuco liderou a exportação brasileira de manga em 2024 e responde por cerca de metade da uva de mesa que o Brasil vende ao exterior.</p>
    <p>Compradores estrangeiros pedem rastreabilidade, certificado fitossanitário e produtores certificados. Por isso, cada proposta parte do que pode ser fornecido e documentado para o destino.</p>
    <p class="mundo__dado"><small>Fontes: Abrafrutas, IBGE/PAM 2024 e Governo de Pernambuco.</small></p>
  </div>
</div></section>
<section class="sec sec--creme" id="international" lang="en"><div class="wrap par">
  <div class="par__cab rv"><h2>For international buyers</h2></div>
  <div class="texto rv" data-d="1">
    <p>Ricardo Agronegócio is an agribusiness trading company based at CEASA Pernambuco, in Recife, Brazil. We connect growers, suppliers and buyers in fresh produce.</p>
    <p>Send us your request with products, specifications, volumes and destination. Each proposal is built on what can be supplied and documented according to the requirements of the destination country.</p>
    <div class="ctas">{btn("Request a quote", "#cotacao-internacional")}</div>
  </div>
</div></section>
<section class="sec" id="cotacao-internacional"><div class="wrap"><div class="caixa">
  <div class="caixa__txt"><h2>Cotação internacional</h2><p>Para importadores e exportadores. Atendimento em português e em inglês; versão em espanhol em breve.</p></div>
  {formulario(campos, "Olá! Quero falar sobre um negócio internacional.", "Enviar solicitação")}
</div></div></section>
{cta_final("Vamos conversar sobre o seu mercado?", "Conte o produto, o volume e o destino. Respondemos com o que é possível fornecer.")}'''
    return pagina("Importação e exportação de frutas e hortifrúti | Ricardo Agronegócio",
                  "Comércio exterior do agronegócio a partir de Pernambuco: cotações, negociação e documentação para importação e exportação de frutas e produtos agrícolas.",
                  corpo, "/comercio-exterior", preload_foto("porto"), nome_rota="Comércio exterior")


def parcerias():
    campos = [("txt", "Seu nome", "Seu nome", "req"), ("tel", "WhatsApp", "WhatsApp", "req"),
              ("txt", "Propriedade ou empresa", "Propriedade ou empresa", ""), ("txt", "Cidade/UF", "Cidade e estado", "req"),
              ("area", "Produtos e safra", "O que você produz ou fornece, volume e época de colheita", "cheio req")]
    origens = "".join(f'<li class="rv" data-d="{i % 3}"><h3>{e(r)}</h3><p>{e(t)}</p></li>' for i, (r, t) in enumerate(ORIGENS))
    corpo = f'''{pag_topo("Produção e parcerias", "Relacionamento com produtores, origens de fornecimento e oportunidades de negócios.", "packing")}
<section class="sec"><div class="wrap par">
  <div class="par__cab rv"><h2>Reconhecemos o valor de quem produz.</h2></div>
  <div class="texto rv" data-d="1">
    <p>A Ricardo Agronegócio quer construir relações de longo prazo com produtores e fornecedores, com combinados claros, regularidade e respeito à procedência e ao cuidado com cada colheita.</p>
    <p>Para quem produz, somos um canal de venda na CEASA Pernambuco, no atacado e, conforme a documentação de cada produto, em negócios internacionais.</p>
  </div>
</div></section>
<section class="sec sec--creme"><div class="wrap">
  <div class="cab rv"><h2>Origens de Pernambuco.</h2><p>Regiões produtoras que abastecem as centrais de abastecimento do estado, segundo Conab e IBGE.</p></div>
  <ul class="origens origens--grade">{origens}</ul>
</div></section>
<section class="sec" id="fornecer"><div class="wrap"><div class="caixa">
  <div class="caixa__txt"><h2>Quero fornecer</h2><p>Conte o que você produz, o volume e a época de colheita. Entramos em contato para conhecer a sua produção.</p></div>
  {formulario(campos, "Olá! Sou produtor ou fornecedor e quero conversar sobre parceria.", "Enviar")}
</div></div></section>
{cta_final()}'''
    return pagina("Produção e parcerias com produtores | Ricardo Agronegócio",
                  "Produtores e fornecedores de frutas, verduras e legumes: venda na CEASA Pernambuco e parcerias de longo prazo com a Ricardo Agronegócio.",
                  corpo, "/parcerias", preload_foto("packing"), nome_rota="Produção e parcerias")


def contato(faq):
    campos = [("txt", "Nome", "Nome", "req"), ("tel", "WhatsApp", "WhatsApp", "req"),
              ("txt", "Empresa", "Empresa (se houver)", ""), ("txt", "Cidade/UF", "Cidade e estado", "req"),
              ("sel:" + "|".join(ASSUNTOS), "Assunto", "Assunto", "cheio req"),
              ("area", "Mensagem", "Mensagem", "cheio req")]
    corpo = f'''{pag_topo("Contato e cotações", "Compradores, fornecedores, importadores e exportadores: escolha o assunto e a mensagem chega pronta no nosso WhatsApp.", "campo",
                         celular=("campo-m", (700, 1122)))}
<section class="sec" id="cotacao"><div class="wrap"><div class="caixa">
  <div class="caixa__txt"><h2>Fale com a Ricardo Agronegócio</h2><p>Cada pedido segue para a área responsável. Se preferir, fale direto no WhatsApp.</p>
    <a class="tel" href="/obrigado?c=contato">{ZAP} {TEL_VER}</a></div>
  {formulario(campos, "Olá! Vim pelo site da Ricardo Agronegócio.", "Enviar pelo WhatsApp")}
</div></div></section>
{onde_sec()}
{faq_sec(faq)}'''
    return pagina("Contato e cotações | Ricardo Agronegócio", f"Fale com a Ricardo Agronegócio pelo WhatsApp {TEL_VER}. CEASA Pernambuco, {ENDERECO}.",
                  corpo, "/contato", preload_foto("campo", "campo-m"), extra_ld=faq_ld(faq), nome_rota="Contato")


def privacidade():
    corpo = f'''{pag_topo("Política de Privacidade", "Como os seus dados são tratados neste site, conforme a LGPD (Lei 13.709/2018).", "campo")}
<section class="sec"><div class="wrap texto texto--pag">
<h2>Quem cuida dos seus dados</h2><p>Este site é da Ricardo Agronegócio, responsável pelo tratamento dos dados enviados por meio dele.</p>
<h2>Que dados recebemos</h2><p>Apenas os que você digita nos formulários e na lista de cotação: nome, empresa, CNPJ quando aplicável, WhatsApp, e-mail, cidade e estado, produtos, volumes e a sua mensagem.</p>
<h2>Para que usamos</h2><p>Para responder ao seu pedido de cotação, compra, fornecimento ou parceria. Não vendemos nem compartilhamos seus dados para fins comerciais.</p>
<h2>Como a mensagem chega até nós</h2><p>Ao enviar, a mensagem é aberta no WhatsApp, já preenchida, para que você a envie à Ricardo Agronegócio. O WhatsApp tem a sua própria política de privacidade.</p>
<h2>Lista de cotação</h2><p>Os produtos que você adiciona à lista ficam guardados só no seu navegador, para você continuar depois. Nada é enviado até você tocar em enviar.</p>
<h2>Cookies</h2><p>Este site não usa cookies de publicidade nem de rastreamento. Se ferramentas de medição forem adicionadas, você será avisado.</p>
<h2>Seus direitos</h2><p>Você pode pedir acesso, correção ou exclusão dos seus dados a qualquer momento pelo WhatsApp {TEL_VER}.</p>
</div></section>'''
    return pagina("Política de Privacidade | Ricardo Agronegócio", "Política de privacidade e tratamento de dados (LGPD) da Ricardo Agronegócio.", corpo, "/privacidade", nome_rota="Privacidade")


def obrigado():
    corpo = f'''<section class="obrigado"><div>
  <img src="/assets/img/logo-emblema-192.webp" alt="Ricardo Agronegócio" width="{dim("assets/img/logo-emblema-192.webp", (217, 192))[0]}" height="192">
  <h1>Abrindo a conversa.</h1>
  <p>Em instantes você fala com a Ricardo Agronegócio pelo WhatsApp.</p>
  <div class="gira" aria-hidden="true"></div>
  <div class="ctas"><a class="btn btn--verde" id="vai" href="https://wa.me/{WHATSAPP}">Abrir o WhatsApp {SETA}</a><a class="btn btn--linha" href="/">Voltar</a></div>
</div></section>
<script>
(function(){{
  var W='{WHATSAPP}', msg='Olá! Vim pelo site da Ricardo Agronegócio e quero uma cotação.';
  try{{ msg=sessionStorage.getItem('ra_msg')||msg; sessionStorage.removeItem('ra_msg'); }}catch(e){{}}
  var dest='https://wa.me/'+W+'?text='+encodeURIComponent(msg); document.getElementById('vai').href=dest;
  var c=(new URLSearchParams(location.search).get('c')||'site').replace(/[^a-z0-9_-]/gi,'');
  var t0=Date.now(), partiu=false;
  function vai(){{ if(partiu) return; partiu=true; location.replace(dest); }}
  function talvez(){{ var f=900-(Date.now()-t0); setTimeout(vai, f>0?f:0); }}
  window.dataLayer=window.dataLayer||[]; window.dataLayer.push({{event:'conversao_whatsapp',contexto:c,eventCallback:talvez,eventTimeout:2000}});
  if(!window.google_tag_manager) talvez();
  setTimeout(vai,2600);
}})();
</script>'''
    return pagina("Abrindo a conversa | Ricardo Agronegócio", "Abrindo o WhatsApp da Ricardo Agronegócio.", corpo, "/obrigado", robots="noindex,nofollow", casca=False)


def main():
    lista, faq = produtos(), carregar_json("faq.json", [])
    mes = date.today().month
    paginas = {"index.html": home(lista, faq, mes), "empresa.html": empresa(), "produtos.html": produtos_pag(lista, faq, mes),
               "atacado.html": atacado(), "comercio-exterior.html": comex(), "parcerias.html": parcerias(),
               "contato.html": contato(faq), "privacidade.html": privacidade(), "obrigado.html": obrigado()}
    for arq, html in paginas.items():
        (RAIZ / arq).write_text(html)
    rotas = ["/"] + [h for _, h in MENU[1:]] + ["/privacidade"]
    hoje = date.today().isoformat()
    (RAIZ / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                      + "".join(f"<url><loc>{DOMINIO}{r}</loc><lastmod>{hoje}</lastmod></url>" for r in rotas) + "</urlset>\n")
    (RAIZ / "robots.txt").write_text("User-agent: *\n" + ("Allow: /\n" if INDEXAR else "Disallow:\n") + f"\nSitemap: {DOMINIO}/sitemap.xml\n")
    cats = dict((c, n) for c, n, *_ in CATS)
    (RAIZ / "llms.txt").write_text(
        f"# Ricardo Agronegócio\n\n> {POSICIONAMENTO} {SLOGAN}\n\nCEASA Pernambuco, {ENDERECO}. CEO: Ricardo Romão.\n\n## O que fazemos\n"
        + "\n".join(f"- {d}" for d in DIMENSOES)
        + "\n\n## Catálogo\n" + "\n".join(f"- {p['nome']} ({cats.get(p['categoria'], '')}): {p.get('descricao', '')}" for p in lista)
        + "\n\n## Perguntas frequentes\n" + "\n".join(f"- {q['p']} {q['r']}" for q in faq)
        + f"\n\n## Contato\nWhatsApp: {TEL_VER}\nSite: {DOMINIO}/\n")
    print(f"  {len(paginas)} páginas, {len(lista)} produtos, {len(faq)} perguntas  site.js v={hash_de(JS)}  indexar={INDEXAR}")


if __name__ == "__main__":
    main()
