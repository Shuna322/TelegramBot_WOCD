from flask import Flask, request, jsonify
import requests
import json
import pymysql.cursors

import settings
import utils

app = Flask(__name__)


def send_msg(chat_id, text, button_markup=None):
    url = settings.URL + "sendMessage"
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


@app.route('/bot', methods=['POST', 'GET'])
def msg_handler():
    if request.method == 'POST':
        r = request.get_json()
        print(r)
        chat_id = r['message']['chat']['id']
        command_found = False

        conn = pymysql.connect(host=settings.database_host,
                               user=settings.database_user,
                               password=settings.database_user_pass,
                               db=settings.database_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)

        try:
            msg_text = r['message']['text']

            # NEW ##### #######################
            try:
                with conn.cursor() as cursor:
                    # Read a single record
                    sql = "SELECT * FROM `users_status` WHERE `user_name` = '" + r['message']['chat']['username'] + "';"
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    if len(result) > 0:
                        for row in result:
                            if row['state'] == 1:
                                sql = "DELETE FROM `users_status` WHERE `users_status`.`user_name` = '" \
                                      + r['message']['chat']['username'] + "';"
                                cursor.execute(sql)
                                conn.commit()
                                message = "Ви ввели `" + r['message']['text'] + "` і завершили реєстрацію"
                                send_msg(chat_id, message)
                    else:
                        if msg_text == "/register":
                            sql = "INSERT INTO `users_status` (`id`, `user_name`, `state`) VALUES (NULL, '" \
                                  + r['message']['chat']['username'] + "', '1');"
                            cursor.execute(sql)
                            conn.commit()
                            message = "Розпочато реєстрацю, введіть Прізвище та ініціали"
                            send_msg(chat_id, message)
                        else:
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


        except Exception as e:
            message = "Помилка, не введено символів"
            send_msg(chat_id, message)
        return jsonify(r)
    else:
        return 'Bot welcomes you !'

# https://api.telegram.org/bot819066941:AAHhUC2DlErMP_NLErJ5mfJTWNFgDiy97Sc/setWebhook?url=https://c0eda49f.ngrok.io/bot
# https://c0eda49f.ngrok.io/bot


if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    utils.delete_old_webhook()

    from threading import Thread
    run_ngrook = Thread(utils.setup_and_run_ngrook())
    run_ngrook.start()

    utils.set_webhook_info(utils.get_ngrok_url())

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

