import datetime
import os
import requests
import json
import urllib.request, urllib.error
from flask import Flask, request, abort, jsonify
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from bs4 import BeautifulSoup
from celery.task import periodic_task
from celery.schedules import crontab

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
YOUR_USER_ID = os.environ["YOUR_USER_ID"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

url_list = [
    "https://over-lap.co.jp/Form/Product/ProductDetail.aspx?shop=0&pid=ZG0003&vid=&cat=CGS&swrd="
    , "https://over-lap.co.jp/Form/Product/ProductDetail.aspx?shop=0&pid=ZG0022&vid=&cat=CGS&swrd="
]


@app.route('/callback', methods=['POST'])
def callback():
    print("callback start")
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        print("InvalidSignatureError message:{0}".format(e.message))
        abort(400)
    except LineBotApiError as e:
        print("LineBotApiError message:{0}".format(e.message))
        abort(400)

    resp = jsonify(success=True)
    return resp


@handler.default()
def default(event):
    print(event)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='サポートされていないテキストメッセージです')
    )


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = create_message()
        
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message))


@periodic_task(run_every=crontab(minute="0", hour="0"))
def task():
    message = create_message()

    post_date = {
        "to": YOUR_USER_ID
        , "message": {
            "type": "text"
            , "text": message
        }
    }
    headers = {
        "Content-Type" : "application/json; charset=UTF-8"
        , "Authorization": "Bearer " + YOUR_CHANNEL_ACCESS_TOKEN
    }
    requests.post("https://api.line.me/v2/bot/message/push", data=json.dumps(post_date), headers=headers)


def create_message():
    titles = ""
    for url in url_list:
        title = scraping(url)
        if title is not None:
            if titles != "": titles += ","
            titles += title.replace("｜コミックガルド作品一覧", "")

    message = ""
    if titles == "":
        message = "更新はありません"
    else:
        message += titles + "が更新されています"
    return message


def scraping(url):
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string

    div_tag = soup.find(id="ctl00_ContentPlaceHolder1_thisnumber")
    inner_div_tag = div_tag.find_all("div")
    string_ = inner_div_tag[1].string
    term = string_.replace("掲載期間：", "").replace("\r\n", "").split("－")
    start = datetime.datetime.strptime(term[0], '%Y.%m.%d')
    
    if datetime.datetime.now() <= start:
        return title
    
    return None


if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)

