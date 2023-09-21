import os
import schedule
import time
import pickle
from bs4 import BeautifulSoup
import requests
import telebot

TELEGRAM_BOT_TOKEN = '6667481530:AAGwxgETMSIJsjy_HLyWMJBSKqSQ_X8dY8Y'
CHAT_ID = '630860614'
SENT_ADS_FILE = os.path.abspath("sent_ads.pkl")

def save_sent_ads(sent_ads):
    with open(SENT_ADS_FILE, "wb") as file:
        pickle.dump(sent_ads, file)

def load_sent_ads():
    try:
        with open(SENT_ADS_FILE, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return set()

sent_ads = load_sent_ads()

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def parse_website():
    url = "https://www.ss.com/ru/real-estate/flats/riga/all/hand_over/"
    page_source = requests.get(url)
    soup = BeautifulSoup(page_source.text, 'html.parser')
    tables = soup.find_all("table")
    new_ads = []

    keywords = ["центр", "Кливерсала", "Торнякалнс", "Агенскалнс"] #Choose your area
    max_price = 400 #choose your price

    if tables:
        for table in tables:
            rows = table.find_all("tr")
            for tag_tr in rows:
                tag_id = tag_tr.get("id", "")
                if tag_id.startswith("tr_5") and tag_id not in sent_ads:
                    tag_td = tag_tr.find_all('td')
                    price_text = tag_td[8].text.strip().replace(',', "")
                    price = float(price_text.split()[0]) if price_text else 0
                    place = tag_td[3].text.strip()
                    square = tag_td[5].text.strip()
                    link = tag_tr.find('a', {'class': 'am'})['href']

                    if any(keyword in place for keyword in keywords) and price <= max_price:
                        sent_ads.add(tag_id)
                        ad_info = f"\nРайон: {place}, \nЦена: {price} €, \nКвадратура: {square}, \nСсылка:https://www.ss.com{link}"
                        new_ads.append(ad_info)

    return new_ads

def send_telegram_message(text):
    try:
        bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в Telegram: {str(e)}")

def main():
    while True:
        new_ads = parse_website()
        new_ads_to_send = []

        for ad in new_ads:
            if ad not in sent_ads:
                send_telegram_message(ad)
                sent_ads.add(ad)
                new_ads_to_send.append(ad)

        save_sent_ads(sent_ads)

        schedule.run_pending()
        time.sleep(180)

if __name__ == "__main__":
    main()