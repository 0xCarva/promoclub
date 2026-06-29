import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import time
import random

OUTPUT_FILE = "produtos.json"  # Vamos mesclar com os outros
AFILIADO_HINODE = "76173688"   # seu ID de consultor

def scrape_hinode():
    produtos = []
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })

    url = f"https://www.hinode.com.br/?id_consultor={AFILIADO_HINODE}"

    try:
        r = session.get(url, timeout=30)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Ajustar conforme a estrutura real da Hinode
        items = soup.select('div.product-item, .produto, .item-produto')  # ajuste os seletores

        for item in items:
            title = item.select_one('h2, .product-name, .titulo')
            title = title.get_text(strip=True) if title else ""

            price = item.select_one('.price, .preco, .valor')
            price_text = price.get_text(strip=True) if price else ""

            original_price = item.select_one('.old-price, .preco-antigo')
            original_text = original_price.get_text(strip=True) if original_price else ""

            image = item.select_one('img')
            image_url = image['src'] if image else ""

            link = item.select_one('a')
            link_url = link['href'] if link else url

            if title and price_text:
                produtos.append({
                    "title": title[:180],
                    "price": price_text,
                    "original_price": original_text,
                    "discount": "",
                    "image": image_url if image_url.startswith('http') else f"https://www.hinode.com.br{image_url}",
                    "link": link_url if link_url.startswith('http') else f"https://www.hinode.com.br{link_url}",
                    "store": "Hinode",
                    "badge": "Hinode",
                    "category": "Beleza",  # vamos melhorar depois
                    "asin": "",  # Hinode não usa ASIN
                })

    except Exception as e:
        print(f"Erro ao raspar Hinode: {e}")

    print(f"✅ Hinode: {len(produtos)} produtos encontrados")
    return produtos

if __name__ == "__main__":
    print("🚀 Atualizando Hinode...")
    hinode_prods = scrape_hinode()
    
    # Carregar produtos existentes e mesclar
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {"ultima_atualizacao": "", "total_produtos": 0, "produtos": []}

    # Remover antigos da Hinode e adicionar novos
    data["produtos"] = [p for p in data["produtos"] if p.get("store") != "Hinode"]
    data["produtos"].extend(hinode_prods)
    data["ultima_atualizacao"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    data["total_produtos"] = len(data["produtos"])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 Total no site: {data['total_produtos']} produtos")
