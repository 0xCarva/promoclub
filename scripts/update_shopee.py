import json
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

OUTPUT_FILE = "produtos/shopee.json"

def scrape_shopee():
    produtos = []
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(options=options)
    
    try:
        url = "https://shopee.com.br/search?keyword=promo%C3%A7%C3%A3o"
        driver.get(url)
        time.sleep(10)

        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)

        items = driver.find_elements(By.CSS_SELECTOR, 'div.shopee-search-item-result__item')

        print(f"Encontrados {len(items)} elementos potenciais")

        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, 'div[data-sqe="name"] div').text.strip()
                if len(title) < 15: continue

                price = item.find_element(By.CSS_SELECTOR, 'div[data-sqe="price"] span').text.strip()
                if not price: continue

                image = item.find_element(By.TAG_NAME, 'img').get_attribute('src')
                link = item.find_element(By.TAG_NAME, 'a').get_attribute('href')

                produtos.append({
                    "title": title[:180],
                    "price": price,
                    "original_price": "",
                    "discount": "",
                    "image": image,
                    "link": "https://shopee.com.br" + link,
                    "store": "Shopee",
                    "badge": "Shopee",
                    "category": "Geral",
                })
            except:
                continue

    except Exception as e:
        print(f"Erro Shopee: {e}")
    finally:
        driver.quit()

    print(f"✅ Shopee: {len(produtos)} produtos")
    return produtos

if __name__ == "__main__":
    print("🚀 Atualizando Shopee...")
    shopee_prods = scrape_shopee()
    
    data = {
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total_produtos": len(shopee_prods),
        "produtos": shopee_prods
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 Salvo em {OUTPUT_FILE}")
