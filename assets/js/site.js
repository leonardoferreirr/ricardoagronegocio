/* Ricardo Agronegócio: comportamento do site. Sem dependências. */
(() => {
  const d = document, h = d.documentElement, w = window;
  const rm = w.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const largo = w.matchMedia('(min-width:761px)');
  const MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const img = (s, n, tam) => `<img src="/assets/img/produtos/${s}-320.webp" alt="${esc(n || '')}" width="320" height="320" loading="lazy" decoding="async"${tam ? ` sizes="${tam}"` : ''}>`;
  let dados = [];
  try { dados = JSON.parse((d.getElementById('dados-produtos') || {}).textContent || '[]'); } catch (_) {}
  const porSlug = Object.fromEntries(dados.map(p => [p.s, p]));
  const mesHoje = new Date().getMonth() + 1;

  /* menu */
  const burger = d.querySelector('.burger');
  if (burger) burger.addEventListener('click', () => {
    const abre = !h.classList.contains('menu-open');
    h.classList.toggle('menu-open', abre);
    burger.setAttribute('aria-expanded', abre);
  });
  d.querySelectorAll('.nav a').forEach(a => a.addEventListener('click', () => h.classList.remove('menu-open')));

  /* vídeo de drone do topo: só no computador, sem economia de dados e sem movimento reduzido.
     Carrega depois da página pronta (a foto continua sendo o maior desenho) e pausa fora da tela. */
  const video = d.querySelector('.capa__video');
  const economia = navigator.connection && (navigator.connection.saveData || /2g/.test(navigator.connection.effectiveType || ''));
  if (video && !rm && !economia && largo.matches) {
    const ligar = () => {
      video.querySelectorAll('source[data-src]').forEach(s => { s.src = s.dataset.src; });
      video.load();
      video.addEventListener('playing', () => video.classList.add('on'), { once: true });
      const tocar = () => { const p = video.play(); if (p && p.catch) p.catch(() => {}); };
      tocar();
      if ('IntersectionObserver' in w) {
        new IntersectionObserver(es => es.forEach(en => { en.isIntersecting ? tocar() : video.pause(); })).observe(video.closest('.capa') || video);
      }
    };
    const depois = () => ('requestIdleCallback' in w ? w.requestIdleCallback(ligar, { timeout: 2500 }) : setTimeout(ligar, 1200));
    d.readyState === 'complete' ? depois() : w.addEventListener('load', depois, { once: true });
  }

  /* revelações (com reserva: nada fica invisível) */
  const alvos = [...d.querySelectorAll('.rv')];
  if ('IntersectionObserver' in w) {
    const io = new IntersectionObserver(es => es.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
    }), { rootMargin: '0px 0px -6% 0px' });
    alvos.forEach(el => io.observe(el));
  } else alvos.forEach(el => el.classList.add('in'));
  setTimeout(() => alvos.forEach(el => { if (el.getBoundingClientRect().top < innerHeight) el.classList.add('in'); }), 2500);

  /* safra do mês do visitante (o HTML vem com o mês do build) */
  const naSafra = m => dados.filter(p => p.m.includes(m));
  const faixa = d.querySelector('[data-safra-t]');
  if (faixa && dados.length) {
    const rotMes = d.querySelector('[data-safra-faixa] [data-mes]');
    if (rotMes && rotMes.textContent.trim() !== MESES[mesHoje - 1]) {
      rotMes.textContent = MESES[mesHoje - 1];
      const ps = naSafra(mesHoje);
      const um = ps.map(p => `<a class="safra__item" href="/produtos#${p.s}">${img(p.s, '')}<span>${esc(p.n)}</span></a>`).join('');
      faixa.innerHTML = um + um;
    }
  }
  d.querySelectorAll('[data-cal]').forEach(cal => {
    const grade = cal.querySelector('[data-cal-grade]');
    const abas = [...cal.querySelectorAll('[data-mes-aba]')];
    const mostra = m => {
      abas.forEach(b => b.setAttribute('aria-selected', String(+b.dataset.mesAba === m)));
      grade.innerHTML = naSafra(m).map(p => `<a class="cal__item" href="/produtos#${p.s}">${img(p.s, '')}<span>${esc(p.n)}</span></a>`).join('');
    };
    abas.forEach(b => b.addEventListener('click', () => mostra(+b.dataset.mesAba)));
    if (dados.length && !abas.some(b => +b.dataset.mesAba === mesHoje && b.getAttribute('aria-selected') === 'true')) mostra(mesHoje);
  });

  /* peças que andam com o scroll */
  const topo = d.querySelector('.top');
  const perc = d.querySelector('[data-perc]');
  const pFotos = perc ? [...perc.querySelectorAll('.perc__foto')] : [];
  const pEtapas = perc ? [...perc.querySelectorAll('.perc__etapa')] : [];
  const pMarcos = perc ? [...perc.querySelectorAll('[data-marco]')] : [];
  const pTrilha = perc && perc.querySelector('.perc__trilha');
  const fundos = [...d.querySelectorAll('[data-paralaxe] img, [data-paralaxe] video')];
  const fundo = fundos[0];
  const lim = v => Math.min(1, Math.max(0, v));
  let etapaAtual = 0;

  const quadro = () => {
    pendente = false;
    topo && topo.classList.toggle('solid', w.scrollY > 30);
    if (perc && largo.matches) {
      const r = perc.getBoundingClientRect(), total = perc.offsetHeight - innerHeight;
      const p = rm ? 1 : lim(-r.top / (total * 0.92));
      const n = Math.min(pEtapas.length - 1, Math.floor(p * pEtapas.length));
      pTrilha && pTrilha.style.setProperty('--p', p.toFixed(3));
      if (n !== etapaAtual) {
        etapaAtual = n;
        pFotos.forEach((f, i) => f.classList.toggle('on', i === n));
        pEtapas.forEach((f, i) => f.classList.toggle('on', i === n));
      }
      pMarcos.forEach((m, i) => m.classList.toggle('on', i <= n));
    }
    if (fundo && !rm && largo.matches) {
      const y = w.scrollY;
      if (y < innerHeight * 1.2) fundos.forEach(f => { f.style.transform = `scale(1.06) translate3d(0,${(y * 0.18).toFixed(1)}px,0)`; });
    }
  };
  let pendente = false;
  const pedir = () => { if (!pendente) { pendente = true; requestAnimationFrame(quadro); } };
  w.addEventListener('scroll', pedir, { passive: true });
  w.addEventListener('resize', pedir, { passive: true });
  quadro();

  /* catálogo: busca e filtros */
  const catal = d.querySelector('.catal');
  if (catal) {
    const busca = catal.querySelector('[data-busca]');
    const botoes = [...catal.querySelectorAll('[data-filtro]')];
    const cards = [...catal.querySelectorAll('.prod')];
    const blocos = [...catal.querySelectorAll('[data-bloco]')];
    const vazio = catal.querySelector('[data-vazio]');
    let filtro = 'todos';
    cards.forEach(c => { if ((c.dataset.safra || '').split(',').map(Number).includes(mesHoje)) c.querySelector('.prod__selo').hidden = false; });
    const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
    const aplica = () => {
      const q = norm(busca.value.trim());
      let algum = false;
      cards.forEach(c => {
        const okCat = filtro === 'todos' || (filtro === 'safra' ? (c.dataset.safra || '').split(',').map(Number).includes(mesHoje) : c.dataset.cat === filtro);
        const ok = okCat && (!q || norm(c.dataset.busca).includes(q));
        c.hidden = !ok; algum = algum || ok;
      });
      blocos.forEach(b => { b.hidden = ![...b.querySelectorAll('.prod')].some(c => !c.hidden); });
      vazio.hidden = algum;
    };
    busca.addEventListener('input', aplica);
    botoes.forEach(b => b.addEventListener('click', () => {
      filtro = b.dataset.filtro;
      botoes.forEach(x => x.classList.toggle('on', x === b));
      aplica();
      const alvo = catal.querySelector('.catal__bloco:not([hidden])');
      if (alvo && filtro !== 'todos') alvo.scrollIntoView({ behavior: rm ? 'auto' : 'smooth', block: 'start' });
    }));
    const deHash = () => {
      const m = location.hash.match(/^#cat-(.+)$/);
      if (m) { const b = botoes.find(x => x.dataset.filtro === m[1]); b && b.click(); }
    };
    deHash(); w.addEventListener('hashchange', deHash);
  }

  /* lista de cotação (fica só no navegador até o envio) */
  const cesta = d.querySelector('[data-cesta]');
  if (cesta && dados.length) {
    const CHAVE = 'ra_lista';
    let lista = [];
    try { lista = JSON.parse(localStorage.getItem(CHAVE) || '[]').filter(i => porSlug[i.s]); } catch (_) {}
    const painel = cesta.querySelector('[data-cesta-painel]');
    const abre = cesta.querySelector('[data-cesta-abre]');
    const itensEl = cesta.querySelector('[data-cesta-itens]');
    const vaziaEl = cesta.querySelector('[data-cesta-vazia]');
    const nEl = cesta.querySelector('[data-cesta-n]');
    const form = cesta.querySelector('[data-cesta-form]');
    const salva = () => { try { localStorage.setItem(CHAVE, JSON.stringify(lista)); } catch (_) {} };
    const marca = () => d.querySelectorAll('[data-add]').forEach(b => {
      const na = lista.some(i => i.s === b.dataset.add);
      b.classList.toggle('na', na);
      const sp = b.querySelector('span'); if (sp) sp.textContent = na ? 'Na lista' : 'Adicionar à lista';
    });
    const desenha = () => {
      nEl.textContent = lista.length;
      vaziaEl.hidden = lista.length > 0; form.hidden = lista.length === 0;
      itensEl.innerHTML = lista.map((i, k) => {
        const p = porSlug[i.s];
        const ops = p.u.map(u => `<option${u === i.u ? ' selected' : ''}>${esc(u)}</option>`).join('');
        return `<li data-k="${k}">${img(p.s, '')}<span class="nome">${esc(p.n)}</span>
          <button class="tira" type="button" aria-label="Tirar ${esc(p.n)} da lista"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
          <span class="qtd"><input type="number" min="1" step="1" inputmode="numeric" value="${i.q}" aria-label="Quantidade de ${esc(p.n)}"><select aria-label="Unidade de ${esc(p.n)}">${ops}</select></span></li>`;
      }).join('');
      marca();
    };
    const abrir = v => { painel.hidden = !v; abre.setAttribute('aria-expanded', String(v)); };
    abre.addEventListener('click', () => abrir(painel.hidden));
    cesta.querySelector('[data-cesta-fecha]').addEventListener('click', () => abrir(false));
    d.addEventListener('keydown', ev => { if (ev.key === 'Escape') abrir(false); });
    d.querySelectorAll('[data-add]').forEach(b => b.addEventListener('click', () => {
      const s = b.dataset.add, k = lista.findIndex(i => i.s === s);
      if (k >= 0) lista.splice(k, 1); else lista.push({ s, q: 1, u: porSlug[s].u[0] });
      salva(); desenha();
      cesta.classList.remove('pula'); void cesta.offsetWidth; cesta.classList.add('pula');
    }));
    itensEl.addEventListener('click', ev => {
      const t = ev.target.closest('.tira'); if (!t) return;
      lista.splice(+t.closest('li').dataset.k, 1); salva(); desenha();
    });
    itensEl.addEventListener('change', ev => {
      const li = ev.target.closest('li'); if (!li) return;
      const it = lista[+li.dataset.k];
      if (ev.target.matches('input')) it.q = Math.max(1, parseInt(ev.target.value, 10) || 1);
      if (ev.target.matches('select')) it.u = ev.target.value;
      salva();
    });
    const t0 = Date.now();
    form.addEventListener('submit', ev => {
      ev.preventDefault();
      if (!lista.length || !form.reportValidity()) return;
      const f = new FormData(form);
      if ((f.get('site') || '').toString().trim() || Date.now() - t0 < 2000) return;
      const linhas = ['Olá! Quero uma cotação destes produtos:', ''];
      const plural = (u, q) => { u = u.toLowerCase(); return q > 1 && u !== 'kg' ? u + 's' : u; };
      lista.forEach(i => linhas.push(`• ${porSlug[i.s].n}: ${i.q} ${plural(i.u, i.q)}`));
      linhas.push('');
      for (const [k, v] of f.entries()) { if (k !== 'site' && v.toString().trim()) linhas.push(`${k}: ${v.toString().trim()}`); }
      try { sessionStorage.setItem('ra_msg', linhas.join('\n')); } catch (_) {}
      location.href = '/obrigado?c=lista';
    });
    desenha();
  }

  /* formulários: mensagem pronta para o WhatsApp */
  const t0 = Date.now();
  d.querySelectorAll('form[data-form]').forEach(form => form.addEventListener('submit', ev => {
    ev.preventDefault();
    if (!form.reportValidity()) return;
    const f = new FormData(form);
    if ((f.get('site') || '').toString().trim() || Date.now() - t0 < 2500) return;
    const linhas = [form.dataset.abertura || 'Olá! Vim pelo site da Ricardo Agronegócio.', ''];
    for (const [k, v] of f.entries()) {
      if (k === 'site' || k === 'aceite') continue;
      const val = v.toString().trim();
      if (val) linhas.push(`${k}: ${val}`);
    }
    try { sessionStorage.setItem('ra_msg', linhas.join('\n')); } catch (_) {}
    location.href = '/obrigado?c=form';
  }));
})();
