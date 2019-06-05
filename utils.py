import requests
import settings
import status


def send_msg(chat_id, text, button_markup=None):
    url = settings.URL + "sendMessage"
    answer = {'chat_id': chat_id, 'text': text}
    if button_markup is not None:
        import base64
        try:
            answer['reply_markup'] = eval(base64.b64decode(button_markup))
        except:
            print("parse markup error")
    r = requests.post(url, json=answer)
    print(r.json())
    return r.json()

################# Ngrok #################

def setup_and_run_ngrok():
    import os, subprocess
    if os.name == "nt":  #if windows:
        from pathlib import Path
        home = str(Path.home())
        filepath = home + "\\.ngrok2\\ngrok.yml"
        if not os.path.exists(filepath):
            subprocess.Popen(["ngrok.exe", "authtoken", settings.ngrok_token])
        ##############################
        # os.system("taskkill /f /im ngrok.exe")

        # os.popen('taskkill /f /im ngrok.exe')

        subprocess.Popen(["taskkill", "/f", "/im", "ngrok.exe"])
        from time import sleep
        sleep(2)
        subprocess.Popen(["ngrok.exe", "http", "5000"])


def get_ngrok_url():
    import time
    while True:
        try:
            r = requests.get("http://localhost:4040/api/tunnels")
            ngr = r.json()['tunnels'][0]['public_url']
            if ngr[0:5] == "https":
                break
            time.sleep(1)
        except Exception as e:
            print("Didn't got link, trying in 2 seconds\nException: "+e.__doc__)
            time.sleep(2)
    return ngr

################# Webhook #################

def set_webhook_info(ngr_url):
    while True:
        r = requests.post(settings.URL + "setWebhook?url=" + ngr_url + "/bot")
        if r.json()['description'] == "Webhook was set":
            break
        else:
            import time
            time.sleep(2)
    return r.json()


def delete_old_webhook():
    r = requests.post(settings.URL + "deleteWebhook")
    return r.json()

################# Registration #################


def registration_start():
    return 0


def registration_cancel(chat_id):
    import pymysql.cursors
    conn = pymysql.connect(host=settings.database_host,
                           user=settings.database_user,
                           password=settings.database_user_pass,
                           db=settings.database_DB,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM `users_status` WHERE `chat_id` = %s"
            cursor.execute(sql, chat_id)
            result = cursor.fetchone()
            if result is not None:
                user_status_id = result['id']
                if result['team_id'] is not None:
                    user_status_teamid = result['team_id']
                    sql = "SELECT * FROM `team_list` WHERE `class_id` = %s"
                    cursor.execute(sql, user_status_teamid)
                    result2 = cursor.fetchone()
                    team_list_id = result2['id']
                    team_list_id_captain_id = result2['captain_id']
                    if result2['members_id'] is not None:
                        team_list_members_id = str.split(result2['members_id'], ",")
                        for member_id in team_list_members_id:
                            sql = "DELETE FROM `members` WHERE `id` = %s"
                            cursor.execute(sql, member_id)
                            conn.commit()
                    sql = "DELETE FROM `members` WHERE `id` = %s"
                    cursor.execute(sql, team_list_id_captain_id)
                    conn.commit()

                    sql = "DELETE FROM `team_list` WHERE `id` = %s"
                    cursor.execute(sql, team_list_id)
                    conn.commit()

                sql = "DELETE FROM `users_status` WHERE `id` = %s"
                cursor.execute(sql, user_status_id)
                conn.commit()

                message = "Операцію відмінео !"
                send_msg(chat_id=chat_id, text=message)
            else:
                message = "Немає чого відміняти"
                send_msg(chat_id=chat_id, text=message)

    except Exception as e:
        print("Got database error at registration_cancel function\nException: " + e.__doc__)

    finally:
        conn.close()


def registration_enterKey(key, chat_id):
    import pymysql.cursors
    conn = pymysql.connect(host=settings.database_host,
                           user=settings.database_user,
                           password=settings.database_user_pass,
                           db=settings.database_DB,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM `classes` WHERE `reg_key`= %s"
            cursor.execute(sql, key)
            result = cursor.fetchone()
            classid = result["id"]
            class_name = result["class"]
            if result is not None:
                sql = "SELECT * FROM `team_list` WHERE class_id = %s"
                cursor.execute(sql, classid)
                result = cursor.fetchone()
                if result is not None:
                    message = "Вибачте, але данну групу вже зареєтровано, спробуйте ввестиключ ще раз, або натисніть /cancel"
                    send_msg(chat_id=chat_id, text=message)
                else:
                    message = "Введено правильний ключ, обрано групу: '" + class_name + "'."
                    sql = "UPDATE `users_status` SET `status` = %s, `team_id` = '%s' WHERE `users_status`.`chat_id` = %s;"
                    cursor.execute(sql, (status.Status.commandName.value, classid, chat_id))
                    conn.commit()

                    sql = "INSERT INTO `members` VALUES (NULL, NULL, '1', %s, NULL);"
                    cursor.execute(sql, chat_id)
                    conn.commit()

                    sql = "SELECT * FROM `members` WHERE `chat_id`= %s"
                    cursor.execute(sql, chat_id)
                    result = cursor.fetchone()
                    capitanid = result['id']

                    sql = "INSERT INTO `team_list` VALUES (NULL, NULL, %s, %s, NULL);"
                    cursor.execute(sql, (classid, capitanid))
                    conn.commit()

                    send_msg(chat_id=chat_id, text=message)

                    message = "Введіть назву команди:"
                    send_msg(chat_id=chat_id, text=message)

            else:
                message = "Не знайдено команду з даним ключем, спробуйте ще раз."
                send_msg(chat_id=chat_id, text=message)

    except Exception as e:
        print("Got database error at registration_enterKey function\nException: " + e.__doc__)

    finally:
        conn.close()

# def registration_commandName(name, username, chat_id):
#     import pymysql.cursors
#     conn = pymysql.connect(host=settings.database_host,
#                            user=settings.database_user,
#                            password=settings.database_user_pass,
#                            db=settings.database_DB,
#                            charset='utf8mb4',
#                            cursorclass=pymysql.cursors.DictCursor)
#     try:
#         with conn.cursor() as cursor:
#             sql = "SELECT * FROM `team_keys` WHERE `reg_key`= %s"
#             cursor.execute(sql, key)
#             result = cursor.fetchone()
#             if result is not None:
#                 message = "Введено правильний ключ, обрано групу: '" + result["class"] + "'."
#                 sql = "UPDATE `users_status` SET `status` = %s, `team_id` = '%s' WHERE `users_status`.`user_name` = %s;"
#                 cursor.execute(sql, (status.Status.commandName.value, result['id'], username))
#                 conn.commit()
#                 send_msg(chat_id=chat_id, text=message)
#
#                 message = "Введіть назву команди:"
#                 send_msg(chat_id=chat_id, text=message)
#             else:
#                 message = "Не знайдено команду з даним ключем, спробуйте ще раз."
#                 send_msg(chat_id=chat_id, text=message)
#
#     except Exception as e:
#         print("Got database error at registration_enterKey function\nException: " + e.__doc__)
#
#     finally:
#         conn.close()