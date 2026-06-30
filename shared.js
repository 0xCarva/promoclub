// shared.js - Versão atualizada
const AFILIADO_TAG = 'carva00-20';

async function loadProdutos() {
  try {
    const res = await fetch('produtos.json');
    const data = await res.json();
    return data.produtos || [];
  } catch(e) {
    console.error('Erro ao carregar produtos', e);
    return [];
  }
}

async function loadCupons() {
  try {
    const res = await fetch('cupons.json');
    const data = await res.json();
    return data || [];
  } catch(e) {
    return [];
  }
}

function parsePrice(str) {
  if (!str) return 0;
  const cleaned = str.replace(/[^0-9,]/g, '').replace(',', '.');
  return parseFloat(cleaned) || 0;
}

function stars(rating) {
  let html = '';
  const full = Math.floor(rating);
  for (let i = 0; i < 5; i++) {
    if (i < full) html += '★';
    else html += '☆';
  }
  return `<span class="text-yellow-400">${html}</span>`;
}

function badgeHTML(badge) {
  if (!badge) return '';
  const cfg = {
    'Hinode': '<span class="absolute top-2 left-2 bg-red-600 text-white text-xs font-bold px-2 py-0.5 rounded">HINODE</span>',
    'Amazon': '<span class="absolute top-2 left-2 bg-yellow-500 text-black text-xs font-bold px-2 py-0.5 rounded">Amazon</span>'
  };
  return cfg[badge] || `<span class="absolute top-2 left-2 bg-gray-700 text-white text-xs font-bold px-2 py-0.5 rounded">${badge}</span>`;
}

function Favs() {
  let favs = JSON.parse(localStorage.getItem('favs') || '[]');
  return {
    has: (id) => favs.includes(id),
    toggle: (id) => {
      if (favs.includes(id)) favs = favs.filter(x=>x!==id);
      else favs.push(id);
      localStorage.setItem('favs', JSON.stringify(favs));
      return favs.includes(id);
    }
  };
}

const FavsInstance = Favs();

function showToast(msg) {
  const t = document.createElement('div');
  t.className = 'fixed bottom-4 left-1/2 -translate-x-1/2 bg-gray-900 border border-white/20 text-white text-xs px-4 py-2 rounded-xl shadow-xl';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2500);
}
