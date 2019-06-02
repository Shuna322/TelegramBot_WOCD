import requests
import settings
import  status

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


def registration_enterKey(key, username, chat_id):
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
            if result is not None:
                message = "Введено правильний ключ, обрано групу: '" + result["class"] + "'."
                sql = "UPDATE `users_status` SET `status` = %s, `team_id` = '%s' WHERE `users_status`.`user_name` = %s;"
                cursor.execute(sql, (status.Status.commandName.value, result['id'], username))
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

def registration_commandName(name, username, chat_id):
    import pymysql.cursors
    conn = pymysql.connect(host=settings.database_host,
                           user=settings.database_user,
                           password=settings.database_user_pass,
                           db=settings.database_DB,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM `team_keys` WHERE `reg_key`= %s"
            cursor.execute(sql, key)
            result = cursor.fetchone()
            if result is not None:
                message = "Введено правильний ключ, обрано групу: '" + result["class"] + "'."
                sql = "UPDATE `users_status` SET `status` = %s, `team_id` = '%s' WHERE `users_status`.`user_name` = %s;"
                cursor.execute(sql, (status.Status.commandName.value, result['id'], username))
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