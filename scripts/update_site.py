import time
import json
import random
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# ================== CONFIG ==================
AFILIADO_TAG = "carva00-20"
MAX_PAGES = 4
MIN_PRICE = 30          # Ignorar produtos muito baratos/ruins
OUTPUT_FILE = "produtos.json"

# ================== FUNÇÕES ==================
def criar_link_afiliado(asin):
    return f"https://www.amazon.com.br/dp/{asin}?tag={AFILIADO_TAG}&linkCode=ll2"

def limpar_texto(texto):
    return " ".join(texto.split()).strip() if texto else ""

def buscar_ofertas_detalhadas():
    produtos = []
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
    })

    # Categorias mais relevantes e com boas promoções
    queries = [
        "headset gamer", "teclado gamer", "mouse gamer", "monitor gamer",
        "tv smart 4k", "notebook gamer", "placa de video", "smartwatch",
        "fones bluetooth", "caixa de som bluetooth", "câmera webcam",
        "ofertas do dia", "tv 4k", "computador gamer"
    ]

    print(f"🔍 Buscando em {len(queries)} categorias...")

    for query in queries:
        for page in range(1, MAX_PAGES + 1):
            url = f"https://www.amazon.com.br/s?k={query.replace(' ', '+')}&page={page}&s=price-asc"
            try:
                r = session.get(url, timeout=30)
                if r.status_code != 200:
                    continue

                soup = BeautifulSoup(r.text, 'html.parser')

                cards = soup.select('div[data-asin][data-component-type="s-search-result"]')

                for card in cards:
                    asin = card.get('data-asin')
                    if not asin or len(asin) < 8:
                        continue

                    # Título
                    title_tag = card.select_one('h2 a span, h2 span')
                    title = limpar_texto(title_tag.get_text()) if title_tag else ""

                    if len(title) < 30:
                        continue

                    # Preços
                    price_tag = card.select_one('.a-price .a-offscreen')
                    price = limpar_texto(price_tag.get_text()) if price_tag else ""

                    original_tag = card.select_one('.a-text-price .a-offscreen')
                    original_price = limpar_texto(original_tag.get_text()) if original_tag else ""

                    preco_num = parse_price(price)
                    if preco_num < MIN_PRICE:
                        continue

                    # Imagem
                    img_tag = card.select_one('img.s-image')
                    image = img_tag['src'] if img_tag else ""

                    produto = {
                        "title": title,
                        "price": price,
                        "original_price": original_price,
                        "discount": "",
                        "asin": asin,
                        "image": image,
                        "link": criar_link_afiliado(asin),
                        "store": "Amazon",
                        "badge": "Amazon",
                        "category": query.title().replace("Gamer", "Gamer"),
                        "description": title[:180] + "..." if len(title) > 180 else title,
                    }
                    produtos.append(produto)

            except Exception as e:
                print(f"   Erro em {query} página {page}: {e}")
                continue

            time.sleep(random.uniform(6, 12))

    # Remover duplicatas
    produtos = list({p['asin']: p for p in produtos}.values())
    print(f"✅ Total final: {len(produtos)} produtos de qualidade")
    return produtos

def parse_price(str_price):
    if not str_price:
        return 0
    cleaned = ''.join(c for c in str_price if c.isdigit() or c in ',.')
    try:
        return float(cleaned.replace(',', '.'))
    except:
        return 0

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

        print(f"💾 {OUTPUT_FILE} atualizado com {len(produtos)} produtos!")
    else:
        print("⚠️ Nenhum produto coletado.")
