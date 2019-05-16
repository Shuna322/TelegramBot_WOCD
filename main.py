from flask import Flask, request, jsonify
import requests
import json
import pymysql.cursors

token = "819066941:AAHhUC2DlErMP_NLErJ5mfJTWNFgDiy97Sc"

URL = 'https://api.telegram.org/bot819066941:AAHhUC2DlErMP_NLErJ5mfJTWNFgDiy97Sc/'

ngrok_token = "2YKzZQs5HbksqP1AkRZaN_3TwdEn6CwZLzED16HeqMs"

app = Flask(__name__)


def send_msg(chat_id, text, button_markup = None):
    url = URL + "sendMessage"
    answer = {'chat_id': chat_id, 'text': text}
    if button_markup is not None:
        import base64
        try:
            answer['reply_markup'] = eval(base64.b64decode(button_markup))
        except:
            print("parse error")
    r = requests.post(url, json=answer)
    print(r.json())
    return r.json()


def get_updates():
    url = URL + "getUpdates"
    r = requests.post(url)
    return r.json()


def send_menu(chat_id):
    url = URL + "sendMessage"
    buttons = {'inline_keyboard': [
        # row 1
        [{'text': 'Button 1 🥳', 'url': 'https://google.com/'}, {'text': 'Button 2 👽', 'url': 'https://youtube.com/'}],
        # row 2
        [{'text': 'Button 3 👾', 'url': 'https://gmail.com/'}]
    ]
    }
    answer = {'chat_id': chat_id, 'text': "Ось ваше меню:", 'reply_markup': buttons}
    r = requests.post(url, json=answer)
    print(r.json())
    return r.json()


@app.route('/bot', methods=['POST', 'GET'])
def msg_handler():
    if request.method == 'POST':
        r = request.get_json()
        print(r)
        chat_id = r['message']['chat']['id']
        command_found = False

        conn = pymysql.connect(host='51.254.175.184',
                               user='wocd_dev_user',
                               password='2E3i9T5i',
                               db='wocd_dev_db',
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)

        try:
            msg_text = r['message']['text']
            try:
                with conn.cursor() as cursor:
                    # Read a single record
                    sql = "SELECT * FROM `commands_list`"
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for row in result:
                        if row['command'] in msg_text:
                            send_msg(chat_id, row['respond_text'], row['respond_button_markup'])
                            command_found = True
                            break
                    if not command_found:
                        message = "Ви написали: '" + r['message']['text'] + "'"
                        send_msg(chat_id, message)
            except Exception as e:
                print("Got DB ex: " + e)
            finally:
                conn.close()

            # msg_text = r['message']['text']
            # if "/menu" in msg_text:
            #     send_menu(chat_id)
            # else:
            #     message = "Ви написали: '"+r['message']['text']+"'"
            #     send_msg(chat_id, message)

        except Exception as e:
            message = "Помилка, не введено символів"
            send_msg(chat_id, message)
        return jsonify(r)
    else:
        return 'Bot welcomes you !'


def get_ngrok_url():
    import time
    time.sleep(10)
    r = requests.get("http://localhost:4040/api/tunnels")
    ngr = r.json()['tunnels'][0]['public_url']
    return ngr


def set_webhook_info(ngr_url):
    r = requests.post(URL + "setWebhook?url=" + ngr_url + "/bot")
    return r.json()


def delete_old_webhook():
    r = requests.post(URL + "deleteWebhook")
    return r.json()

# https://api.telegram.org/bot819066941:AAHhUC2DlErMP_NLErJ5mfJTWNFgDiy97Sc/setWebhook?url=https://c0eda49f.ngrok.io/bot
# https://c0eda49f.ngrok.io/bot


if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    delete_old_webhook()
    import os, subprocess
    if os.name == "nt":
        from pathlib import Path
        home = str(Path.home())
        filepath = home + "\\.ngrok2\\ngrok.yml"
        if not os.path.exists(filepath):
            subprocess.Popen(["ngrok.exe", "authtoken", ngrok_token])
        ##############################

        subprocess.Popen(["ngrok.exe", "http", "5000"])

    set_webhook_info(get_ngrok_url())

    app.run()

    # try:
    #     with conn.cursor() as cursor:
    #         # Read a single record
    #         sql = "SELECT * FROM `commands_list`"
    #         cursor.execute(sql)
    #         result = cursor.fetchall()
    #         print(result)
    # finally:
    #     conn.close()
    #

