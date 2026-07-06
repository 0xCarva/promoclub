"""
json_utils.py
-------------
Funções para carregar, salvar e sincronizar os arquivos JSON de produtos
(produtos_amazon.json, produtos_shopee.json, produtos_meli.json, etc).

Cada JSON é salvo como um dicionário {id_produto: {...dados...}} para
permitir atualização/remoção rápida por chave, mas o script sempre grava
no arquivo final como uma lista (mais fácil de consumir no front-end do
GitHub Pages).
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


def parse_preco_brl(texto: str) -> float | None:
    """Converte um texto de preço brasileiro (ex: 'R$ 1.234,56') em float (1234.56).
    Retorna None se não conseguir interpretar o texto.
    """
    if not texto:
        return None
    limpo = re.sub(r"[^\d,.-]", "", texto).strip()
    if not limpo:
        return None
    # Formato BR: milhar com ponto, decimal com vírgula
    limpo = limpo.replace(".", "").replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return None


def _carregar_bruto(caminho_json: Path) -> Dict[str, Any]:
    """Lê o arquivo JSON existente e devolve um dict indexado por id.
    Se o arquivo não existir ou estiver corrompido, devolve dict vazio.
    """
    if not caminho_json.exists():
        return {}
    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            conteudo = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

    # Aceita tanto uma lista quanto um dict já salvo anteriormente
    if isinstance(conteudo, list):
        return {p["id"]: p for p in conteudo if "id" in p}
    if isinstance(conteudo, dict):
        return conteudo
    return {}


def _salvar_bruto(caminho_json: Path, produtos_dict: Dict[str, Any]) -> None:
    """Grava o dict de produtos no disco, como uma lista ordenada por título."""
    lista_final = sorted(produtos_dict.values(), key=lambda p: p.get("titulo", ""))
    caminho_json.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(lista_final, f, ensure_ascii=False, indent=2)


def sincronizar_produtos(
    caminho_json: Path, produtos_coletados: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Atualiza o arquivo JSON da loja com os produtos recém-coletados.

    Regras:
      - Produto novo (id não existia)      -> adicionado
      - Produto já existia, preço mudou    -> atualizado
      - Produto já existia, preço igual    -> apenas timestamp atualizado (não notifica)
      - Produto que estava no JSON mas NÃO -> removido (saiu de promoção / página
        veio na coleta atual                  fora do ar / link inválido)

    Retorna:
      (produtos_para_notificar, ids_removidos)
      onde produtos_para_notificar são os produtos novos ou com preço alterado
      (só esses devem ser enviados ao Telegram, para evitar spam no canal).
    """
    existentes = _carregar_bruto(caminho_json)
    agora = datetime.now(timezone.utc).isoformat()

    ids_coletados = set()
    produtos_para_notificar: List[Dict[str, Any]] = []

    for produto in produtos_coletados:
        pid = produto["id"]
        ids_coletados.add(pid)
        produto["atualizado_em"] = agora

        antigo = existentes.get(pid)
        if antigo is None:
            produtos_para_notificar.append(produto)
        elif antigo.get("preco") != produto.get("preco"):
            produto["preco_anterior"] = antigo.get("preco")
            produtos_para_notificar.append(produto)

        existentes[pid] = produto

    # Remove do JSON tudo que não veio na coleta atual (saiu de promoção)
    ids_removidos = [pid for pid in list(existentes.keys()) if pid not in ids_coletados]
    for pid in ids_removidos:
        del existentes[pid]

    _salvar_bruto(caminho_json, existentes)

    return produtos_para_notificar, ids_removidos
