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
    preco_por: "R$ 1051,00",
    desconto: "19%",
    avaliacao: 4.4,
    avaliacoes: "88",
    badge: "hot",
    destaque: true,
    estoque: "Mais de 500 vendidos esse mês",
    parcelamento: "12x de R$ 87,62 sem juros",
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

    // ─── iPhone ─────────────────────────────────────────────────
  {
    id: "tcl-32s5k-google-tv",
    nome: "Apple iPhone 17 Pro Max (1 TB) - Laranja cósmico",
    categoria: "Eletrônicos",
    emoji: "📱",
    preco_de: "R$ 15.499,00",
    preco_por: "R$ 11.789,10",
    desconto: "Menor preço em 365 dias",
    avaliacao: 4.4,
    avaliacoes: "88",
    badge: "hot",
    destaque: true,
    estoque: "Mais de 500 vendidos esse mês",
    parcelamento: "12x de R$ 1.091,62 sem juros",
    link: "https://www.amazon.com.br/Apple-iPhone-17-Pro-Max/dp/B0FQHGM3B1?pf_rd_r=ASMA37XV0P78N1SEPAEW&pf_rd_p=ee591aeb-eb2e-4c60-8a96-60d91796b7a0&th=1&linkCode=ll2&tag=carva00-20&linkId=4fadbb519fca7cd2ef70036d483cc9f7&ref_=as_li_ss_tl",
    imagem: "https://m.media-amazon.com/images/I/51k0qRQFcuL._AC_SL1000_.jpg",
    descricao: "O iPhone 17 Pro Max é o smartphone mais avançado da Apple em 2025, combinando desempenho excepcional, câmera profissional e a maior autonomia de bateria da história da linha Pro. Com design premium em titânio, tela Super Retina XDR de 6,9 polegadas com ProMotion 120Hz e brilho de até 3000 nits, ele entrega experiência visual imersiva. Equipado com o poderoso chip A19 Pro, 12 GB de RAM e armazenamento de até 2 TB, é ideal para quem busca o melhor em produtividade, jogos e criação de conteúdo.",
    features: [
      "Tela: 6,9\" Super Retina XDR OLED com ProMotion (1-120Hz), Always-On, brilho de até 3000 nits e Ceramic Shield 2",
      "Processador: Chip A19 Pro (3nm) – até 40% mais rápido que a geração anterior",
      "Memória e Armazenamento: 12 GB RAM | 256 GB / 512 GB / 1 TB / 2 TB",
      "Câmeras Traseiras: 48 MP Principal (f/1.6, OIS), 48 MP Ultra-wide, 48 MP Telefoto (zoom óptico 4x–8x), Scanner LiDAR",
      "Câmera Frontal: 18 MP com Center Stage"
      "Bateria: Maior da história do iPhone (até 39 horas de reprodução de vídeo)"
      "Conectividade: 5G, Wi-Fi 7, USB-C 3.2, UWB de 2ª geração"
      "Outros: iOS 26, IP68, Face ID, alto-falantes estéreo, suporte a Apple Intelligence"
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
