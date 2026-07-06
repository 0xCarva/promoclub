"""
config.py
---------
Configurações compartilhadas por todos os scripts do PromoClub Brasil.

As credenciais do Telegram NÃO ficam neste arquivo. Elas são lidas a partir
das variáveis de ambiente / Secrets que você já cadastrou no GitHub Actions
(Settings > Secrets and variables > Actions):

    TELEGRAM_TOKEN    -> token do bot (gerado com o @BotFather)
    TELEGRAM_CHAT_ID  -> ID do canal/grupo de destino

Rodando localmente, basta exportar as mesmas variáveis antes de executar:
    export TELEGRAM_TOKEN="seu_token_aqui"
    export TELEGRAM_CHAT_ID="seu_chat_id_aqui"

Se alguma delas não estiver definida, os scripts avisam com um erro claro
em vez de tentar enviar a mensagem com um valor vazio.
"""

import os
from pathlib import Path

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Tag de afiliado da Amazon (identificador público, usado nos links de afiliado)
AMAZON_AFFILIATE_TAG = "carva00-20"

# Configurações gerais do Playwright
HEADLESS = True             # Rodar o navegador sem interface gráfica
PAGE_TIMEOUT_MS = 30_000     # Timeout de carregamento de página (ms)
NAV_WAIT_UNTIL = "domcontentloaded"

# Pasta onde os JSONs de produtos ficam salvos (raiz/produtos)
# Cada script está em raiz/scripts/xxx_scraper.py, então "produtos" é irmã de "scripts"
PRODUTOS_DIR = Path(__file__).resolve().parent.parent.parent / "produtos"
PRODUTOS_DIR.mkdir(parents=True, exist_ok=True)
