import json
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

OUTPUT_FILE = "produtos/amazon.json"
AFILIADO_TAG = "carva00-20"

def scrape_amazon():
    produtos = []
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(options=options)
    
    try:
        url = "https://www.amazon.com.br/deals?tag=" + AFILIADO_TAG
        driver.get(url)
        time.sleep(8)

        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)

        items = driver.find_elements(By.CSS_SELECTOR, 'div.deal, div.grid-item, div.product')

        print(f"Encontrados {len(items)} elementos potenciais")

        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, 'h2, .title, .deal-title').text.strip()
                if len(title) < 15: continue

                price = item.find_element(By.CSS_SELECTOR, '.price, .a-price, .deal-price').text.strip()
                if not price: continue

                image = item.find_element(By.TAG_NAME, 'img').get_attribute('src')
                link = item.find_element(By.TAG_NAME, 'a').get_attribute('href')

                produtos.append({
                    "title": title[:180],
                    "price": price,
                    "original_price": "",
                    "discount": "",
                    "image": image,
                    "link": link,
                    "store": "Amazon",
                    "badge": "Amazon",
                    "category": "Geral",
                })
            except:
                continue

    except Exception as e:
        print(f"Erro Amazon: {e}")
    finally:
        driver.quit()

    print(f"✅ Amazon: {len(produtos)} produtos")
    return produtos

if __name__ == "__main__":
    print("🚀 Atualizando Amazon...")
    amazon_prods = scrape_amazon()
    
    data = {
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total_produtos": len(amazon_prods),
        "produtos": amazon_prods
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 Salvo em {OUTPUT_FILE}")
