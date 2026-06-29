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
        print(f"Status: {r.status_code} | Tamanho: {len(r.text)} caracteres")

        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Salvar um pedaço da página para debug
        with open("hinode_debug.html", "w", encoding="utf-8") as f:
            f.write(r.text[:50000])  # primeiros 50k caracteres

        print("✅ Página salva como hinode_debug.html (abra no navegador)")

        # Tente diferentes seletores
        possible_selectors = [
            'div.product', 'div.produto', '.product-item', '.item', 
            'div[class*="product"]', 'a[href*="produto"]'
        ]

        for selector in possible_selectors:
            items = soup.select(selector)
            print(f"Selector '{selector}' encontrou {len(items)} itens")

    except Exception as e:
        print(f"Erro: {e}")

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
