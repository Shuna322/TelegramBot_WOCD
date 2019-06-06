from flask import Flask, request, jsonify
import requests
import json
import pymysql.cursors

import settings
import utils
import status

app = Flask(__name__)
app.debug = True


@app.route('/bot', methods=['POST', 'GET'])
def msg_handler():
    if request.method == 'POST':
        r = request.get_json()
        print("Received:")
        print(r)

        chat_id = r['message']['chat']['id']
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
        if 'text' in r['message']:
            msg_text = r['message']['text']
        if 'contact' in r['message']:
            msg_text = r['message']['contact']['phone_number']
        if msg_text == "/cancel":
            utils.registration_cancel(chat_id=chat_id)
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
                try:
                    msg_text = r['message']['text']
                except Exception as e:
                    print("Couldn't find text in msg, probably msg without text was send \nException: " + e.__doc__)
                    message = "Ви відправили повідомлення без тексту.\n" + \
                              "Скористайтеся командою /menu для отримння меню з доступними функціями."
                    utils.send_msg(chat_id, message)
                if msg_text == "/register":
                    conn = pymysql.connect(host=settings.database_host,
                                           user=settings.database_user,
                                           password=settings.database_user_pass,
                                           db=settings.database_DB,
                                           charset='utf8mb4',
                                           cursorclass=pymysql.cursors.DictCursor)
                    try:
                        with conn.cursor() as cursor:
                            sql = "INSERT INTO `users_status` (`id`, `chat_id`, `status`, `team_id`) VALUES (NULL, %s, %s, NULL);"
                            cursor.execute(sql, (chat_id, status.Status.keyEnter.value))
                            conn.commit()
                            message = "Розпочато реєстрацю, введіть персональний ключ"
                            utils.send_msg(chat_id, message)
                    except Exception as e:
                        print("Got DB ex: " + e.__doc__)
                        message = "Сталася помилка при роботі з базою данних"
                        utils.send_msg(chat_id, message)
                    finally:
                        conn.close()
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


# https://api.telegram.org/bot819066941:AAHhUC2DlErMP_NLErJ5mfJTWNFgDiy97Sc/setWebhook?url=https://c0eda49f.ngrok.io/bot
# https://c0eda49f.ngrok.io/bot


if __name__ == '__main__':
    utils.delete_old_webhook()
    from threading import Thread

    run_ngrook = Thread(utils.setup_and_run_ngrok())
    run_ngrook.start()

    utils.set_webhook_info(utils.get_ngrok_url())

    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('localhost', 5000), application=app)
    print("Server is running !")
    http_server.serve_forever()

    ##############################

    ################
    # Команда для створення сертифікату:
    # bin\openssl req -newkey rsa:2048 -sha256 -nodes -keyout YOURPRIVATE.key -x509 -days 365 -out YOURPUBLIC.pem -subj "/C=US/ST=New York/L=Brooklyn/O=Example Brooklyn Company/CN=109.162.4.106"
    ################

    # utils.delete_old_webhook()
    # url = settings.URL + "setWebhook"
    # answer = {
    #     'url': "https://109.162.4.106:443/bot"
    # }
    # files = {'certificate': open("openssl/YOURPUBLIC.pem", 'r')}
    # r1 = requests.post(url, data=answer, files=files)
    # print("Webhook set !")
    #
    # from gevent.pywsgi import WSGIServer
    #
    # http_server = WSGIServer(('0.0.0.0', 443), application=app, keyfile='openssl/YOURPRIVATE.key', certfile='openssl/YOURPUBLIC.pem')
    # print("Server is running !")
    # http_server.serve_forever()
