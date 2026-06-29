// ── SHARED CONFIG ─────────────────────────────────────────
const AFILIADO_TAG = 'carva00-20';

// ── HELPERS ───────────────────────────────────────────────
function tagURL(url) {
  if (!url) return '#';
  try {
    if (url.includes('amazon.com') || url.includes('amzn.to')) {
      const u = new URL(url);
      u.searchParams.set('tag', AFILIADO_TAG);
      return u.toString();
    }
  } catch(e) {}
  return url;
}

function parsePrice(str) {
  if (!str) return 0;
  const cleaned = String(str).replace(/[^\d.,]/g, '').replace(',', '.');
  return parseFloat(cleaned) || 0;
}

function calcDiscount(orig, curr) {
  if (!orig || !curr || orig <= curr) return '';
  const pct = Math.round(((orig - curr) / orig) * 100);
  return pct > 0 ? pct + '%' : '';
}

function stars(rating, size = 'sm') {
  const r = parseFloat(rating) || 0;
  const sz = size === 'sm' ? 'w-3 h-3' : 'w-4 h-4';
  return Array.from({length: 5}, (_, i) => `
    <svg class="${sz} ${i < Math.round(r) ? 'text-yellow-400' : 'text-gray-600'}" fill="currentColor" viewBox="0 0 20 20">
      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
    </svg>`).join('');
}

// ── JSON LOADERS ──────────────────────────────────────────
async function loadProdutos() {
  try {
    const res = await fetch('produtos.json');
    if (!res.ok) return [];
    const raw = await res.json();
    const list = Array.isArray(raw) ? raw : (raw.produtos || []);
    
    return list.map((p, i) => {
      const preco = parsePrice(p.price || p.preco_por);
      const orig  = parsePrice(p.original_price || p.preco_de);
      
      return {
        id:          p.asin || ('p' + i),
        nome:        p.title || p.nome || 'Produto sem nome',
        loja:        p.store || 'Amazon',
        categoria:   p.category || p.categoria || 'Geral',
        preco_por:   p.price || p.preco_por || '',
        preco_de:    p.original_price || p.preco_de || '',
        desconto:    p.discount || calcDiscount(orig, preco),
        imagem:      p.image || p.imagem || '',
        link:        tagURL(p.link),
        badge:       p.badge || '',
        avaliacao:   0,
        avaliacoes:  '',
        parcelamento: '',
        estoque:     '',
        is_prime:    false,
        menor_preco: false,
        menor_preco_30: false,
        descricao:   '',
        features:    [],
        destaque:    false,
      };
    }).filter(p => p.preco_por && p.imagem && parsePrice(p.preco_por) > 10);
  } catch(e) {
    console.warn('[PromoClub] Erro ao carregar produtos:', e);
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
    console.warn('[PromoClub] Erro ao carregar cupons:', e);
    return [];
  }
}

// Outras funções (toast, favs, drawer...) permanecem iguais...
