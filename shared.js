// ── CONFIG ────────────────────────────────────────────────
const TG_LINK = 'https://t.me/promoclubhub';
const IG_LINK = 'https://www.instagram.com/promoclubhub/';
const AFILIADO_TAG = 'carva00-20';

// ── HELPERS ───────────────────────────────────────────────
function fmtPrice(n) {
  if (!n && n !== 0) return '';
  return 'R$ ' + Number(n).toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
}

function calcDiscount(orig, curr) {
  if (orig > curr && orig > 0 && curr > 0)
    return Math.round((orig - curr) / orig * 100);
  return 0;
}

// ── LOADER — produtos.json ────────────────────────────────
// JSON format: { "ASIN": { title, current_price, original_price,
//   image, affiliate_url, original_url, last_checked }, ... }
async function loadProdutos() {
  try {
    const res = await fetch('produtos.json?_=' + Date.now());
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const raw = await res.json();

    // Support both object {ASIN: {...}} and array [{...}]
    const entries = Array.isArray(raw)
      ? raw.map(p => [p.asin || p.id || 'x', p])
      : Object.entries(raw);

    return entries.map(([asin, p]) => {
      const curr = parseFloat(p.current_price || p.price) || 0;
      const orig = parseFloat(p.original_price) || 0;
      const disc = calcDiscount(orig, curr);
      return {
        id:         asin,
        nome:       p.title || p.nome || 'Produto',
        loja:       p.store || p.loja || 'Amazon',
        categoria:  p.category || p.categoria || 'Geral',
        preco_por:  fmtPrice(curr),
        preco_de:   orig > curr ? fmtPrice(orig) : '',
        desconto:   disc > 0 ? disc + '%' : '',
        pct:        disc,
        imagem:     p.image || p.imagem || '',
        link:       p.affiliate_url || p.link || `https://www.amazon.com.br/dp/${asin}?tag=${AFILIADO_TAG}`,
        badge:      disc >= 40 ? 'super' : disc >= 20 ? 'hot' : '',
        atualizado: p.last_checked ? new Date(p.last_checked).toLocaleDateString('pt-BR') : '',
      };
    }).filter(p => p.preco_por && p.imagem);
  } catch(e) {
    console.warn('[PromoClub] produtos.json erro:', e.message);
    return [];
  }
}

// ── LOADER — cupons.json ──────────────────────────────────
async function loadCupons() {
  try {
    const res = await fetch('cupons.json?_=' + Date.now());
    if (!res.ok) return [];
    const raw = await res.json();
    return Array.isArray(raw) ? raw : (raw.cupons || []);
  } catch(e) { return []; }
}

// ── BADGE CONFIG ──────────────────────────────────────────
const BADGES = {
  super: { label: '💥 Super Oferta', cls: 'bg-orange-500 text-white' },
  hot:   { label: '🔥 Em Alta',      cls: 'bg-red-500 text-white'    },
  new:   { label: '✨ Novo',          cls: 'bg-blue-500 text-white'   },
};

function badgePill(badge) {
  const b = BADGES[badge];
  if (!b) return '';
  return `<span class="absolute top-2 left-2 z-10 text-xs font-bold px-2 py-0.5 rounded-full ${b.cls}">${b.label}</span>`;
}

// ── STAR RATING ───────────────────────────────────────────
function stars(r) {
  return Array.from({length:5},(_,i)=>`<svg class="w-3 h-3 ${i<Math.round(r)?'text-yellow-400':'text-gray-700'}" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>`).join('');
}

// ── TOAST ─────────────────────────────────────────────────
function showToast(msg) {
  let el = document.getElementById('_toast');
  if (!el) {
    el = Object.assign(document.createElement('div'), {id:'_toast'});
    el.className = 'fixed bottom-5 right-5 z-[9999] bg-gray-800 border-l-2 border-yellow-400 text-white text-sm px-4 py-2.5 rounded-lg shadow-xl transition-all duration-300 translate-y-16 opacity-0 pointer-events-none';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.classList.remove('translate-y-16','opacity-0');
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.add('translate-y-16','opacity-0'), 3000);
}

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
