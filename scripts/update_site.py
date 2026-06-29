import json
from datetime import datetime
from amzpy import AmazonScraper
import random

AFILIADO_TAG = "carva00-20"
OUTPUT_FILE = "produtos.json"
MIN_PRICE = 35

def main():
    print(f"🚀 Atualização Amazon com amzpy - {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    scraper = AmazonScraper(
        locale="br",
        user_agent_rotation=True,
        delay=(8, 15)
    )

    produtos = []

    # Buscas principais
    searches = [
        "headset gamer",
        "teclado gamer",
        "mouse gamer",
        "monitor gamer",
        "tv smart 4k",
        "notebook gamer",
        "fones bluetooth"
    ]

    for query in searches:
        try:
            print(f"🔍 Buscando: {query}")
            results = scraper.search(query, max_pages=2)

            for item in results:
                if not item.get('asin') or not item.get('title'):
                    continue

                price = item.get('price', 0)
                if price < MIN_PRICE:
                    continue

                produto = {
                    "title": item['title'][:180],
                    "price": f"R$ {price:,.2f}".replace(',', '.'),
                    "original_price": item.get('original_price', ''),
                    "discount": item.get('discount', ''),
                    "asin": item['asin'],
                    "image": item.get('image', ''),
                    "link": f"https://www.amazon.com.br/dp/{item['asin']}?tag={AFILIADO_TAG}&linkCode=ll2",
                    "store": "Amazon",
                    "badge": "Amazon",
                    "category": query.title(),
                }
                produtos.append(produto)

            time.sleep(random.uniform(5, 10))

        except Exception as e:
            print(f"   Erro em {query}: {e}")

    # Remover duplicatas
    produtos = list({p['asin']: p for p in produtos}.values())

    if produtos:
        data = {
            "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "total_produtos": len(produtos),
            "produtos": produtos
        }
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Sucesso! {len(produtos)} produtos salvos.")
    else:
        print("⚠️ Nenhum produto coletado.")

if __name__ == "__main__":
    main()
