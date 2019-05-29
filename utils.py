import requests
import settings

def get_ngrok_url():
    import time
    time.sleep(10)
    r = requests.get("http://localhost:4040/api/tunnels")
    ngr = r.json()['tunnels'][0]['public_url']
    return ngr


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
