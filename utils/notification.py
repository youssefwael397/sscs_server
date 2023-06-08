import telegram
import requests

def send_violence_notification(message):
    TOKEN = "5981970677:AAFvjxBcsVU-GhoWpKSyrzUg2UjJetekr4g"
    user_id = "5936380186"  # @youssef_wael_elsayed - 5936380186
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={user_id}&text={message}"
    print(requests.get(url).json()) # this sends the message