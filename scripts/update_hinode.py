import json
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

AFILIADO_HINODE = "76173688"
OUTPUT_FILE = "../produtos/hinode.json"

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
        time.sleep(10)

        for _ in range(6):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)

        items = driver.find_elements(By.CSS_SELECTOR, 'div, article, li, section')

        print(f"Encontrados {len(items)} elementos potenciais")

        for item in items:
            try:
                title = ""
                for sel in ['h1', 'h2', 'h3', '.product-name', '.title', 'span[class*="name"]']:
                    try:
                        el = item.find_element(By.CSS_SELECTOR, sel)
                        title = el.text.strip()
                        if len(title) > 15: break
                    except:
                        continue

                if len(title) < 15: continue

                price = ""
                for sel in ['.price', '.selling-price', '.promocional', 'span[class*="price"]']:
                    try:
                        el = item.find_element(By.CSS_SELECTOR, sel)
                        price = el.text.strip()
                        if price: break
                    except:
                        continue

                if not price: continue

                image = ""
                try:
                    img = item.find_element(By.TAG_NAME, 'img')
                    image = img.get_attribute('src') or img.get_attribute('data-src')
                except:
                    pass

                link = ""
                try:
                    a = item.find_element(By.TAG_NAME, 'a')
                    link = a.get_attribute('href')
                except:
                    pass

                if title and price:
                    produtos.append({
                        "title": title[:180],
                        "price": price,
                        "original_price": "",
                        "discount": "",
                        "image": image,
                        "link": link,
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

    print(f"💾 Salvo em {OUTPUT_FILE}")
