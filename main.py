from flask import Flask, request, jsonify
import requests
import json
import pymysql.cursors

import settings
import utils
import status

app = Flask(__name__)


@app.route('/bot', methods=['POST', 'GET'])
def msg_handler():
    if request.method == 'POST':
        r = request.get_json()
        print("Received:")
        print(r)

        chat_id = r['message']['chat']['id']
        username = r['message']['chat']['username']
        msg_text = ""

        result = None

        command_found = False

        conn = pymysql.connect(host=settings.database_host,
                               user=settings.database_user,
                               password=settings.database_user_pass,
                               db=settings.database_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        try:
            with conn.cursor() as cursor:
                # Read a single record
                sql = "SELECT * FROM `users_status` WHERE `user_name` = %s;"
                cursor.execute(sql, (username,))
                result = cursor.fetchall()
        except Exception as e:
            print("Got DB ex: " + e.__doc__)
        finally:
            conn.close()

        if len(result) > 0:
            for row in result:
                if row['status'] == status.Status.keyEnter.value:

                    ############# TO-DO #############
                    # Probably better to do universal parser for every status
                    try:
                        msg_text = r['message']['text']
                        utils.registration_enterKey(key=msg_text, username=username, chat_id=chat_id)
                    except Exception as e:
                        print("Couldn't find msg text, suggesting verify input \nException: " + e.__doc__)
                        message = status.statusErrorMsg[status.Status.keyEnter]
                        utils.send_msg(chat_id, message)
                    ############# ^TO-DO^ #############
                    if row['status'] == status.Status.commandName.value:

                        ############# TO-DO #############
                        # Probably better to do universal parser for every status
                        try:
                            msg_text = r['message']['text']
                            utils.registration_enterKey(key=msg_text, username=username, chat_id=chat_id)
                        except Exception as e:
                            print("Couldn't find msg text, suggesting verify input \nException: " + e.__doc__)
                            message = status.statusErrorMsg[status.Status.keyEnter]
                            utils.send_msg(chat_id, message)
                        ############# ^TO-DO^ #############
        else:
            try:
                msg_text = r['message']['text']
            except Exception as e:
                print("Couldn't find text in msg, probably msg without text was send \nException: " + e.__doc__)
                message = "Ви прислали повідомлення без тексту.\n" + \
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
                        sql = "INSERT INTO `users_status` (`id`, `user_name`, `status`, `team_id`) VALUES (NULL, %s, %s, NULL);"
                        cursor.execute(sql, (username, status.Status.keyEnter.value))
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

                for row in result:
                    if row['command'] in msg_text:
                        utils.send_msg(chat_id, row['respond_text'], row['respond_button_markup'])
                        command_found = True
                        break
                if not command_found and msg_text != "":
                    message = "Ви написали: '" + msg_text + "'"
                    utils.send_msg(chat_id, message)

        return jsonify(r)
    else:
        return 'Bot welcomes you !'


# https://api.telegram.org/bot819066941:AAHhUC2DlErMP_NLErJ5mfJTWNFgDiy97Sc/setWebhook?url=https://c0eda49f.ngrok.io/bot
# https://c0eda49f.ngrok.io/bot


if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    utils.delete_old_webhook()

    from threading import Thread

    run_ngrook = Thread(utils.setup_and_run_ngrok())
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
