import json
import random
import requests
import time
from datetime import datetime

AFILIADO_TAG = "carva00-20"
OUTPUT_FILE = "produtos.json"
MIN_PRICE = 35

def criar_link_afiliado(asin):
    return f"https://www.amazon.com.br/dp/{asin}?tag={AFILIADO_TAG}&linkCode=ll2"

def parse_price(text):
    if not text: return 0
    import re
    numbers = re.findall(r'[\d.,]+', str(text))
    if numbers:
        return float(numbers[0].replace(',', '.'))
    return 0

def buscar_ofertas():
    produtos = []
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "pt-BR,pt;q=0.9",
    })

    # Foco em páginas mais estáveis
    urls = [
        "https://www.amazon.com.br/deals?ref_=nav_cs_gb",
        "https://www.amazon.com.br/s?k=headset+gamer&crid=2QJ5Z5Z5Z5Z5",
        "https://www.amazon.com.br/s?k=teclado+gamer",
    ]

    print("🔍 Tentando coletar...")

    for url in urls:
        try:
            r = session.get(url, timeout=25)
            print(f"   {url} → {r.status_code}")

            if r.status_code != 200:
                time.sleep(8)
                continue

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, 'html.parser')

            items = soup.select('div[data-asin]')[:40]

            for item in items:
                asin = item.get('data-asin')
                if not asin or len(asin) < 8: continue

                title_tag = item.select_one('h2 span, .a-size-base-plus')
                title = title_tag.get_text(strip=True) if title_tag else ""
                if len(title) < 25: continue

                price_tag = item.select_one('.a-price .a-offscreen')
                price = price_tag.get_text(strip=True) if price_tag else ""
                if parse_price(price) < MIN_PRICE: continue

                img = item.select_one('img')
                image = img['src'] if img else ""

                produtos.append({
                    "title": title[:180],
                    "price": price,
                    "original_price": "",
                    "discount": "",
                    "asin": asin,
                    "image": image,
                    "link": criar_link_afiliado(asin),
                    "store": "Amazon",
                    "badge": "Amazon",
                    "category": "Ofertas",
                })

        except Exception as e:
            print(f"   Erro: {e}")

        time.sleep(random.uniform(10, 18))

    produtos = list({p['asin']: p for p in produtos}.values())
    print(f"✅ Total: {len(produtos)} produtos")
    return produtos

if __name__ == "__main__":
    print(f"🚀 Atualização - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    produtos = buscar_ofertas()

    if produtos:
        data = {
            "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "total_produtos": len(produtos),
            "produtos": produtos
        }
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("💾 JSON atualizado!")
    else:
        print("⚠️ Nenhum produto coletado.")
