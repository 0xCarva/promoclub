import time
import json
import random
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# ================== CONFIGURAÇÕES ==================
AFILIADO_TAG = "carva00-20"
MAX_PAGES = 3
OUTPUT_FILE = "produtos.json"

# ================== FUNÇÕES ==================
def criar_link_afiliado(asin):
    return f"https://www.amazon.com.br/dp/{asin}?tag={AFILIADO_TAG}&linkCode=ll2"

def buscar_ofertas_detalhadas():
    produtos = []
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
    })

    queries = ["headset gamer", "teclado gamer", "mouse gamer", "monitor gamer", "tv smart", "ofertas do dia"]

    print(f"🔍 Buscando ofertas em {len(queries)} categorias...")

    for query in queries:
        for page in range(1, MAX_PAGES + 1):
            url = f"https://www.amazon.com.br/s?k={query.replace(' ', '+')}&page={page}"
            try:
                r = session.get(url, timeout=25)
                print(f"   → {query} | Página {page} | Status: {r.status_code}")

                soup = BeautifulSoup(r.text, 'html.parser')

                cards = (
                    soup.select('div[data-asin][data-component-type="s-search-result"]') or
                    soup.select('div.s-result-item') or
                    soup.select('div[data-asin]')
                )

                for card in cards:
                    asin = card.get('data-asin')
                    if not asin or len(asin) < 8:
                        continue

                    title_tag = card.select_one('h2 span, h2 a span, .a-size-base-plus')
                    title = title_tag.get_text(strip=True) if title_tag else ""

                    price_tag = card.select_one('.a-price .a-offscreen, .a-price-whole')
                    price = price_tag.get_text(strip=True) if price_tag else ""

                    if not title or not price or "R$" not in price or len(title) < 25:
                        continue

                    original_tag = card.select_one('.a-text-price .a-offscreen')
                    original_price = original_tag.get_text(strip=True) if original_tag else ""

                    discount_tag = card.select_one('.a-badge-text')
                    discount = discount_tag.get_text(strip=True) if discount_tag else ""

                    img_tag = card.select_one('img.s-image')
                    image = img_tag['src'] if img_tag else ""

                    produto = {
                        "title": title,
                        "price": price,
                        "original_price": original_price,
                        "discount": discount,
                        "asin": asin,
                        "image": image,
                        "link": criar_link_afiliado(asin),
                        "store": "Amazon",
                        "badge": "Amazon",
                        "installments": "",
                        "category": query.title(),
                    }
                    produtos.append(produto)

            except Exception as e:
                print(f"   Erro na página {page} de {query}: {e}")
                continue

            time.sleep(random.uniform(8, 15))  # Delay anti-block

    # Remove duplicatas
    produtos = list({p['asin']: p for p in produtos}.values())
    print(f"✅ Total coletado: {len(produtos)} produtos únicos")
    return produtos

# ================== EXECUÇÃO PRINCIPAL ==================
if __name__ == "__main__":
    print(f"🚀 Iniciando atualização do PromoClub - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    produtos = buscar_ofertas_detalhadas()

    if produtos:
        data = {
            "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "total_produtos": len(produtos),
            "produtos": produtos
        }

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"💾 Arquivo {OUTPUT_FILE} atualizado com sucesso!")
    else:
        print("⚠️ Nenhum produto encontrado.")
