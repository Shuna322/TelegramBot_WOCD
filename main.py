import requests
from flask import Flask
from flask import request
from flask import jsonify
import json

token = "819066941:AAHhUC2DlErMP_NLErJ5mfJTWNFgDiy97Sc"

URL = 'https://api.telegram.org/bot819066941:AAHhUC2DlErMP_NLErJ5mfJTWNFgDiy97Sc/'

app = Flask(__name__)


def send_echo_msg(chatID, text):
    url = URL + "sendMessage"
    answer = {'chat_id': chatID, 'text': text}
    r = requests.post(url, json=answer)
    return r.json()


def get_updates():
    url = URL + "getUpdates"
    r = requests.post(url)
    return r.json()


@app.route('/bot', methods=['POST', 'GET'])
def echo():
    if request.method == 'POST':
        r = request.get_json()
        print(r)
        chat_id = r['message']['chat']['id']
        try:
            message = "Ви написали: '"+r['message']['text']+"'"
        except:
            message = "Помилка, не введено символів"
        send_echo_msg(chat_id, message)
        return jsonify(r)
    return 'Bot welcomes you !'


def get_ngrok_url():
    import time
    time.sleep(5)
    r = requests.get("http://localhost:4040/api/tunnels")
    ngr = r.json()['tunnels'][0]['public_url']
    return ngr


def set_webhook_info(String):
    r = requests.post(URL + "setWebhook?url=" + String + "/bot")
    return r.json()


def delete_old_webhook():
    r = requests.post(URL + "deleteWebhook")
    return r.json()

# https://api.telegram.org/bot819066941:AAHhUC2DlErMP_NLErJ5mfJTWNFgDiy97Sc/setWebhook?url=https://c0eda49f.ngrok.io/bot
# https://c0eda49f.ngrok.io/bot


if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    delete_old_webhook()

    import subprocess

    subprocess.Popen(["ngrok.exe", "http", "5000"])

    set_webhook_info(get_ngrok_url())

    app.run()


