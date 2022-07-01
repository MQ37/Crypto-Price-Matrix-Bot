# Crypto Price Matrix Bot
Simple crypto price alert bot for Matrix in Python

### How bot works
Bot checks 24h percentage change on coinmarketcap.com and sends alert to your Matrix

### How to install
- Using pip install `requests` python library
   - `pip install requests`
- Configure bot
   
### Configuration
Configuration is stored in `config.py` file
- Set `WURL` to your public coinmarketcap watchlist
- Set `MROOM` to your Matrix room ID (replace `!` with `%21`)
- Set `MTOKEN` to your Matrix access token
- Add favorite coins that will be highlighted to `IMPORTANT_COINS` list (coinmarketcap coin name from URL)

### How to run
- Run `main.py`
   - `python3 main.py`

### Arguments
- `-v`, `--verbose` - verbose mode
- `-fh` - uses top 500 coins on coinmarketcap insted of your public coinmarketcap watchlist (`WURL`)
