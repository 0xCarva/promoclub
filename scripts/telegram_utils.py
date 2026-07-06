"""
telegram_utils.py
------------------
Funções para formatar e enviar mensagens de promoção para o canal do
Telegram, usando a API HTTP de Bot do Telegram (sem precisar de SDK extra,
apenas a biblioteca 'requests').
"""

import time
from typing import Any, Dict, List

import requests

from .config import TELEGRAM_CHAT_ID, TELEGRAM_TOKEN


def montar_legenda(produto: Dict[str, Any]) -> str:
    """Monta o texto (caption) da mensagem de promoção em Markdown."""
    titulo = produto.get("titulo", "Produto")
    preco = produto.get("preco")
    preco_anterior = produto.get("preco_anterior")
    url = produto.get("url", "")
    loja = produto.get("loja", "").capitalize()

    preco_fmt = f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if preco else "Consulte o site"

    linhas = [f"🔥 *{titulo}*", ""]

    if preco_anterior and preco and preco_anterior > preco:
        preco_ant_fmt = (
            f"R$ {preco_anterior:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        linhas.append(f"~{preco_ant_fmt}~ ➜ *{preco_fmt}*")
    else:
        linhas.append(f"💰 *{preco_fmt}*")

    linhas.append("")
    linhas.append(f"🏬 Loja: {loja}")
    linhas.append(f"🔗 [Ver oferta]({url})")

    return "\n".join(linhas)


def enviar_produto_telegram(produto: Dict[str, Any]) -> bool:
    """Envia um único produto para o canal configurado.

    Usa sendPhoto (com a imagem do produto) quando disponível; caso não haja
    imagem, cai para sendMessage. Retorna True se o Telegram confirmou o envio.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError(
            "As variáveis de ambiente TELEGRAM_TOKEN e TELEGRAM_CHAT_ID não estão "
            "definidas. Configure-as como Secrets do GitHub Actions ou exporte-as "
            "localmente antes de rodar o script."
        )

    legenda = montar_legenda(produto)
    imagem = produto.get("imagem")
    base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

    try:
        if imagem:
            resposta = requests.post(
                f"{base_url}/sendPhoto",
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "caption": legenda,
                    "parse_mode": "Markdown",
                    "photo": imagem,
                },
                timeout=15,
            )
        else:
            resposta = requests.post(
                f"{base_url}/sendMessage",
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": legenda,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False,
                },
                timeout=15,
            )

        resposta.raise_for_status()
        return resposta.json().get("ok", False)

    except requests.RequestException as erro:
        print(f"[telegram] Falha ao enviar '{produto.get('titulo')}': {erro}")
        return False


def enviar_produtos_telegram(produtos: List[Dict[str, Any]], intervalo_segundos: float = 2.0) -> None:
    """Envia uma lista de produtos, um por um, com um pequeno intervalo entre
    envios para respeitar os limites de taxa (rate limit) do Telegram.
    """
    for produto in produtos:
        sucesso = enviar_produto_telegram(produto)
        status = "OK" if sucesso else "FALHOU"
        print(f"[telegram] {status}: {produto.get('titulo')}")
        time.sleep(intervalo_segundos)
