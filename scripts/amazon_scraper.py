"""
amazon_scraper.py
------------------
Monitora produtos da Amazon Brasil, extrai título/imagem/preço, sincroniza
com 'produtos/produtos_amazon.json' e envia as novidades/alterações para o
canal do Telegram.

COMO USAR:
1) Adicione os links dos produtos (com ou sem a tag de afiliado, tanto faz)
   na lista PRODUCT_URLS abaixo.
2) Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID em common/config.py.
3) Rode: python amazon_scraper.py
"""

import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from playwright.sync_api import sync_playwright, Page

sys.path.append(str(Path(__file__).resolve().parent))
from common.config import AMAZON_AFFILIATE_TAG, HEADLESS, NAV_WAIT_UNTIL, PAGE_TIMEOUT_MS, PRODUTOS_DIR
from common.json_utils import parse_preco_brl, sincronizar_produtos
from common.telegram_utils import enviar_produtos_telegram

# >>> Adicione aqui os links dos produtos da Amazon que você quer monitorar <<<
PRODUCT_URLS = [
    "https://www.amazon.com.br/Novo-Echo-Studio/dp/B0DXNFVJ9H",
    # "https://www.amazon.com.br/dp/OUTRO_ASIN",
]

ARQUIVO_JSON = PRODUTOS_DIR / "produtos_amazon.json"

TITLE_SELECTORS = ["#productTitle"]
PRICE_SELECTORS = [
    "#corePriceDisplay_desktop_feature_div .a-price .a-offscreen",
    "#corePrice_feature_div .a-price .a-offscreen",
    ".a-price .a-offscreen",
    "#priceblock_ourprice",
    "#priceblock_dealprice",
]
IMAGE_SELECTORS = ["#landingImage", "#imgTagWrapperId img"]


def extrair_asin(url: str) -> Optional[str]:
    """Extrai o ASIN (identificador único do produto na Amazon) da URL."""
    match = re.search(r"/dp/([A-Z0-9]{10})", url) or re.search(r"/gp/product/([A-Z0-9]{10})", url)
    return match.group(1) if match else None


def montar_link_afiliado(asin: str) -> str:
    """Monta um link de afiliado limpo e padronizado a partir do ASIN."""
    return f"https://www.amazon.com.br/dp/{asin}?tag={AMAZON_AFFILIATE_TAG}"


def _primeiro_texto(page: Page, seletores: list[str]) -> Optional[str]:
    for seletor in seletores:
        elemento = page.locator(seletor).first
        if elemento.count() > 0:
            texto = elemento.inner_text(timeout=3000).strip()
            if texto:
                return texto
    return None


def _primeira_imagem(page: Page, seletores: list[str]) -> Optional[str]:
    for seletor in seletores:
        elemento = page.locator(seletor).first
        if elemento.count() > 0:
            src = elemento.get_attribute("src") or elemento.get_attribute("data-old-hires")
            if src:
                return src
    return None


def extrair_dados_produto(page: Page, url_original: str) -> Optional[Dict[str, Any]]:
    """Abre a página do produto e extrai título, preço e imagem."""
    asin = extrair_asin(url_original)
    if not asin:
        print(f"[amazon] ASIN não encontrado em: {url_original}")
        return None

    link_afiliado = montar_link_afiliado(asin)
    page.goto(link_afiliado, wait_until=NAV_WAIT_UNTIL, timeout=PAGE_TIMEOUT_MS)

    titulo = _primeiro_texto(page, TITLE_SELECTORS)
    preco_texto = _primeiro_texto(page, PRICE_SELECTORS)
    imagem = _primeira_imagem(page, IMAGE_SELECTORS)

    if not titulo:
        print(f"[amazon] Não foi possível extrair o título de {link_afiliado}")
        return None

    preco = parse_preco_brl(preco_texto) if preco_texto else None

    return {
        "id": asin,
        "titulo": titulo,
        "preco": preco,
        "preco_texto": preco_texto,
        "imagem": imagem,
        "url": link_afiliado,
        "loja": "amazon",
    }


def coletar_produtos() -> list[Dict[str, Any]]:
    """Percorre todos os links de PRODUCT_URLS e coleta os dados de cada um."""
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
                    print(f"[amazon] OK: {produto['titulo'][:60]} - {produto['preco_texto']}")
            except Exception as erro:
                # Evita que um erro em um produto derrube a coleta dos outros
                print(f"[amazon] Erro ao processar {url}: {erro}")

        navegador.close()
    return produtos


def main():
    produtos_coletados = coletar_produtos()

    if not produtos_coletados:
        print("[amazon] Nenhum produto coletado. Encerrando sem alterar o JSON.")
        return

    # 1) Primeiro salva/atualiza/remove no JSON
    produtos_para_notificar, ids_removidos = sincronizar_produtos(ARQUIVO_JSON, produtos_coletados)
    print(f"[amazon] JSON atualizado em {ARQUIVO_JSON} ({len(produtos_coletados)} produtos ativos)")
    if ids_removidos:
        print(f"[amazon] Produtos removidos (saíram de promoção): {ids_removidos}")

    # 2) Só depois envia para o Telegram os produtos novos ou com preço alterado
    if produtos_para_notificar:
        enviar_produtos_telegram(produtos_para_notificar)
    else:
        print("[amazon] Nenhuma novidade/alteração de preço para notificar.")


if __name__ == "__main__":
    main()
