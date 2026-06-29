import json
from datetime import datetime
import random
import time

try:
    from amzpy import AmazonScraper
except ImportError:
    print("amzpy não encontrado. Usando fallback.")
    AmazonScraper = None

AFILIADO_TAG = "carva00-20"
OUTPUT_FILE = "produtos.json"
MIN_PRICE = 35

def main():
    print(f"🚀 Atualização Amazon - {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    produtos = []

    if AmazonScraper:
        try:
            scraper = AmazonScraper()
            print("✅ amzpy carregado")

            searches = ["headset gamer", "teclado gamer", "monitor gamer"]

            for query in searches:
                try:
                    print(f"🔍 Buscando: {query}")
                    # Método correto do amzpy
                    results = scraper.get_search_results(query, page=1)
                    
                    for item in results.get('products', [])[:20]:
                        asin = item.get('asin')
                        if not asin: continue

                        price = item.get('price', 0)
                        if price < MIN_PRICE: continue

                        produto = {
                            "title": str(item.get('title', ''))[:180],
                            "price": f"R$ {price:,.2f}".replace(',', '.'),
                            "original_price": str(item.get('original_price', '')),
                            "asin": asin,
                            "image": item.get('image_url', ''),
                            "link": f"https://www.amazon.com.br/dp/{asin}?tag={AFILIADO_TAG}",
                            "store": "Amazon",
                            "badge": "Amazon",
                            "category": query.title(),
                        }
                        produtos.append(produto)
                except Exception as e:
                    print(f"   Erro em {query}: {e}")
                time.sleep(random.uniform(8, 15))
        except Exception as e:
            print(f"Erro ao usar amzpy: {e}")

    # Se não pegou nada, podemos voltar para requests (mas por enquanto só amzpy)

    produtos = list({p['asin']: p for p in produtos}.values())

    if produtos:
        data = {
            "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "total_produtos": len(produtos),
            "produtos": produtos
        }
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ {len(produtos)} produtos salvos!")
    else:
        print("⚠️ Nenhum produto coletado.")

if __name__ == "__main__":
    main()
