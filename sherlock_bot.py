import threading
import requests
import pandas as pd
from dotenv import load_dotenv
from flask import Flask
from telegram.ext import Updater, CommandHandler
import os
import time
df = pd.read_csv("QandA.csv",encoding='cp1252')
load_dotenv()

purpose="Hi! I’m your study assistant bot. I can help you with PYQs and notes to prepare for Quiz 1. Just type the subject followed by 'notes' or 'pyqs' to get what you need. You can also type 'Sherlock YouTube' to watch the summary sessions."

token = os.getenv("BOT_TOKEN")
base_url = f"https://api.telegram.org/bot{token}"
pyq_links = {
    "statistics":["BQACAgUAAxkBAAMDaGZNSRHblTeGzRdbhlAKvzazTAYAAoAUAAIdtzFX6PvB_ddh1qE2BA",
                  "BQACAgUAAxkBAAMEaGZVcEe4Qgag3yeRVISy9pJvbIsAAooUAAIdtzFXZFT_1MB5DzE2BA"],
     "maths":['BQACAgUAAxkBAAMFaGZWjhb1Q7lLzuI0X6KWc4TDjr4AAo0UAAIdtzFXoa1_8F8xUQU2BA',
              'BQACAgUAAxkBAAMFaGZWjhb1Q7lLzuI0X6KWc4TDjr4AAo0UAAIdtzFXoa1_8F8xUQU2BA'],
    "ct":['BQACAgUAAxkBAAMHaGZXs2ejbFtpcopIP10IFnu-oJEAApEUAAIdtzFXcOLE9S1G6l02BA',
          'BQACAgUAAxkBAAMIaGZX-OYoL0p6vWYputk7KuMvyBYAApMUAAIdtzFXvNlqTyysX5E2BA'],
    "english":['BQACAgUAAxkBAAMJaGZZFa8ZCX9pVOCq3JcrsWzw3PsAApUUAAIdtzFXLuDMc15B12o2BA',
               'BQACAgUAAxkBAAMKaGZZIRzd1rD-6URgS5WJ8eOmAAGBAAKWFAACHbcxV6Fbt_JXxksmNgQ']
}



def read_msg(offset):
  parameters={
    "offset":offset
  }
  res=requests.get(base_url+"/getUpdates",data=parameters)
  data=res.json()

  if not data.get("ok"):
        print("Error from Telegram API:", data.get("description"))
        return offset

  if "result" not in data or len(data["result"]) == 0:
        return offset

  for result in data["result"]:
    message = result.get("message")
    if not message:
            continue

    text = message.get("text")
    if not text:
            continue

    if text.lower()=="sherlock":
      send_msg(purpose,message)
    elif "pyqs" in text.lower():
        parts = text.split()
        if len(parts)==2:
          subject=parts[0].lower()
          if subject in pyq_links:
            get_pyqs(subject,message)
          else:
           send_msg("Please provide the vaild subject like: pyqs subject/maths/ct/english/statistics ",message)
    else:
      answer = find_answer(text)
      send_msg(answer, message)


  if data["result"]:
    return data["result"][-1]["update_id"] + 1

def find_answer(user_question):
    for index, row in df.iterrows():
        if row['question'].lower() == user_question.lower():
            return row['answer']

def send_msg(comment,message):
  message_id=message["message_id"]
  chat_id=message["chat"]["id"]
  parameters={
      "chat_id":chat_id,
      "text":comment,
      "reply_to_message_id":message_id
  }
  res=requests.get(base_url+"/sendMessage",data=parameters)
  data=res.json()


def send_pdf(id_field,message):
    chat_id=message["chat"]["id"]
    parameters = {
        "chat_id":chat_id,
        "document": id_field
    }
    res = requests.post(base_url + "/sendDocument", data=parameters)

def get_pyqs(subject,message):

  if subject in pyq_links:
    for sub in pyq_links[subject]:
      id_field= sub
      send_pdf(id_field,message)
        
def run_bot():
    offset = 0
    while True:
        offset = read_msg(offset)
        time.sleep(1)
 
def run_web():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return "Bot is running"

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
if __name__ == "__main__":
    # Thread 1: Telegram bot
    t1 = threading.Thread(target=run_bot)
    # Thread 2: Dummy web server
    t2 = threading.Thread(target=run_web)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
