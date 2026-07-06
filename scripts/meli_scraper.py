"""
meli_scraper.py
------------------
Monitora produtos do Mercado Livre, extrai título/imagem/preço, sincroniza
com 'produtos/produtos_meli.json' e envia as novidades/alterações para o
canal do Telegram.

NOTA SOBRE LINKS DE AFILIADO DO MELI:
Os links de afiliado do tipo "mercadolivre.com.br/social/seu_usuario?matt_word=..."
ou os encurtados "meli.la/..." são redirecionamentos. O script segue o
redirecionamento normalmente e extrai os dados da página final do produto,
mas SALVA no JSON a URL de afiliado original (para não perder a comissão),
e não a URL final sem os parâmetros de afiliado.

COMO USAR:
1) Adicione os links de afiliado (curtos ou completos) em PRODUCT_URLS.
2) Defina as variáveis de ambiente/Secrets TELEGRAM_TOKEN e TELEGRAM_CHAT_ID.
3) Rode: python meli_scraper.py
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

# >>> Adicione aqui os seus links de afiliado do Mercado Livre <<<
PRODUCT_URLS = [
    "https://www.mercadolivre.com.br/social/juliofc92?matt_word=promoclub&matt_tool=32776673",
    # "https://meli.la/2hAbCK8",
]

ARQUIVO_JSON = PRODUTOS_DIR / "produtos_meli.json"

TITLE_SELECTORS = ["h1.ui-pdp-title"]
PRICE_SELECTORS = [
    "div.ui-pdp-price__second-line span.andes-money-amount__fraction",
    "span.andes-money-amount__fraction",
]
IMAGE_SELECTORS = [
    "figure.ui-pdp-gallery__figure img",
    ".ui-pdp-image",
]


def extrair_id_mlb(url_final: str) -> str:
    """Tenta extrair o código MLB do produto na URL final do Mercado Livre.
    Caso não encontre (ex: página de social/redirect não resolvida), usa um
    hash da URL original como identificador estável.
    """
    match = re.search(r"(MLB-?\d{6,})", url_final, re.IGNORECASE)
    if match:
        return match.group(1).replace("-", "").upper()
    return hashlib.md5(url_final.encode()).hexdigest()[:16]


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
            src = elemento.get_attribute("src") or elemento.get_attribute("data-src")
            if src:
                return src
    return None


def extrair_dados_produto(page: Page, url_afiliado: str) -> Optional[Dict[str, Any]]:
    """Segue o link de afiliado, espera a página final do produto carregar e
    extrai os dados, mas preserva a URL de afiliado original para o JSON.
    """
    page.goto(url_afiliado, wait_until=NAV_WAIT_UNTIL, timeout=PAGE_TIMEOUT_MS)
    # Links de afiliado às vezes fazem um redirecionamento via JS; aguarda um pouco
    page.wait_for_selector("h1.ui-pdp-title", timeout=PAGE_TIMEOUT_MS)

    url_final = page.url
    produto_id = extrair_id_mlb(url_final)

    titulo = _primeiro_texto(page, TITLE_SELECTORS)
    preco_texto = _primeiro_texto(page, PRICE_SELECTORS)
    imagem = _primeira_imagem(page, IMAGE_SELECTORS)

    if not titulo:
        print(f"[meli] Não foi possível extrair o título de {url_afiliado}")
        return None

    # O texto do preço do ML normalmente vem só com a parte inteira (ex: "1.234")
    preco = parse_preco_brl(preco_texto) if preco_texto else None

    return {
        "id": produto_id,
        "titulo": titulo,
        "preco": preco,
        "preco_texto": preco_texto,
        "imagem": imagem,
        "url": url_afiliado,  # mantém o link de afiliado original, não o final
        "loja": "meli",
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
                    print(f"[meli] OK: {produto['titulo'][:60]} - {produto['preco_texto']}")
            except Exception as erro:
                print(f"[meli] Erro ao processar {url}: {erro}")

        navegador.close()
    return produtos


def main():
    produtos_coletados = coletar_produtos()

    if not produtos_coletados:
        print("[meli] Nenhum produto coletado. Encerrando sem alterar o JSON.")
        return

    produtos_para_notificar, ids_removidos = sincronizar_produtos(ARQUIVO_JSON, produtos_coletados)
    print(f"[meli] JSON atualizado em {ARQUIVO_JSON} ({len(produtos_coletados)} produtos ativos)")
    if ids_removidos:
        print(f"[meli] Produtos removidos (saíram de promoção): {ids_removidos}")

    if produtos_para_notificar:
        enviar_produtos_telegram(produtos_para_notificar)
    else:
        print("[meli] Nenhuma novidade/alteração de preço para notificar.")


if __name__ == "__main__":
    main()
