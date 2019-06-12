token = "819066941:AAGuh7wFi_Ek_RjZMzBGGC61ry1ZLCkxY_0"

URL = 'https://api.telegram.org/bot' + token + '/'

ngrok_token = "2YKzZQs5HbksqP1AkRZaN_3TwdEn6CwZLzED16HeqMs"

#################################
database_host = "51.254.175.184"

database_user = "wocd_dev_user"

database_user_pass = "2E3i9T5i"

database_DB = "wocd_dev_db"

num_of_members = 0
#################################


def parse_external_settings():
    import pymysql.cursors
    conn = pymysql.connect(host=database_host,
                           user=database_user,
                           password=database_user_pass,
                           db=database_DB,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

    try:
        with conn.cursor() as cursor:

            sql = "SELECT * FROM `settings`;"
            cursor.execute(sql)
            result = cursor.fetchall()
            global num_of_members
            for row in result:
                if row['attribute'] == "num_of_members": #TODO переробити як відтягуються данні
                    num_of_members = row['value']

    except Exception as e:
        print("Got database error at parse_external_settings function\nException: " + e.__doc__)

    finally:
        conn.close()
