"""
shopee_scraper.py
-------------------
Monitora produtos da Shopee, extrai título/imagem/preço, sincroniza com
'produtos/produtos_shopee.json' e envia as novidades/alterações para o
canal do Telegram.

NOTA IMPORTANTE SOBRE A SHOPEE:
A Shopee usa nomes de classes CSS gerados/ofuscados que mudam com frequência,
então este script prioriza as tags Open Graph (<meta property="og:...">) da
página, que são muito mais estáveis, e só usa seletores de texto como
fallback. Se a Shopee alterar o layout e a extração falhar, verifique
primeiro se as tags og:title/og:image continuam presentes no HTML.

COMO USAR:
1) Adicione os links (podem ser os links curtos "s.shopee.com.br/...", o
   script segue o redirecionamento automaticamente) na lista PRODUCT_URLS.
2) Defina as variáveis de ambiente/Secrets TELEGRAM_TOKEN e TELEGRAM_CHAT_ID.
3) Rode: python shopee_scraper.py
"""

import hashlib
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from playwright.sync_api import sync_playwright, Page

sys.path.append(str(Path(__file__).resolve().parent))
from common.config import HEADLESS, NAV_WAIT_UNTIL, PAGE_TIMEOUT_MS, PRODUTOS_DIR
from common.json_utils import parse_preco_brl, sincronizar_produtos
from common.telegram_utils import enviar_produtos_telegram

# >>> Adicione aqui os links (curtos ou completos) de produtos da Shopee <<<
PRODUCT_URLS = [
    "https://s.shopee.com.br/5q6NDf954Z",
    # "https://shopee.com.br/outro-produto-i.123456.789012",
]

ARQUIVO_JSON = PRODUTOS_DIR / "produtos_shopee.json"

# Seletores de fallback (caso as tags Open Graph não estejam disponíveis)
PRICE_SELECTORS_FALLBACK = [
    "div[class*='pqTWkA']",  # classes da Shopee mudam com frequência - ajuste se necessário
    "[class*='product-price'] span",
]


def _meta_content(page: Page, propriedade: str) -> Optional[str]:
    elemento = page.locator(f'meta[property="{propriedade}"]').first
    if elemento.count() > 0:
        return elemento.get_attribute("content")
    return None


def extrair_id_produto(url_final: str) -> str:
    """Tenta extrair o padrão shopid.itemid da URL final da Shopee.
    Caso não encontre, usa um hash da URL como identificador estável.
    """
    match = re.search(r"i\.(\d+)\.(\d+)", url_final)
    if match:
        return f"{match.group(1)}_{match.group(2)}"
    return hashlib.md5(url_final.encode()).hexdigest()[:16]


def extrair_dados_produto(page: Page, url_original: str) -> Optional[Dict[str, Any]]:
    """Abre o link (segue redirecionamento se for link curto) e extrai os dados."""
    page.goto(url_original, wait_until=NAV_WAIT_UNTIL, timeout=PAGE_TIMEOUT_MS)
    # Aguarda o redirecionamento/JS terminar de carregar o conteúdo
    page.wait_for_timeout(2500)

    url_final = page.url
    produto_id = extrair_id_produto(url_final)

    titulo = _meta_content(page, "og:title")
    imagem = _meta_content(page, "og:image")
    preco_texto = _meta_content(page, "product:price:amount") or _meta_content(page, "og:price:amount")

    if not preco_texto:
        for seletor in PRICE_SELECTORS_FALLBACK:
            elemento = page.locator(seletor).first
            if elemento.count() > 0:
                texto = elemento.inner_text(timeout=3000).strip()
                if texto:
                    preco_texto = texto
                    break

    if not titulo:
        print(f"[shopee] Não foi possível extrair o título de {url_original}")
        return None

    preco = parse_preco_brl(preco_texto) if preco_texto else None

    return {
        "id": produto_id,
        "titulo": titulo,
        "preco": preco,
        "preco_texto": preco_texto,
        "imagem": imagem,
        "url": url_final,
        "loja": "shopee",
    }


def coletar_produtos() -> list[Dict[str, Any]]:
    produtos = []
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=HEADLESS)
        contexto = navegador.new_context(
            locale="pt-BR",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
            ),
        )
        page = contexto.new_page()

        for url in PRODUCT_URLS:
            try:
                produto = extrair_dados_produto(page, url)
                if produto:
                    produtos.append(produto)
                    print(f"[shopee] OK: {produto['titulo'][:60]} - {produto['preco_texto']}")
            except Exception as erro:
                print(f"[shopee] Erro ao processar {url}: {erro}")

        navegador.close()
    return produtos


def main():
    produtos_coletados = coletar_produtos()

    if not produtos_coletados:
        print("[shopee] Nenhum produto coletado. Encerrando sem alterar o JSON.")
        return

    produtos_para_notificar, ids_removidos = sincronizar_produtos(ARQUIVO_JSON, produtos_coletados)
    print(f"[shopee] JSON atualizado em {ARQUIVO_JSON} ({len(produtos_coletados)} produtos ativos)")
    if ids_removidos:
        print(f"[shopee] Produtos removidos (saíram de promoção): {ids_removidos}")

    if produtos_para_notificar:
        enviar_produtos_telegram(produtos_para_notificar)
    else:
        print("[shopee] Nenhuma novidade/alteração de preço para notificar.")


if __name__ == "__main__":
    main()
