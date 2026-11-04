# Ricardo Agronegócio

Site da Ricardo Agronegócio, trading de hortifrúti na CEASA Pernambuco (Recife). Cliente da Karla Messias (Plancenter).
Estático, sem dependências: `python3 build.py` gera as páginas na raiz.

## Páginas
- `/` início: topo, safra do mês, percurso campo → CEASA → distribuição → mundo, categorias, atacado, lista de cotação, comércio exterior, origem, calendário de safra, liderança, onde estamos (mapa do Ceasa), perguntas frequentes.
- `/empresa`: história, posicionamento, missão, visão, 12 valores, Ricardo Romão.
- `/produtos`: catálogo de 42 produtos com busca, filtros, selo "Na safra" e lista de cotação. A lista fica no navegador e é enviada pronta pelo WhatsApp.
- `/atacado`, `/comercio-exterior` (com bloco em inglês), `/parcerias`, `/contato` (7 assuntos), `/privacidade`, `/obrigado` (ponte para o WhatsApp).

## Fontes
- Copy: estrutura que a Karla mandou em 03/11 (OCR em `_src/estrutura-ocr.txt`).
- Catálogo e FAQ: `_src/produtos.json` e `_src/faq.json`. A safra vem do calendário de comercialização do Ceasa-PE.
- Fotos: geradas no ChatGPT (originais em `assets/src/geradas/`, fora do git). `python3 tools/fatiar.py` corta as grades de produto e gera os WebP.
- Logo: `python3 tools/logo.py` recorta a arte original (`assets/src/logo-original.jpg`) sem redesenhar.
- Mapa: OpenStreetMap (`tools/osm-ceasa.json`, `tools/mapa_osm.py`).

## Pendências com o cliente
- **Box e horário na CEASA.** O site pede para confirmar pelo WhatsApp antes de ir.
- A estrutura fala em "presença comercial planejada" na CEASA, mas o áudio cita a loja que ele já tem lá. Confirmar e ajustar o texto da empresa.
- **Fotos reais dos produtos.** O briefing pede foto real; as atuais são ilustrativas e o site diz isso.
- **Unidades de venda de cada produto.** Vieram do costume do atacado.
- **Radar Siscomex e certificações dos fornecedores**, antes de falar em operação própria de exportação.
- **Domínio oficial.** Depois de ligar, trocar `DOMINIO` e virar `INDEXAR = True`.
- **Loja com pagamento.** A Karla sugeriu WooCommerce, com carrinho, pagamento e frete. Esta versão é a primeira fase que ela mesma recomenda: catálogo com cotação. O checkout entra quando a logística por região estiver definida.

## Prévia local
`python3 tools/serve.py 4210` (imita o cleanUrls da Vercel).
