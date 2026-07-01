import json
from datetime import datetime
import requests
import time

# Coloque seu token aqui
ACCESS_TOKEN = "SEU_ACCESS_TOKEN_AQUI"

OUTPUT_FILE = "produtos/mercadolivre.json"

def scrape_mercadolivre():
    produtos = []
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    # Exemplo: busca por promoções
    url = "https://api.mercadolibre.com/sites/MLB/search?sort=price_asc&limit=50"

    try:
        r = requests.get(url, headers=headers, timeout=30)
        data = r.json()

        for item in data.get("results", []):
            produtos.append({
                "title": item["title"][:180],
                "price": f"R$ {item['price']}",
                "original_price": f"R$ {item.get('original_price', item['price'])}",
                "discount": "",
                "image": item["thumbnail"],
                "link": item["permalink"],
                "store": "Mercado Livre",
                "badge": "Mercado Livre",
                "category": item.get("category_id", "Geral"),
            })

    except Exception as e:
        print(f"Erro Mercado Livre: {e}")

    print(f"✅ Mercado Livre: {len(produtos)} produtos")
    return produtos

if __name__ == "__main__":
    print("🚀 Atualizando Mercado Livre...")
    ml_prods = scrape_mercadolivre()
    
    data = {
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total_produtos": len(ml_prods),
        "produtos": ml_prods
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 Salvo em produtos/mercadolivre.json")
