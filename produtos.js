// ============================================================
// ARQUIVO DE PRODUTOS — OFERTATOP
// ============================================================

const AFILIADO_TAG = 'carva00-20';

const PRODUTOS = [

  // ─── TV ─────────────────────────────────────────────────
  {
    id: "tcl-32s5k-google-tv",
    nome: "Smart TV TCL 32\" QLED Full HD Google TV Wi-Fi Bluetooth HDR10 Dolby Audio 32S5K",
    categoria: "Eletrônicos",
    emoji: "📺",
    preco_de: "R$ 1.299,00",
    preco_por: "R$ 811,80",
    desconto: "38%",
    avaliacao: 4.4,
    avaliacoes: "88",
    badge: "hot",
    destaque: true,
    estoque: "Mais de 500 vendidos esse mês",
    parcelamento: "12x de R$ 75,24 sem juros",
    link: "https://www.amazon.com.br/TCL-Polegadas-Bluetooth-Google-32S5K/dp/B0FTGL2XBC?linkCode=ll2&tag=carva00-20&linkId=651b459ccf8c5c0db04c85b6113815e1&ref_=as_li_ss_tl",
    imagem: "https://m.media-amazon.com/images/I/61jW+tFc5DL._AC_SL1000_.jpg",
    descricao: "Smart TV compacta com painel QLED Full HD, Google TV nativo com acesso a Netflix, YouTube e Disney+, Chromecast integrado, 20W RMS de som e design sem bordas. Ideal para quarto, escritório ou cozinha.",
    features: [
      "Tela QLED Full HD 32\" com HDR10 e Dolby Audio",
      "Google TV — acesso à Play Store, YouTube, Netflix, Disney+",
      "Chromecast e Miracast integrados",
      "Wi-Fi, Bluetooth 5.0, 2x HDMI, 1x USB, LAN",
      "20W RMS — som mais potente que TVs comuns de 32\""
    ]
  },

];

// ─── NÃO MEXA ABAIXO DESTA LINHA ────────────────────────
// Injeção automática da tag de afiliado em todos os links

function tagAmazonURL(url) {
  if (!url || typeof url !== 'string') return url;
  try {
    if (url.includes('amzn.to') || (url.includes('amzn.') && !url.includes('amazon.com'))) {
      const clean = url.replace(/([?&])tag=[^&]*/g, '$1').replace(/[?&]$/, '');
      const sep = clean.includes('?') ? '&' : '?';
      return clean + sep + 'tag=' + AFILIADO_TAG;
    }
    if (url.includes('amazon.com')) {
      const u = new URL(url);
      u.searchParams.set('tag', AFILIADO_TAG);
      if (!u.searchParams.get('linkCode')) u.searchParams.set('linkCode', 'll2');
      return u.toString();
    }
  } catch(e) {}
  return url;
}

PRODUTOS.forEach(p => { if (p.link) p.link = tagAmazonURL(p.link); });

console.log('[OfertaTop] ' + PRODUTOS.length + ' produtos carregados | tag: ' + AFILIADO_TAG);
