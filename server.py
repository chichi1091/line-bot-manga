import datetime
import os
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
import urllib2
from bs4 import BeautifulSoup

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

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
        
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message))


def scraping(url):
    html = urllib2.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string

    div_tag = soup.find(id="ctl00_ContentPlaceHolder1_thisnumber")
    for tag in div_tag:
        clazz = tag.get("class").pop(0)
        if clazz == "limit":
            string_ = tag.string
            term = string_.split(":")[1].split("－")
            start = datetime.datetime.strptime(term[0], '%Y.%m.%d')
            
            if datetime.Now <= start:
                return title
    
    return None


if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
