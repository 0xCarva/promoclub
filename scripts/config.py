"""
config.py
---------
Configurações compartilhadas por todos os scripts do PromoClub Brasil.

>>> INSIRA SUAS CREDENCIAIS AQUI <<<

Existem duas formas de configurar o Bot do Telegram:

1) (Mais simples) Preencha diretamente as strings abaixo:
       TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
       TELEGRAM_CHAT_ID   = "-1001234567890"

2) (Mais seguro, recomendado em produção/GitHub Actions) Defina variáveis de
   ambiente com o mesmo nome, e o código abaixo vai usá-las automaticamente,
   sem precisar editar este arquivo nem expor o token no repositório público:
       export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
       export TELEGRAM_CHAT_ID="-1001234567890"

   Como o GitHub Pages é público, a opção 2 é fortemente recomendada para não
   vazar o token do bot no histórico do repositório. Se for rodar via GitHub
   Actions, cadastre esses valores em Settings > Secrets and variables > Actions.
"""

import os

# ⚠️ TOKEN DO BOT DO TELEGRAM (fale com o @BotFather para gerar o seu)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "COLOQUE_SEU_TOKEN_AQUI")

# ⚠️ CHAT ID do canal/grupo do Telegram para onde as promoções serão enviadas
# (para canais costuma começar com -100...). Você pode descobrir o chat_id
# adicionando o bot @getidsbot ao canal, ou chamando a API getUpdates.
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "COLOQUE_SEU_CHAT_ID_AQUI")

# Tag de afiliado da Amazon
AMAZON_AFFILIATE_TAG = "carva00-20"

# Configurações gerais do Playwright
HEADLESS = True            # Rodar o navegador sem interface gráfica
PAGE_TIMEOUT_MS = 30_000    # Timeout de carregamento de página (ms)
NAV_WAIT_UNTIL = "domcontentloaded"

# Pasta onde os JSONs de produtos ficam salvos (raiz/produtos)
# Cada script está em raiz/scripts/xxx_scraper.py, então "produtos" é irmã de "scripts"
from pathlib import Path
PRODUTOS_DIR = Path(__file__).resolve().parent.parent.parent / "produtos"
PRODUTOS_DIR.mkdir(parents=True, exist_ok=True)
