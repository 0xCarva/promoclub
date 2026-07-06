# PromoClub Brasil — Scripts de monitoramento

Estrutura esperada no repositório (GitHub Pages):

```
raiz-do-repo/
├── scripts/
│   ├── common/
│   │   ├── config.py          <- credenciais do Telegram aqui
│   │   ├── json_utils.py
│   │   └── telegram_utils.py
│   ├── amazon_scraper.py
│   ├── shopee_scraper.py
│   ├── meli_scraper.py
│   └── requirements.txt
└── produtos/
    ├── produtos_amazon.json   <- gerado/atualizado automaticamente
    ├── produtos_shopee.json   <- gerado/atualizado automaticamente
    └── produtos_meli.json     <- gerado/atualizado automaticamente
```

## 1) Instalação

```bash
cd scripts
pip install -r requirements.txt
playwright install chromium
```

## 2) Configurar credenciais

Edite `scripts/common/config.py` e preencha:

- `TELEGRAM_BOT_TOKEN`: token gerado pelo @BotFather no Telegram.
- `TELEGRAM_CHAT_ID`: ID do canal/grupo (para canais, geralmente começa com `-100`).

Ou, se preferir (recomendado para não expor o token no GitHub), defina como
variáveis de ambiente com o mesmo nome antes de rodar os scripts.

## 3) Adicionar produtos para monitorar

Em cada script (`amazon_scraper.py`, `shopee_scraper.py`, `meli_scraper.py`),
edite a lista `PRODUCT_URLS` no topo do arquivo, colando os links dos produtos
que você quer acompanhar.

## 4) Rodar

```bash
python amazon_scraper.py
python shopee_scraper.py
python meli_scraper.py
```

Cada execução:
1. Coleta os dados atuais das páginas listadas em `PRODUCT_URLS`.
2. Atualiza o JSON da loja (`produtos/produtos_<loja>.json`): adiciona
   produtos novos, atualiza os que mudaram de preço e **remove** os que não
   vieram mais na coleta (ou seja, saíram da lista de promoções).
3. Só então envia ao Telegram os produtos que são **novos** ou que tiveram
   **mudança de preço** (produtos sem alteração não gera nova mensagem, para
   não floodar o canal).

## 5) Automatizar (opcional)

Para rodar periodicamente, você pode usar um cron job no seu servidor ou um
workflow do GitHub Actions agendado (`schedule` com `cron`), lembrando de
cadastrar `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` como *Secrets* do
repositório nesse caso.

## Observações importantes

- Sites de e-commerce mudam o layout das páginas com frequência e podem ter
  proteções anti-bot. Os seletores usados aqui são os atuais no momento da
  criação do script; se a extração parar de funcionar, normalmente basta
  ajustar os seletores CSS no topo de cada arquivo.
- Respeite os Termos de Uso de cada plataforma e adicione atrasos entre
  requisições (já incluído no envio ao Telegram) para não sobrecarregar os
  servidores nem levar bloqueio de IP.
