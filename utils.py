import requests
import settings

def setup_and_run_ngrook():
    import os, subprocess
    if os.name == "nt":  #if windows:
        from pathlib import Path
        home = str(Path.home())
        filepath = home + "\\.ngrok2\\ngrok.yml"
        if not os.path.exists(filepath):
            subprocess.Popen(["ngrok.exe", "authtoken", settings.ngrok_token])
        ##############################
        os.system("taskkill /f /im ngrok.exe")
        subprocess.Popen(["ngrok.exe", "http", "5000"])

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


def registration_start():
    return 0


