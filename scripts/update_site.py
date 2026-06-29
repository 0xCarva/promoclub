import json
import random
import requests
from datetime import datetime

AFILIADO_TAG = "carva00-20"
OUTPUT_FILE = "produtos.json"
MIN_PRICE = 40

def criar_link_afiliado(asin):
    return f"https://www.amazon.com.br/dp/{asin}?tag={AFILIADO_TAG}&linkCode=ll2"

def buscar_ofertas():
    produtos = []
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0 Safari/537.36",
    })

    # Usar página de ofertas do dia (mais estável)
    urls = [
        "https://www.amazon.com.br/deals",
        "https://www.amazon.com.br/s?k=headset+gamer",
        "https://www.amazon.com.br/s?k=teclado+gamer",
        "https://www.amazon.com.br/s?k=monitor+gamer"
    ]

    print("🔍 Tentando coletar ofertas...")

    for url in urls:
        try:
            r = session.get(url, timeout=20)
            print(f"   {url} → Status: {r.status_code}")

            if r.status_code != 200:
                continue

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, 'html.parser')

            # Tentativa com seletores diferentes
            items = soup.select('div[data-asin]')[:30]  # limite para não sobrecarregar

            for item in items:
                asin = item.get('data-asin')
                if not asin or len(asin) < 8:
                    continue

                title = item.select_one('h2, .a-size-base-plus, .a-link-normal')
                title = title.get_text(strip=True) if title else ""

                if len(title) < 30:
                    continue

                price = item.select_one('.a-price .a-offscreen, .a-price')
                price_text = price.get_text(strip=True) if price else ""

                if parse_price(price_text) < MIN_PRICE:
                    continue

                img = item.select_one('img')
                image = img['src'] if img else ""

                produto = {
                    "title": title[:180],
                    "price": price_text,
                    "original_price": "",
                    "discount": "",
                    "asin": asin,
                    "image": image,
                    "link": criar_link_afiliado(asin),
                    "store": "Amazon",
                    "badge": "Amazon",
                    "category": "Promoções",
                }
                produtos.append(produto)

        except Exception as e:
            print(f"   Erro: {e}")
            continue

        time.sleep(random.uniform(5, 10))

    produtos = list({p['asin']: p for p in produtos}.values())
    print(f"✅ Coletados {len(produtos)} produtos")
    return produtos

def parse_price(text):
    if not text: return 0
    import re
    numbers = re.findall(r'[\d.,]+', str(text))
    if numbers:
        return float(numbers[0].replace(',', '.'))
    return 0

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
        print("⚠️ Nada coletado.")
