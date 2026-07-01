import json
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

AFILIADO_HINODE = "76173688"
OUTPUT_FILE = "produtos/hinode.json"

def scrape_hinode():
    produtos = []
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(options=options)
    
    try:
        url = f"https://www.hinode.com.br/?id_consultor={AFILIADO_HINODE}"
        driver.get(url)
        time.sleep(12)

        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)

        items = driver.find_elements(By.CSS_SELECTOR, 'div.vtex-product-summary-2-x-element, article, div[class*="product"]')

        for item in items:
            try:
                title = ""
                for sel in ['h2', '.product-name', '.vtex-product-summary-2-x-productName', '.title', 'span']:
                    try:
                        el = item.find_element(By.CSS_SELECTOR, sel)
                        title = el.text.strip()
                        if len(title) > 15: break
                    except:
                        continue

                if len(title) < 15: continue

                price = ""
                for sel in ['.price', '.vtex-product-price-1-x-sellingPrice', '.preco-promocional', '.preco']:
                    try:
                        el = item.find_element(By.CSS_SELECTOR, sel)
                        price = el.text.strip()
                        if price: break
                    except:
                        continue

                if not price: continue

                image_url = ""
                try:
                    img = item.find_element(By.TAG_NAME, 'img')
                    image_url = img.get_attribute('src') or img.get_attribute('data-src')
                except:
                    pass

                link_url = url
                try:
                    link = item.find_element(By.TAG_NAME, 'a')
                    link_url = link.get_attribute('href')
                except:
                    pass

                produtos.append({
                    "title": title[:180],
                    "price": price,
                    "original_price": "",
                    "discount": "",
                    "image": image_url,
                    "link": link_url,
                    "store": "Hinode",
                    "badge": "Hinode",
                    "category": "Beleza",
                })
            except:
                continue

    except Exception as e:
        print(f"Erro Hinode: {e}")
    finally:
        driver.quit()

    print(f"✅ Hinode: {len(produtos)} produtos")
    return produtos

if __name__ == "__main__":
    print("🚀 Atualizando Hinode...")
    hinode_prods = scrape_hinode()
    
    data = {
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total_produtos": len(hinode_prods),
        "produtos": hinode_prods
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 Salvo em produtos/hinode.json")
