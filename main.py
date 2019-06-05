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
        try:
            msg_text = r['message']['text']
        except Exception as e:
            print("Couldn't find text in msg, probably msg without text was send \nException: " + e.__doc__)
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

                    for row in result:
                        if row['command'] in msg_text:
                            utils.send_msg(chat_id, row['respond_text'], row['respond_button_markup'])
                            command_found = True
                            break
                    if not command_found and msg_text != "":
                        message = "ВИбачте я вас не розумію.\n" \
                                  "Скористайтеся командою /menu для отримння меню з доступними функціями."
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
