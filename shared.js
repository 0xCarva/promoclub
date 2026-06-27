// ── SHARED CONFIG ─────────────────────────────────────────
const AFILIADO_TAG = 'carva00-20';
const TG_LINK = 'https://t.me/promoclubhub';
const IG_LINK = 'https://www.instagram.com/promoclubhub/';
const HINODE_LINK = 'https://www.hinode.com.br/?id_consultor=76173688';
const PRIME_LINK = `https://www.amazon.com.br/prime?tag=${AFILIADO_TAG}`;

// ── HELPERS ───────────────────────────────────────────────
function tagURL(url) {
  if (!url) return '#';
  try {
    if (url.includes('amazon.com') || url.includes('amzn.to')) {
      if (url.includes('amzn.to')) {
        const sep = url.includes('?') ? '&' : '?';
        return url.replace(/[?&]tag=[^&]*/g, '').replace(/[?&]$/, '') + sep + `tag=${AFILIADO_TAG}`;
      }
      const u = new URL(url);
      u.searchParams.set('tag', AFILIADO_TAG);
      return u.toString();
    }
  } catch(e) {}
  return url;
}

function buildAmazonLink(asin) {
  return `https://www.amazon.com.br/dp/${asin}?tag=${AFILIADO_TAG}&linkCode=ll2`;
}

function parsePrice(str) {
  if (!str) return 0;
  const m = String(str).match(/[\d]+[,.][\d]{2}/);
  return m ? parseFloat(m[0].replace(',', '.')) : 0;
}

function calcDiscount(orig, curr) {
  if (orig > curr && orig > 0) return Math.round((orig - curr) / orig * 100) + '%';
  return '';
}

function stars(rating, size = 'sm') {
  const r = parseFloat(rating) || 0;
  const sz = size === 'sm' ? 'w-3 h-3' : 'w-4 h-4';
  return Array.from({length: 5}, (_, i) => `
    <svg class="${sz} ${i < Math.round(r) ? 'text-yellow-400' : 'text-gray-600'}" fill="currentColor" viewBox="0 0 20 20">
      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
    </svg>`).join('');
}

// ── BADGE CONFIG ──────────────────────────────────────────
const BADGE_CONFIG = {
  hot:        { label: '🔥 Em Alta',        bg: 'bg-red-500',    text: 'text-white' },
  new:        { label: '✨ Novo',            bg: 'bg-blue-500',   text: 'text-white' },
  top:        { label: '⭐ Top',             bg: 'bg-indigo-500', text: 'text-white' },
  prime:      { label: '★ Prime',           bg: 'bg-blue-600',   text: 'text-white' },
  super:      { label: '💥 Super Oferta',   bg: 'bg-orange-500', text: 'text-white' },
  flash:      { label: '⚡ Relâmpago',      bg: 'bg-yellow-500', text: 'text-black' },
  exclusive:  { label: '🏆 Exclusivo',      bg: 'bg-purple-600', text: 'text-white' },
  clearance:  { label: '🏷️ Liquidação',    bg: 'bg-green-600',  text: 'text-white' },
};

function badgeHTML(badge) {
  if (!badge) return '';
  const b = BADGE_CONFIG[badge] || { label: badge, bg: 'bg-gray-600', text: 'text-white' };
  return `<span class="absolute top-2 left-2 z-10 text-xs font-bold px-2 py-0.5 rounded-full ${b.bg} ${b.text}">${b.label}</span>`;
}

// ── JSON LOADERS ──────────────────────────────────────────
async function loadProdutos() {
  try {
    const res = await fetch('produtos.json');
    if (!res.ok) return [];
    const raw = await res.json();
    const list = Array.isArray(raw) ? raw : (raw.produtos || raw.products || []);
    return list.map((p, i) => {
      const asin = p.asin || p.id || ('p' + i);
      const preco = parsePrice(p.price || p.preco_por);
      const orig  = parsePrice(p.original_price || p.preco_de);
      return {
        id:          asin,
        nome:        p.title || p.nome || 'Produto',
        loja:        p.store || p.loja || 'Amazon',
        categoria:   p.category || p.categoria || 'Geral',
        preco_por:   p.price || p.preco_por || '',
        preco_de:    p.original_price || p.preco_de || '',
        desconto:    p.discount || p.desconto || (orig > preco && orig > 0 ? calcDiscount(orig, preco) : ''),
        imagem:      p.image || p.imagem || '',
        link:        tagURL(p.link || (p.asin ? buildAmazonLink(p.asin) : '#')),
        badge:       p.badge || (parseInt(p.discount) >= 40 ? 'super' : parseInt(p.discount) >= 20 ? 'hot' : ''),
        avaliacao:   parseFloat(p.rating || p.avaliacao) || 0,
        avaliacoes:  String(p.reviews || p.avaliacoes || ''),
        parcelamento: p.installments || p.parcelamento || '',
        estoque:     p.stock_alert || p.estoque || '',
        is_prime:    p.is_prime || false,
        menor_preco: p.menor_preco || false,
        menor_preco_30: p.menor_preco_30 || false,
        descricao:   (p.description || p.descricao || '').substring(0, 280),
        features:    p.features || [],
        destaque:    p.destaque || false,
      };
    }).filter(p => p.preco_por && p.imagem);
  } catch(e) {
    console.warn('[PromoClub] produtos.json:', e.message);
    return [];
  }
}

async function loadCupons() {
  try {
    const res = await fetch('cupons.json');
    if (!res.ok) return [];
    const raw = await res.json();
    return Array.isArray(raw) ? raw : (raw.cupons || []);
  } catch(e) {
    console.warn('[PromoClub] cupons.json:', e.message);
    return [];
  }
}

// ── TOAST ─────────────────────────────────────────────────
function showToast(msg) {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    el.className = 'fixed bottom-5 right-5 z-50 bg-gray-800 border border-yellow-500/30 text-white text-sm px-4 py-2.5 rounded-lg shadow-xl border-l-2 border-l-yellow-400 transition-all duration-300 translate-y-16 opacity-0 pointer-events-none';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.classList.remove('translate-y-16', 'opacity-0');
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.add('translate-y-16', 'opacity-0'), 3000);
}

// ── FAVORITES ─────────────────────────────────────────────
const Favs = {
  get: () => JSON.parse(localStorage.getItem('pc_favs') || '[]'),
  toggle(id) {
    const f = this.get();
    const i = f.indexOf(id);
    if (i >= 0) f.splice(i, 1); else f.push(id);
    localStorage.setItem('pc_favs', JSON.stringify(f));
    return i < 0;
  },
  has: (id) => Favs.get().includes(id),
};

// ── DRAWER ────────────────────────────────────────────────
function openDrawer() {
  document.getElementById('drawer').classList.remove('translate-x-full');
  document.getElementById('drawerBg').classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}
function closeDrawer() {
  document.getElementById('drawer').classList.add('translate-x-full');
  document.getElementById('drawerBg').classList.add('hidden');
  document.body.style.overflow = '';
}
