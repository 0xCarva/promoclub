import json
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

AFILIADO_HINODE = "76173688"
OUTPUT_FILE = "produtos/hinode.json"

def scrape_hinode():
    # ... (mesmo código anterior que estava funcionando com 4+ produtos)
    # (copie a função scrape_hinode_selenium do anterior)
    pass  # vou te dar o completo depois

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

    print(f"💾 Hinode salvo: {len(hinode_prods)} produtos")
