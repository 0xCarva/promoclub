import json
import requests
import time
from datetime import datetime

# ================== CONFIG ==================
TOKEN = ""          # Cole seu token aqui
CHAT_ID = ""        # Cole seu chat ID aqui

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

    if original and original != price:
        caption += f"\nDe: ~~{original}~~"

    caption += f"""
✅ Por: {price} 🔥"""

    if parcelamento:
        caption += f"\n💳 {parcelamento}"

    caption += """

🛒 PROMO CLUB
https://0xcarva.github.io/promoclub/ofertas.html"""

    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                      data={
                          "chat_id": CHAT_ID,
                          "caption": caption,
                          "parse_mode": "Markdown"
                      },
                      files={"photo": requests.get(p['image']).content} if p.get('image') else None)
        print(f"✅ Produto enviado: {titulo[:50]}")
    except Exception as e:
        print(f"Erro ao enviar produto: {e}")

def enviar_cupom(c, loja="Amazon"):
    codigo = c.get('codigo', '')
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
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                          data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "Markdown"},
                          files={"photo": f})
        print(f"✅ Cupom enviado: {codigo}")
    except Exception as e:
        print(f"Erro ao enviar cupom: {e}")

# ================== EXECUÇÃO ==================
if __name__ == "__main__":
    print(f"📨 Enviando para Telegram - {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Carregar produtos
    try:
        with open("produtos.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            produtos = data.get("produtos", [])
    except:
        produtos = []

    # Enviar 5 melhores produtos
    for p in sorted(produtos, key=lambda x: x.get('discount', ''), reverse=True)[:5]:
        enviar_produto(p)
        time.sleep(4)

    print("✅ Envio concluído!")
