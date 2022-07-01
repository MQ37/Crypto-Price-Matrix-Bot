import os
import requests
import time
import re
import random
import argparse
import logging
from config import IMPORTANT_COINS, WURL, MROOM, MTOKEN, MSERVER


def send_matrix_msg(msg):
    if "**" not in msg:
        data = {
            "msgtype": "m.text",
            "body": msg,
        }
    else:
        formatted_msg = msg
        for i in range(formatted_msg.count("**")):
            if i % 2 == 0:
                rep = "<strong>"
            else:
                rep = "</strong>"
            formatted_msg = formatted_msg.replace("**", rep, 1)
        formatted_msg = formatted_msg.replace("\n", "<br>")
        data = {
            "msgtype": "m.text",
            "body": msg,
            "format": "org.matrix.custom.html",
            "formatted_body": formatted_msg,
        }

    url = "https://%(MSERVER)s/_matrix/client/r0/rooms/%(MROOM)s/send/m.room.message?access_token=%(MTOKEN)s"
    url = url % {"MSERVER": MSERVER, "MROOM": MROOM, "MTOKEN": MTOKEN}
    r = requests.post(url, json=data)
    r.raise_for_status()


def fetch_text(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
    except:
        return None
    return r.text


def fetch_links(url):
    data = fetch_text(url)
    if not data:
        return None
    links = re.findall("<a href=\"(\/currencies.+?\/)", data)
    return links


def get_sign_change(text):
    match = re.findall(
        "priceValue.*?<span class=\"icon-Caret-(\w+)\"></span>(\d+\.\d+)",
        text)

    if not match:
        return None, None

    sign, change = match[0]
    return sign, change


def gather_change(fh=False, logger=logging):
    if fh:
        links = []
        for i in range(1, 6):
            links += set(fetch_links(f"https://coinmarketcap.com/?page={i}"))
    else:
        wlinks = fetch_links(WURL)
        top100links = fetch_links("https://coinmarketcap.com/")
        links = set(wlinks + top100links)

    if not links:
        logger.error("Couldn't fetch links")
        return

    msgs = []
    for link in links:
        time.sleep(0.3 + random.random() * 0.2)
        url = "https://coinmarketcap.com%s" % link
        page = fetch_text(url)
        if not page:
            logger.error("Failed to fetch text from url %s" % url)
            continue

        coin_name = link.split("/")[2]
        sign, change = get_sign_change(page)

        if not sign:  # or also change
            logger.error("Failed to extract change and sign for  %s" %
                         coin_name)
            continue

        change = float(change)
        if sign.lower() == "down":
            change = -change

        if fh:
            threshold = 20
        else:
            if link in top100links:
                threshold = 5
            else:
                threshold = 10

        logger.debug(f"{coin_name} {change}")

        if abs(change) > threshold:
            # If coin in important highlight
            if coin_name in IMPORTANT_COINS:
                coin_name = "**%s**" % coin_name
            if change < -20:
                msg = f"{coin_name} 24h change -> {change}% 📉 BEARISH"
            elif change < 0:
                msg = f"{coin_name} 24h change -> {change}% 📉"
            elif change > 20:
                msg = f"{coin_name} 24h change -> {change}% 📈 BULLISH"
            else:
                msg = f"{coin_name} 24h change -> {change}% 📈"
            logger.info(msg)
            msgs.append(msg)
    if msgs:
        try:
            send_matrix_msg("\n".join(msgs))
        except:
            logger.error("Failed to send matrix message")
        else:
            logger.info("Matrix message sent")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-v',
                        "--verbose",
                        action="store_true",
                        default=False,
                        help="verbose mode")
    parser.add_argument('-fh',
                        action="store_true",
                        default=False,
                        help="top 500 cryptos")
    args = parser.parse_args()

    logger = logging.getLogger("bot_watcher")
    loglevel = logging.DEBUG if args.verbose else logging.INFO
    logger.setLevel(loglevel)

    logformat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(logformat)

    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(formatter)
    logger.addHandler(streamhandler)

    DIR = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(DIR, "bot_watcher.log")

    filehandler = logging.FileHandler(filepath)
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)

    gather_change(args.fh, logger)
