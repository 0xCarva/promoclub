import json
import requests
import time
import os
from datetime import datetime

# ================== CONFIG (seguro) ==================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("❌ Credenciais Telegram não encontradas.")
    exit(1)

def enviar_produto(p):
    loja = p.get('store', 'Amazon').upper()
    titulo = p.get('title', 'Produto')[:100]
    link = p.get('link', '#')
    price = p.get('price', 'R$ --')
    original = p.get('original_price', '')
    parcelamento = p.get('parcelamento', '')

    caption = f"""🏷️ PROMO DA {loja} CHEGANDO!

➡️ {titulo}

🔗 {link}"""

    if original and original != price and "R$" in original:
        caption += f"\nDe: ~~{original}~~"

    caption += f"""
✅ Por: {price} 🔥"""

    if parcelamento:
        caption += f"\n💳 {parcelamento}"

    caption += """

🛒 PROMO CLUB
https://0xcarva.github.io/promoclub/ofertas.html"""

    try:
        if p.get('image'):
            response = requests.get(p['image'])
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "Markdown"},
                files={"photo": response.content}
            )
        else:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": caption, "parse_mode": "Markdown"}
            )
        print(f"✅ Produto enviado: {titulo[:60]}...")
    except Exception as e:
        print(f"Erro ao enviar produto: {e}")

def enviar_cupom(c, loja="Amazon"):
    codigo = c.get('codigo', 'SEM CÓDIGO')
    desconto = c.get('desconto', '')
    condicao = c.get('condicao', '')
    link = c.get('link', 'https://0xcarva.github.io/promoclub/cupons.html')

    imagem = "cupom_amazon.jpg"
    if "shopee" in loja.lower():
        imagem = "cupom_shopee.jpg"
    elif "meli" in loja.lower() or "mercado" in loja.lower():
        imagem = "cupom_meli.jpg"

    caption = f"""🔥 CUPOM {loja.upper()}

🎟 {codigo}
{desconto} | {condicao}

Confira aqui: 🔗 {link}

🛒 PROMO CLUB
https://0xcarva.github.io/promoclub/cupons.html"""

    try:
        with open(imagem, "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "Markdown"},
                files={"photo": f}
            )
        print(f"✅ Cupom enviado: {codigo}")
    except Exception as e:
        print(f"Erro ao enviar cupom: {e}")

if __name__ == "__main__":
    print(f"📨 Enviando posts limpos para Telegram - {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Carregar produtos
    try:
        with open("produtos.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            produtos = data.get("produtos", [])
    except:
        produtos = []
        print("⚠️ Nenhum produto encontrado no JSON.")

    # Enviar produtos (melhores primeiro)
    sorted_produtos = sorted(produtos, key=lambda x: float(x.get('discount', '0').replace('%', '') or 0), reverse=True)
    for p in sorted_produtos[:6]:   # máximo 6 por vez
        enviar_produto(p)
        time.sleep(5)

    print("✅ Envio concluído!")
