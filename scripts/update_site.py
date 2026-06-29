import time
import json
import random
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# ================== CONFIG ==================
AFILIADO_TAG = "carva00-20"
MAX_PAGES = 3
MIN_PRICE = 25
OUTPUT_FILE = "produtos.json"

# ================== HELPERS ==================
def criar_link_afiliado(asin):
    return f"https://www.amazon.com.br/dp/{asin}?tag={AFILIADO_TAG}&linkCode=ll2"

def limpar_texto(texto):
    return " ".join(str(texto).split()).strip() if texto else ""

def parse_price(text):
    if not text: return 0
    cleaned = ''.join(c for c in str(text) if c.isdigit() or c in ',.')
    try:
        return float(cleaned.replace(',', '.'))
    except:
        return 0

# ================== SCRAPER ==================
def buscar_ofertas_detalhadas():
    produtos = []
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
    })

    queries = [
        "headset gamer", "teclado gamer", "mouse gamer", "monitor gamer",
        "tv smart 4k", "notebook", "fones bluetooth", "caixa de som",
        "smartwatch", "ofertas do dia"
    ]

    print(f"🔍 Buscando em {len(queries)} categorias...")

    for query in queries:
        for page in range(1, MAX_PAGES + 1):
            url = f"https://www.amazon.com.br/s?k={query.replace(' ', '+')}&page={page}"
            try:
                r = session.get(url, timeout=30)
                print(f"   → {query} | P{page} | {r.status_code}")

                soup = BeautifulSoup(r.text, 'html.parser')

                # Seletores mais amplos e resistentes
                cards = soup.find_all('div', attrs={'data-asin': True})

                for card in cards:
                    asin = card.get('data-asin')
                    if not asin or len(asin) < 8:
                        continue

                    # Título
                    title = limpar_texto(card.select_one('h2 a span, h2 span, .a-size-medium'))
                    if not title or len(title) < 25:
                        continue

                    # Preço atual
                    price_tag = card.select_one('.a-price .a-offscreen, .a-price-whole, .a-price')
                    price = limpar_texto(price_tag) if price_tag else ""

                    preco_num = parse_price(price)
                    if preco_num < MIN_PRICE:
                        continue

                    # Preço original
                    original = limpar_texto(card.select_one('.a-text-price .a-offscreen'))

                    # Imagem
                    img = card.select_one('img.s-image')
                    image = img['src'] if img else ""

                    produto = {
                        "title": title,
                        "price": price,
                        "original_price": original,
                        "discount": "",
                        "asin": asin,
                        "image": image,
                        "link": criar_link_afiliado(asin),
                        "store": "Amazon",
                        "badge": "Amazon",
                        "category": query.title(),
                        "description": title[:200],
                    }
                    produtos.append(produto)

            except Exception as e:
                print(f"   Erro: {e}")
                continue

            time.sleep(random.uniform(7, 14))

    produtos = list({p['asin']: p for p in produtos}.values())
    print(f"✅ Total coletado: {len(produtos)} produtos")
    return produtos

# ================== MAIN ==================
if __name__ == "__main__":
    print(f"🚀 Atualização Amazon - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    produtos = buscar_ofertas_detalhadas()

    if produtos:
        data = {
            "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "total_produtos": len(produtos),
            "produtos": produtos
        }
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Salvo {len(produtos)} produtos!")
    else:
        print("⚠️ Nenhum produto coletado.")
