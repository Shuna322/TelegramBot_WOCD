import requests
import settings


def test_internet_conn():
    url = 'http://www.google.com/'
    timeout = 5
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("Internet connection can't be established.")
    return False


def send_msg(chat_id, text, button_markup=None, parse_mode=None):
    url = settings.URL + "sendMessage"
    answer = {'chat_id': chat_id, 'text': text}
    if button_markup is not None:
        import base64
        try:
            answer['reply_markup'] = eval(base64.b64decode(button_markup))
        except:
            try:
                answer['reply_markup'] = button_markup
            except:
                pass
    if parse_mode is not None:
        answer['parse_mode'] = parse_mode
    r = requests.post(url, json=answer)
    print("Send:")
    print(r.json())
    return r.json()


def download_image_from_telegram(r):
    file_id = r['message']['photo'][-1]['file_id']
    url = settings.URL + "getFile"
    answer = {'file_id': file_id}
    r = requests.post(url, json=answer)
    file_path = r.json()['result']['file_path']

    r = requests.get('https://api.telegram.org/file/bot' + settings.token + '/' + file_path, stream=True)

    pic_path = 'downloaded_pictures/' + file_id + '.jpg'

    with open(pic_path, 'wb') as f:
        f.write(r.content)
    return pic_path


def scan_qr_code(pic_path):
    from pyzbar.pyzbar import decode
    from PIL import Image
    import os
    result = decode(Image.open(pic_path))
    os.remove(pic_path)
    if len(result) > 0:
        data = result[0].data
        return data
    else:
        return None

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
        FNULL = open(os.devnull, 'w')

        subprocess.Popen(["taskkill", "/f", "/im", "ngrok.exe"], stdout=FNULL, stderr=subprocess.STDOUT)
        from time import sleep
        sleep(2)
        subprocess.Popen(["ngrok.exe", "http", "5000"])
        print("Ngrok started !")


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
    print("Got ngrok new link: " + ngr)
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
    print("New link was set !")
    return r.json()


def delete_old_webhook():
    r = requests.post(settings.URL + "deleteWebhook")
    print("Old webhook deleted !")
    return r.json()

def show_rates(chat_id):
    import pymysql.cursors
    conn = pymysql.connect(host=settings.database_host,
                           user=settings.database_user,
                           password=settings.database_user_pass,
                           db=settings.database_DB,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

    try:
        with conn.cursor() as cursor:

            sql = "SELECT * FROM `team_list` WHERE `name` IS NOT NULL AND `score` IS NOT NULL ORDER BY `score` DESC"
            cursor.execute(sql)
            result = cursor.fetchall()

            if len(result) > 0:
                message = "Ось вам таблиця результатів:\n" \
                          "<b>Назва команди - Кількість балів</b>\n"
                for row in result:
                    message = message + row['name'] + " - " + row['score'] + "\n"
            else:
                message = "Таблиця команд на данний момент - порожня."

            send_msg(chat_id=chat_id, text=message, parse_mode="HTML")

    except Exception as e:
        print("Got database error at registration_enterKey function\nException: " + e.__doc__)

    finally:
        conn.close()

def show_help(chat_id):
    message = 'Цей бот призначений для проведення тижня комп`ютерних дисциплін у <a href="http://tk.te.ua/">ТкТНТУ імені Івана Пулюя</a>\n\n' \
              'Ви можете спостерігати за результатами конкорсу, а також отримати для розв`язування технічний кросворд\n' \
              'Якщо ви хочете взяти участь, то вам необхідно зареєструватись використовуючи відповідну кнопку, ' \
              'для цього вам також необхідно мати персональний ключ реєстрації який повинен видати вам організатор.\n' \
              'Він буде представлений у вигляді <a href="https://uk.wikipedia.org/wiki/QR-%D0%BA%D0%BE%D0%B4">QR коду</a>' \
              ' який ви можете просто сфотографувати та надіслати боту, на його вимогу. Якщо бот не може розпізнати код ' \
              'після декількох спроб, спробуйте відсканувати його використовуючи сторонній додаток, на надішліть отриманий ' \
              'текст боту.\n\n' \
              'Якщо ви не знайшли потрібної інформації або у вас виникли запитання, будь ласка, зверніться до класного керівника.'
    send_msg(chat_id=chat_id, text=message, parse_mode="HTML")

def get_crossword(chat_id):
    import pymysql.cursors
    conn = pymysql.connect(host=settings.database_host,
                           user=settings.database_user,
                           password=settings.database_user_pass,
                           db=settings.database_DB,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

    try:
        with conn.cursor() as cursor:

            sql = "SELECT `value` FROM `settings` WHERE `attribute` = 'crossword_link'"
            cursor.execute(sql)
            result = cursor.fetchone()

            if result is not None and result['value'] is not None:
                photo_link = result['value']
                message = "Ось вам кросворд, розв'яжіть та віддайте його класному керівнику."
                send_msg(chat_id=chat_id, text=message)

                url = settings.URL + "sendPhoto"
                answer = {'chat_id': chat_id, 'photo': photo_link}
                r = requests.post(url, json=answer)
            else:
                message = "Кросворду немає, спробуйте пізніше."
                send_msg(chat_id=chat_id, text=message)

    except Exception as e:
        print("Got database error at registration_enterKey function\nException: " + e.__doc__)

    finally:
        conn.close()


class Quest:
    @staticmethod
    def quest_init():
        import pymysql.cursors
        conn = pymysql.connect(host=settings.database_host,
                               user=settings.database_user,
                               password=settings.database_user_pass,
                               db=settings.database_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE `settings` SET `value` = 1 WHERE `attribute` = 'quest_is_online';"
                cursor.execute(sql)
                conn.commit()

                sql = "SELECT * FROM `members` WHERE `is_capitan` = 1"
                cursor.execute(sql)
                result = cursor.fetchall()
                captain_ids = []
                for row in result:
                    captain_ids.append({
                        1: row['id'],
                        2: row['chat_id']
                    })

                sql = "SELECT * FROM `quest_rooms`"
                cursor.execute(sql)
                result = cursor.fetchall()
                quest_rooms = []
                for row in result:
                    quest_rooms.append({
                        1: row['id'],
                        2: row['puzzle'],
                    })

                counter = 0

                for id in captain_ids:
                    sql = "UPDATE `team_list` SET `team_list`.`current_quest_room` = %s WHERE `team_list`.`captain_id` = %s"
                    cursor.execute(sql, (quest_rooms[counter][1], id[1]))
                    conn.commit()

                    sql = "SELECT * FROM `quest_rooms` WHERE `id` = %s"
                    cursor.execute(sql, quest_rooms[counter][1])
                    result = cursor.fetchone()

                    sql = "UPDATE `quest_rooms` SET `teams_on_this_room` = %s WHERE `quest_rooms`.`id` = %s;"
                    cursor.execute(sql, (int(result['teams_on_this_room']) + 1, quest_rooms[counter][1]))
                    conn.commit()

                    message = "Увага учасники - квест розпочато !\nЯкщо ви не знаєте правил, натисніть на кнопку довідки.\nДля вашої команди перша підсказка буде такою: '"+quest_rooms[counter][2]+"'"
                    send_msg(id[2], message)
                    counter = counter + 1
                    if counter == len(quest_rooms):
                        counter = 0

                from gevent import sleep
                # sleep(7200)
                sleep(60*5)
                sql = "UPDATE `settings` SET `value` = 0 WHERE `attribute` = 'quest_is_online';"
                cursor.execute(sql)
                conn.commit()

                for id in captain_ids:
                    message = "Увага учасники - квест завершено !\nРезультати можна переглянути у рейтинговій таблиці."
                    send_msg(id[2], message)

        finally:
            conn.close()

    @staticmethod
    def quest_start(chat_id):
        import pymysql.cursors
        import status
        conn = pymysql.connect(host=settings.database_host,
                               user=settings.database_user,
                               password=settings.database_user_pass,
                               db=settings.database_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM `settings` WHERE `attribute` = 'quest_is_online'"
                cursor.execute(sql)
                result = cursor.fetchone()
                if result['value'] == '1':

                    sql = "SELECT * FROM `quest_rooms`"
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    num_of_rooms = len(result)

                    sql = "SELECT * FROM `members`, `team_list`, `quest_rooms` WHERE `is_capitan` = '1' AND `chat_id` = %s AND `members`.`id` = `captain_id` AND `current_quest_room` = `quest_rooms`.`id`"
                    cursor.execute(sql, chat_id)
                    result = cursor.fetchone()
                    if result is not None:
                        if result['visited_quest_rooms'] is not None:
                            array_visited_quest_rooms = result['visited_quest_rooms'].split(',')
                            if len(array_visited_quest_rooms) == num_of_rooms and array_visited_quest_rooms[-1] != '':
                                message = "Ви уже побували в усіх кімнатах !"
                                send_msg(chat_id=chat_id, text=message)
                                return

                        puzzle = result['puzzle']

                        message = "Нагадую, ваша загадка звучить так: '"+puzzle+"'\n\nНадішліть мені фотографію з оцінкою, отриманою у викладача:"

                        sql = "INSERT INTO `users_status` (`id`, `chat_id`, `status`, `team_id`) VALUES (NULL, %s, %s, NULL);"
                        cursor.execute(sql, (chat_id, status.Status.quest_keyEnter.value))
                        conn.commit()

                        back_to_main_menu_keyboard = {
                            'keyboard': [
                                [{
                                    'text': 'Повернутися до головного меню ⬅️'
                                }]
                            ],
                            'resize_keyboard': True,
                            'one_time_keyboard': True
                        }

                        send_msg(chat_id=chat_id, text=message, button_markup=back_to_main_menu_keyboard)
                    else:
                        message = "Ви не є капітаном жодної із команд. Усіх капітанів буде сповіщено про початок квесту !"
                        send_msg(chat_id=chat_id, text=message)
                else:
                    message = "Квест ще не початий. Усіх капітанів буде сповіщено про початок квесту !"
                    send_msg(chat_id=chat_id, text=message)

        finally:
            conn.close()

    @staticmethod
    def quest_keyEnter(r):
        import status
        import pymysql.cursors
        conn = pymysql.connect(host=settings.database_host,
                               user=settings.database_user,
                               password=settings.database_user_pass,
                               db=settings.database_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        chat_id = r['message']['chat']['id']
        code = None
        if 'text' in r['message']:
            code = r['message']['text']
        elif 'photo' in r['message']:
            pic_path = download_image_from_telegram(r)
            code = scan_qr_code(pic_path).decode("utf-8")
        else:
            print("Couldn't find msg text, suggesting verify input")
            message = status.statusErrorMsg[status.Status.quest_keyEnter.value]
            send_msg(chat_id, message)
            conn.close()
            return

        if code is not None:
            if code == "Повернутися до головного меню ⬅️":
                with conn.cursor() as cursor:
                    message = "Ось ваше меню:"

                    sql = "DELETE FROM `users_status` WHERE `chat_id` = %s;"
                    cursor.execute(sql, chat_id)
                    conn.commit()

                    send_msg(chat_id=chat_id, text=message, button_markup=settings.main_menu_keyboard)
            else:
                string_visited_quest_rooms = None
                array_visited_quest_rooms = None
                try:
                    with conn.cursor() as cursor:
                        sql = "SELECT * FROM `quest_rooms`"
                        cursor.execute(sql)
                        result = cursor.fetchall()
                        num_of_rooms = len(result)

                        sql = "SELECT * FROM `quest_rooms`, `team_list`, `members` WHERE `members`.`chat_id` = %s AND `members`.`id` = `team_list`.`captain_id` AND `team_list`.`current_quest_room` = `quest_rooms`.`id`"
                        cursor.execute(sql, chat_id)
                        result = cursor.fetchone()
                        if result is not None:

                            if result['visited_quest_rooms'] is not None:
                                string_visited_quest_rooms = result['visited_quest_rooms']
                                array_visited_quest_rooms = string_visited_quest_rooms.split(',')
                                if len(array_visited_quest_rooms) == num_of_rooms and array_visited_quest_rooms[-1] != '':
                                    message = "Ви уже побували в усіх кімнатах !"
                                    send_msg(chat_id=chat_id, text=message)
                                    return

                            current_room = result['current_quest_room']
                            current_score = result['score']

                            one_point_code = result["one_point_code"]
                            two_points_code = result["two_points_code"]
                            three_points_code = result["three_points_code"]

                            points = 0
                            if code == one_point_code:
                                points = 1
                                message = "Ви заробили один бал, старайтеся краще в майбутньому."
                            elif code == two_points_code:
                                points = 2
                                message = "Ви заробили два бали, непоганий результат, але можна краще."
                            elif code == three_points_code:
                                points = 3
                                message = "Вітаємо ! Ви заробили три бали."

                            else:
                                message = status.statusErrorMsg[status.Status.quest_keyEnter.value]
                                send_msg(chat_id=chat_id, text=message)
                                return

                            sql = "UPDATE `team_list`, `members` SET `team_list`.`score` = %s WHERE `team_list`.`captain_id` = `members`.`id` AND `members`.`chat_id` = %s;"
                            cursor.execute(sql, (int(current_score)+points, chat_id))
                            conn.commit()
                            send_msg(chat_id=chat_id, text=message)

                            #Становити правильний порядок відвіданих кімнат.
                            if string_visited_quest_rooms is not None:
                                string_visited_quest_rooms = result['visited_quest_rooms']
                                array_visited_quest_rooms = result['visited_quest_rooms'].split(',')

                                string_visited_quest_rooms = string_visited_quest_rooms + current_room

                                if len(array_visited_quest_rooms) < (num_of_rooms):
                                    string_visited_quest_rooms = string_visited_quest_rooms + ","
                                    sql = "UPDATE `team_list`, `members` SET `team_list`.`visited_quest_rooms` = %s WHERE `team_list`.`captain_id` = `members`.`id` AND `members`.`chat_id` = %s;"
                                    cursor.execute(sql, (string_visited_quest_rooms, chat_id))
                                    conn.commit()
                                    array_visited_quest_rooms[-1] = current_room

                                if len(array_visited_quest_rooms) == (num_of_rooms):
                                    sql = "UPDATE `team_list`, `members` SET `team_list`.`visited_quest_rooms` = %s WHERE `team_list`.`captain_id` = `members`.`id` AND `members`.`chat_id` = %s;"
                                    cursor.execute(sql, (string_visited_quest_rooms, chat_id))
                                    conn.commit()
                                    array_visited_quest_rooms[-1] = current_room

                            else:
                                string_visited_quest_rooms = current_room + ","
                                array_visited_quest_rooms = current_room
                                sql = "UPDATE `team_list`, `members` SET `team_list`.`visited_quest_rooms` = %s WHERE `team_list`.`captain_id` = `members`.`id` AND `members`.`chat_id` = %s;"
                                cursor.execute(sql, (string_visited_quest_rooms, chat_id))
                                conn.commit()

                            # Код для вибору нової кімнати
                            sql = "SELECT * FROM `quest_rooms` WHERE "
                            for id in array_visited_quest_rooms:
                                sql = sql + "`id` <> " + id + " AND "
                            sql = sql[0:len(sql)-4] + "ORDER BY `quest_rooms`.`teams_on_this_room` ASC;"
                            cursor.execute(sql)
                            result = cursor.fetchone()

                            if result is not None:
                                new_quest_room = result['id']
                                puzzle = result['puzzle']
                                sql = "UPDATE `team_list`, `members` SET `team_list`.`current_quest_room` = %s WHERE `team_list`.`captain_id` = `members`.`id` AND `members`.`chat_id` = %s;"
                                cursor.execute(sql, (new_quest_room, chat_id))
                                conn.commit()

                                message = "Ваша наступна підсказка така: '"+puzzle+"'\n Успіхів вам !"
                                send_msg(chat_id=chat_id, text=message)
                            else:
                                message = "Ви уже побували в усіх кімнатах !"
                                send_msg(chat_id=chat_id, text=message)

                        else:
                            message = "Не знайдено команду з даним ключем, спробуйте ще раз."
                            send_msg(chat_id=chat_id, text=message)

                except Exception as e:
                    print("Got database error at registration_enterKey function\nException: " + e.__doc__)

                finally:
                    conn.close()
        else:
            print("Couldn't find msg text, suggesting verify input")
            message = status.statusErrorMsg[status.Status.registration_keyEnter.value]
            send_msg(chat_id, message)
            conn.close()
            return


class Registration:

    @staticmethod
    def registration_start(chat_id):
        import status
        import pymysql.cursors
        conn = pymysql.connect(host=settings.database_host,
                               user=settings.database_user,
                               password=settings.database_user_pass,
                               db=settings.database_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO `users_status` (`id`, `chat_id`, `status`, `team_id`) VALUES (NULL, %s, %s, NULL);"
                cursor.execute(sql, (chat_id, status.Status.registration_keyEnter.value))
                conn.commit()
                button_markup_clear = "eydyZW1vdmVfa2V5Ym9hcmQnOlRydWV9"
                message = "Увага, буде вважатися, що профіль з якого ви реєструєтеся є профілем капітана команди. Якщо це не так, натисніть кнопку відміни.\n\nРозпочато реєстрацю, надішліть мені фотографію вашого персонального ключа:"
                send_msg(chat_id, message, button_markup=button_markup_clear)
        except Exception as e:
            print("Got DB ex: " + e.__doc__)
            message = "Сталася помилка при роботі з базою данних"
            send_msg(chat_id, message)
        finally:
            conn.close()

    @staticmethod
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

                    main_menu_markup = "eydrZXlib2FyZCc6W1t7J3RleHQnOifQoNC10ZTRgdGC0YDQsNGG0ZbRjyDinI/vuI8nfSx7J3RleHQnOifQotC10YXQvdC+INC60LLQtdGB0YIg8J+Oryd9LHsndGV4dCc6J9Ce0YLRgNC40LzQsNGC0Lgg0LrRgNC+0YHQstC+0YDQtCDwn46yJ31dLFt7J3RleHQnOifQotCw0LHQu9C40YbRjyDRgNC10LnRgtC40L3Qs9GW0LIg8J+PhSd9LHsndGV4dCc6J9CU0L7QstGW0LTQutCwIOKdkyd9XSxbeyd0ZXh0Jzon0JLQuNC60LvRjtGH0LjRgtC4INC80LXQvdGOIPCfkb4nfV1dLCdyZXNpemVfa2V5Ym9hcmQnOlRydWUsJ29uZV90aW1lX2tleWJvYXJkJzpGYWxzZX0="

                    message = "Операцію відмінео !"
                    send_msg(chat_id=chat_id, text=message, button_markup=main_menu_markup)
                else:
                    message = "Немає чого відміняти"
                    send_msg(chat_id=chat_id, text=message)

        except Exception as e:
            print("Got database error at registration_cancel function\nException: " + e.__doc__)

        finally:
            conn.close()

    @staticmethod
    def registration_enterKey(r):
        import status
        import pymysql.cursors
        conn = pymysql.connect(host=settings.database_host,
                               user=settings.database_user,
                               password=settings.database_user_pass,
                               db=settings.database_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        chat_id = r['message']['chat']['id']
        key = None
        if 'text' in r['message']:
            key = r['message']['text']
        elif 'photo' in r['message']:
            pic_path = download_image_from_telegram(r)
            key = scan_qr_code(pic_path)

        else:
            print("Couldn't find msg text, suggesting verify input")
            message = status.statusErrorMsg[status.Status.registration_keyEnter.value]
            send_msg(chat_id, message)
            conn.close()
            return
        if key is not None:
            try:
                with conn.cursor() as cursor:
                    sql = "SELECT * FROM `classes` WHERE `reg_key`= %s"
                    cursor.execute(sql, key)
                    result = cursor.fetchone()
                    if result is not None:
                        classid = result["id"]
                        class_name = result["class"]
                        sql = "SELECT * FROM `team_list` WHERE `class_id` = %s"
                        cursor.execute(sql, classid)
                        result = cursor.fetchone()
                        if result is not None:
                            message = "Вибачте, але данну групу вже зареєтровано, спробуйте ввести ключ ще раз, або натисніть /cancel"
                            send_msg(chat_id=chat_id, text=message)
                        else:
                            message = "Введено правильний ключ, обрано групу: '" + class_name + "'."
                            sql = "UPDATE `users_status` SET `status` = %s, `team_id` = '%s' WHERE `users_status`.`chat_id` = %s;"
                            cursor.execute(sql, (status.Status.registration_commandName.value, classid, chat_id))
                            conn.commit()

                            sql = "INSERT INTO `members` VALUES (NULL, NULL, '1', %s, NULL);"
                            cursor.execute(sql, chat_id)
                            conn.commit()

                            sql = "SELECT * FROM `members` WHERE `chat_id`= %s"
                            cursor.execute(sql, chat_id)
                            result = cursor.fetchone()
                            capitanid = result['id']

                            sql = "INSERT INTO `team_list` VALUES (NULL, NULL, %s, %s, NULL, NULL, NULL, 0);"
                            cursor.execute(sql, (classid, capitanid))
                            # cursor.execute(sql, (classid, result['id']))
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
        else:
            print("Couldn't find msg text, suggesting verify input")
            message = status.statusErrorMsg[status.Status.registration_keyEnter.value]
            send_msg(chat_id, message)
            conn.close()
            return

    @staticmethod
    def registration_commandName(r):
        import pymysql.cursors
        conn = pymysql.connect(host=settings.database_host,
                               user=settings.database_user,
                               password=settings.database_user_pass,
                               db=settings.database_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)

        import status
        chat_id = r['message']['chat']['id']
        try:
            name = r['message']['text']
        except Exception as e:
            print("Couldn't find msg text, suggesting verify input \nException: " + e.__doc__)
            message = status.statusErrorMsg[status.Status.registration_commandName.value]
            send_msg(chat_id, message)
            conn.close()
            return

        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM `members` WHERE `chat_id`= %s"
                cursor.execute(sql, chat_id)
                result = cursor.fetchone()
                if result is not None:
                    team_caitan_id = result['id']
                    sql = "UPDATE `team_list` SET `name` = %s WHERE `team_list`.`captain_id` = %s;"
                    cursor.execute(sql, (name, team_caitan_id))
                    conn.commit()

                    message = "Успішно встановлено назву команди."
                    send_msg(chat_id=chat_id, text=message)

                    sql = "UPDATE `users_status` SET `status` = %s WHERE `users_status`.`chat_id` = %s;"
                    cursor.execute(sql, (status.Status.registration_captainName.value, chat_id))
                    conn.commit()

                    message = "Введіть прізвище та ім'я капітана команди:"
                    send_msg(chat_id=chat_id, text=message)
                else:
                    message = "Не знайдено команду закріплену за вами."
                    send_msg(chat_id=chat_id, text=message)

        except Exception as e:
            print("Got database error at registration_enterKey function\nException: " + e.__doc__)

        finally:
            conn.close()

    @staticmethod
    def registration_captainName(r):
        import pymysql.cursors
        conn = pymysql.connect(host=settings.database_host,
                               user=settings.database_user,
                               password=settings.database_user_pass,
                               db=settings.database_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)

        import status
        chat_id = r['message']['chat']['id']
        try:
            name = r['message']['text']
        except Exception as e:
            print("Couldn't find msg text, suggesting verify input \nException: " + e.__doc__)
            message = status.statusErrorMsg[status.Status.registration_captainName.value]
            send_msg(chat_id, message)
            conn.close()
            return

        try:
            with conn.cursor() as cursor:
                sql = "UPDATE `members` SET `name` = %s WHERE `members`.`chat_id` = %s;"
                cursor.execute(sql, (name, chat_id))
                conn.commit()

                message = "Успішно встановлено данні капітана."
                send_msg(chat_id=chat_id, text=message)

                sql = "UPDATE `users_status` SET `status` = %s WHERE `users_status`.`chat_id` = %s;"
                cursor.execute(sql, (status.Status.registration_captainPhoneNumber.value, chat_id))
                conn.commit()

                button_markup_request_phone = "eydrZXlib2FyZCc6W1t7J3RleHQnOifQndCw0LTQsNGC0Lgg0L3QvtC80LXRgCDRgtC10LvQtdGE0L7QvdGDJywncmVxdWVzdF9jb250YWN0JzpUcnVlfV1dLCdyZXNpemVfa2V5Ym9hcmQnOlRydWUsJ29uZV90aW1lX2tleWJvYXJkJzpUcnVlfQ=="

                message = "Введіть номер телефону капітана у форматі (+380XXXXXXXXX), або натиніть на запропоновану кнопку:"
                send_msg(chat_id=chat_id, text=message, button_markup=button_markup_request_phone)

        except Exception as e:
            print("Got database error at registration_enterKey function\nException: " + e.__doc__)
            message = "Сталася невідома помилка, код " + status.Status.registration_captainName.value + " 🤷‍"
            send_msg(chat_id=chat_id, text=message)

        finally:
            conn.close()

    @staticmethod
    def registration_captainPhoneNumber(r):
        import pymysql.cursors
        conn = pymysql.connect(host=settings.database_host,
                               user=settings.database_user,
                               password=settings.database_user_pass,
                               db=settings.database_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)

        import status
        chat_id = r['message']['chat']['id']
        parse_success = [False, False]

        phone = ""
        if 'text' in r['message']:
            phone = r['message']['text']
            parse_success[0] = True
        if 'contact' in r['message']:
            phone = r['message']['contact']['phone_number']
            parse_success[1] = True
        button_markup_request_phone = "eydrZXlib2FyZCc6W1t7J3RleHQnOifQndCw0LTQsNGC0Lgg0L3QvtC80LXRgCDRgtC10LvQtdGE0L7QvdGDJywncmVxdWVzdF9jb250YWN0JzpUcnVlfV1dLCdyZXNpemVfa2V5Ym9hcmQnOlRydWUsJ29uZV90aW1lX2tleWJvYXJkJzpUcnVlfQ=="
        import re
        if not re.compile('\+?380[50,63,66,67,68,73,89,91,92,93,94,95,96,97,98,99]\d{6,9}').match(phone):
            message = "Введено не правильний номер телефону\n" \
                      "Введіть номер телефону капітана у форматі (+380XXXXXXXXX), або натиніть на запропоновану кнопку:"
            send_msg(chat_id=chat_id, text=message, button_markup=button_markup_request_phone)
            return
        else:
            try:
                with conn.cursor() as cursor:
                    sql = "UPDATE `members` SET `phone_number` = %s WHERE `members`.`chat_id` = %s;"
                    cursor.execute(sql, (phone, chat_id))
                    conn.commit()

                    button_markup_clear = "eydyZW1vdmVfa2V5Ym9hcmQnOlRydWV9"

                    message = "Успішно встановлено данні капітана."
                    send_msg(chat_id=chat_id, text=message, button_markup=button_markup_clear)

                    sql = "UPDATE `users_status` SET `status` = %s WHERE `users_status`.`chat_id` = %s;"
                    cursor.execute(sql, (status.Status.registration_teammateName.value, chat_id))
                    conn.commit()

                    message = "Введіть прізвище та ім'я члена команди:"
                    send_msg(chat_id=chat_id, text=message, button_markup=button_markup_clear)

            except Exception as e:
                print("Got database error at registration_enterKey function\nException: " + e.__doc__)
                message = "Сталася невідома помилка, код " + status.Status.registration_captainPhoneNumber.value + " 🤷‍"
                send_msg(chat_id=chat_id, text=message)

            finally:
                conn.close()

    @staticmethod
    def registration_teammateName(r):
        import pymysql.cursors
        conn = pymysql.connect(host=settings.database_host,
                               user=settings.database_user,
                               password=settings.database_user_pass,
                               db=settings.database_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)

        import status
        chat_id = r['message']['chat']['id']
        try:
            name = r['message']['text']
        except Exception as e:
            print("Couldn't find msg text, suggesting verify input \nException: " + e.__doc__)
            message = status.statusErrorMsg[status.Status.registration_teammateName.value]
            send_msg(chat_id, message)
            conn.close()
            return

        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO `members` VALUES (NULL, %s, '0', NULL, NULL);"
                cursor.execute(sql, name)
                conn.commit()

                sql = "SELECT * FROM `members` WHERE `name` = %s;"
                cursor.execute(sql, name)
                result = cursor.fetchone()

                new_member_id = result['id']

                sql = "SELECT * FROM `members`, `team_list` WHERE `members`.`chat_id` = %s AND `members`.`id` = `team_list`.`captain_id`;"
                cursor.execute(sql, chat_id)
                result = cursor.fetchone()
                members_ids = None
                array_members_ids = None
                if result['members_id'] is not None:
                    members_ids = result['members_id']
                    array_members_ids = members_ids.split(",")

                    members_ids = members_ids + str(new_member_id)

                    if len(array_members_ids) < (int (settings.num_of_members) - 1):
                        members_ids = members_ids + ","
                        sql = "UPDATE `team_list`, `members` SET `team_list`.`members_id` = %s WHERE `team_list`.`captain_id` = `members`.`id` AND `members`.`chat_id` = %s;"
                        cursor.execute(sql, (members_ids, chat_id))
                        conn.commit()

                        message = "Успішно встановлено данні члена команди.\nВведіть наступне прізвище ім'я:"
                        send_msg(chat_id=chat_id, text=message)

                    if len(array_members_ids) == (int (settings.num_of_members) - 1):
                        sql = "UPDATE `team_list`, `members` SET `team_list`.`members_id` = %s WHERE `team_list`.`captain_id` = `members`.`id` AND `members`.`chat_id` = %s;"
                        cursor.execute(sql, (members_ids, chat_id))
                        conn.commit()

                        message = "Успішно встановлено данні всіх членів команди."
                        send_msg(chat_id=chat_id, text=message)

                        sql = "UPDATE `users_status` SET `status` = %s WHERE `users_status`.`chat_id` = %s;"
                        cursor.execute(sql, (status.Status.registration_Verification.value, chat_id))
                        conn.commit()

                        verification_buttons_markup = "eydrZXlib2FyZCc6W1t7J3RleHQnOifQktGW0LTQvNGW0L3QsCDinYwnfSx7J3RleHQnOifQn9GA0LDQstC40LvRjNC90L4g4pyU77iPJ31dXSwncmVzaXplX2tleWJvYXJkJzpUcnVlLCdvbmVfdGltZV9rZXlib2FyZCc6VHJ1ZX0="

                        sql = "SELECT * FROM `members`, `team_list`, `classes` WHERE `members`.`chat_id` = %s AND `members`.`id` = `team_list`.`captain_id` AND `team_list`.`class_id` = `classes`.`id`;"
                        cursor.execute(sql, chat_id)
                        result = cursor.fetchone()

                        command_class = result['class']
                        command_name = result['team_list.name']
                        captain_name = result['name']
                        captain_phone = result['phone_number']
                        team_ids_array = result['members_id'].split(",")
                        team_names_array = []
                        for member_id in team_ids_array:
                            sql = "SELECT * FROM `members` WHERE `members`.`id` = %s;"
                            cursor.execute(sql, member_id)
                            result = cursor.fetchone()
                            team_names_array.append(result['name'])

                        message = "Будь ласка підтвердіть правильність введених даних:\nГрупа: '" + command_class + "'\nНазва команди: '" + command_name + "'\nПрізвище Ім'я капітана: '"\
                                  + captain_name + "'\nНомер телефону капітана: '" + captain_phone + "'\nДанні членів команди:\n"
                        i = 1
                        for name in team_names_array:
                            message = message + str(i) + ". '" + name + "'\n"
                            i = i + 1

                        send_msg(chat_id=chat_id, text=message, button_markup=verification_buttons_markup)

                else:
                    members_ids = str(new_member_id) + ","
                    sql = "UPDATE `team_list`, `members` SET `team_list`.`members_id` = %s WHERE `team_list`.`captain_id` = `members`.`id` AND `members`.`chat_id` = %s;"
                    cursor.execute(sql, (members_ids, chat_id))
                    conn.commit()

                    message = "Успішно встановлено данні члена команди.\nВведіть наступне прізвище ім'я:"
                    send_msg(chat_id=chat_id, text=message)

        except Exception as e:
            print("Got database error at registration_teammateName function\nException: " + e.__doc__)
            message = "Сталася невідома помилка, код " + status.Status.registration_teammateName.value + " 🤷‍"
            send_msg(chat_id=chat_id, text=message)

        finally:
            conn.close()

    @staticmethod
    def registration_registrationVerification(r):
        import pymysql.cursors
        conn = pymysql.connect(host=settings.database_host,
                               user=settings.database_user,
                               password=settings.database_user_pass,
                               db=settings.database_DB,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)

        import status
        chat_id = r['message']['chat']['id']
        try:
            respond = r['message']['text']
        except Exception as e:
            print("Couldn't find msg text, suggesting verify input \nException: " + e.__doc__)
            message = status.statusErrorMsg[status.Status.registration_Verification.value]
            send_msg(chat_id, message)
            conn.close()
            return

        if respond == "Відміна ❌":
            Registration.registration_cancel(chat_id=chat_id)

        if respond == "Правильно ✔️":
            try:
                with conn.cursor() as cursor:

                    sql = "DELETE FROM `users_status` WHERE `users_status`.`chat_id` = %s;"
                    cursor.execute(sql, chat_id)
                    conn.commit()

                    message = "Успішно завершено реєстрацію !"
                    send_msg(chat_id=chat_id, text=message)

            except Exception as e:
                print("Got database error at registration_enterKey function\nException: " + e.__doc__)
                message = "Сталася невідома помилка, код " + status.Status.registration_teammateName.value + " 🤷‍"
                send_msg(chat_id=chat_id, text=message)

            finally:
                conn.close()
