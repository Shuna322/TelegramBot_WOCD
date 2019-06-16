from flask import Flask, request, jsonify
import requests
import pymysql.cursors

import settings
import utils
import status


app = Flask(__name__)
app.debug = False


@app.route('/bot', methods=['POST', 'GET'])
def admin_msg_handler():
    if request.method == 'POST':
        r = request.get_json()
        print("Received:")
        print(r)

        if 'message' in r:
            chat_id = r['message']['chat']['id']
        elif 'edited_message' in r:
            chat_id = r['edited_message']['chat']['id']
        # username = r['message']['chat']['username']
        msg_text = None

        result = None

        command_found = False

        conn = pymysql.connect(host=settings.database_host,
                               user=settings.database_user,
                               password=settings.database_user_pass,
                               db=settings.database_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        if 'message' in r:
            if 'text' in r['message']:
                msg_text = r['message']['text']
            if 'contact' in r['message']:
                msg_text = r['message']['contact']['phone_number']
        elif 'edited_message' in r:
            if 'text' in r['edited_message']:
                msg_text = r['edited_message']['text']
            if 'contact' in r['edited_message']:
                msg_text = r['edited_message']['contact']['phone_number']
        if msg_text == "/cancel":
            utils.Registration.registration_cancel(chat_id=chat_id)
        else:
            try:
                with conn.cursor() as cursor:
                    # Read a single record
                    sql = "SELECT * FROM `users_status` WHERE `chat_id` = %s;"
                    cursor.execute(sql, (chat_id,))
                    result = cursor.fetchall()
            except Exception as e:
                print("Got DB ex: " + e.__doc__)
            finally:
                conn.close()

            if len(result) > 0:
                for row in result:
                    status.stagesMap[row['status']](r)
            else:
                if msg_text == "Реєстрація ✏️":
                    utils.Registration.registration_start(chat_id)
                elif msg_text == "Техно квест 🎯":
                    utils.Quest.quest_start(chat_id)
                elif msg_text == "Таблиця рейтингів 🏅":
                    utils.show_rates(chat_id)
                elif msg_text == "Довідка ❓":
                    utils.show_help(chat_id)
                elif msg_text == "Отримати кросворд 🎲":
                    utils.get_crossword(chat_id)
                else:
                    conn = pymysql.connect(host=settings.database_host,
                                           user=settings.database_user,
                                           password=settings.database_user_pass,
                                           db=settings.database_DB,
                                           charset='utf8mb4',
                                           cursorclass=pymysql.cursors.DictCursor)
                    try:
                        with conn.cursor() as cursor:
                            sql = "SELECT * FROM `commands_list`"
                            cursor.execute(sql)
                            result = cursor.fetchall()
                    except Exception as e:
                        print("Got DB ex: " + e.__doc__)
                    finally:
                        conn.close()
                    if result is not None and msg_text is not None:
                        for row in result:
                            if row['command'] in msg_text:
                                utils.send_msg(chat_id, row['respond_text'], row['respond_button_markup'])
                                command_found = True
                                break
                    if not command_found and msg_text != "":
                        message = "Вибачте я вас не розумію.\n" \
                                  "Скористайтеся командою /menu для отримння меню з доступними функціями."
                        utils.send_msg(chat_id, message)

        return jsonify(r)
    else:
        return 'Bot welcomes you !'

@app.route('/admin', methods=['GET'])
def msg_handler():
    if request.method == 'GET':
        action = request.args.get('action')
        token = request.args.get('token')
        if action == "quest_start":
            from threading import Thread

            quest_init = Thread(utils.Quest.quest_init())
            quest_init.start()
            return "{status: 'OK'}"

# https://api.telegram.org/bot819066941:AAHhUC2DlErMP_NLErJ5mfJTWNFgDiy97Sc/setWebhook?url=https://c0eda49f.ngrok.io/bot
# https://c0eda49f.ngrok.io/bot


if __name__ == '__main__':
    if utils.test_internet_conn():
        settings.parse_external_settings()
        # utils.delete_old_webhook()
        # from threading import Thread
        #
        # run_ngrook = Thread(utils.setup_and_run_ngrok())
        # run_ngrook.start()
        #
        # utils.set_webhook_info(utils.get_ngrok_url())
        #
        # from gevent.pywsgi import WSGIServer
        # http_server = WSGIServer(('localhost', 5000), application=app)
        # print("Server is running !")
        # http_server.serve_forever()

        ##############################

        ################
        # Команда для створення сертифікату:
        # bin\openssl req -newkey rsa:2048 -sha256 -nodes -keyout YOURPRIVATE.key -x509 -days 365 -out YOURPUBLIC.pem -subj "/C=US/ST=New York/L=Brooklyn/O=Example Brooklyn Company/CN=109.162.4.106"
        ################

        utils.delete_old_webhook()
        url = settings.URL + "setWebhook"
        answer = {
            'url': "https://109.162.4.106:443/bot"
        }
        files = {'certificate': open("YOURPUBLIC.pem", 'r')}
        r1 = requests.post(url, data=answer, files=files)
        print("Webhook set !")

        from gevent.pywsgi import WSGIServer


        http_server = WSGIServer(('0.0.0.0', 443), application=app, keyfile='YOURPRIVATE.key',
                                 certfile='YOURPUBLIC.pem')
        try:
            print("Server is running !")
            # http_server.serve_forever()

            http_server.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down...")
            from sys import exit

            exit(0)
        except OSError as e:
            print("Can't connect to Internet !")
        except Exception as e:
            print("Got an error:" + e.__doc__)


