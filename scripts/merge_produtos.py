import json
from datetime import datetime
from pathlib import Path

def merge_all():
    all_produtos = []
    sources = ["amazon", "hinode", "shopee", "mercadolivre"]

    for source in sources:
        file = Path(f"produtos/{source}.json")
        if file.exists():
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    produtos = data.get("produtos", [])
                    for p in produtos:
                        p["source"] = source
                    all_produtos.extend(produtos)
                print(f"✅ Carregado {len(produtos)} de {source}")
            except:
                print(f"⚠️ Erro ao carregar {source}")

    data = {
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total_produtos": len(all_produtos),
        "produtos": all_produtos
    }

    with open("produtos.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 Total combinado: {len(all_produtos)} produtos")

if __name__ == "__main__":
    merge_all()
