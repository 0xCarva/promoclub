import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def update_amazon_devices():
    print("🔄 Monitorando dispositivos Amazon...")

    products = [
        "B0DYC5S7DK",
        "B0DXNFVJ9H",
        "B0CJLFQP4W"
    ]

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resultados = []

    for asin in products:
        try:
            url = f"https://www.amazon.com.br/dp/{asin}"
            r = requests.get(url, headers=headers, timeout=15)
            
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                
                title = soup.find('span', id='productTitle')
                title = title.get_text(strip=True) if title else f"Produto {asin}"
                
                price = soup.find('span', class_='a-price-whole')
                price = price.get_text(strip=True) if price else "N/A"
                
                resultados.append({
                    "asin": asin,
                    "title": title[:120],
                    "price": price,
                    "url": url,
                    "last_checked": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                print(f"✅ {asin} - OK")
            else:
                print(f"⚠️ Erro ao acessar {asin}")
        except Exception as e:
            print(f"Erro {asin}:", e)

    # Salva para o site
    dados = {
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "store": "Amazon Devices",
        "produtos": resultados
    }

    with open("produtos/amazon_devices.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f"✅ Monitoramento concluído! {len(resultados)} produtos salvos.")

if __name__ == "__main__":
    update_amazon_devices()
