import os
import threading
import time
import urllib.request
import webview

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_URL = "http://127.0.0.1:8000"


class Api:

    def __init__(self):
        self.splash_complete = threading.Event()

    def close_app(self):
        webview.windows[0].destroy()

    def splash_done(self):
        print("[GF Brain] splash_done() chamado")
        self.splash_complete.set()


api = Api()


def wait_for_server(url, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url, timeout=2).close()
            return True
        except Exception:
            time.sleep(0.5)
    return False


def startup():
    splash.events.loaded.wait()
    print("[GF Brain] splash loaded")

    splash_done = api.splash_complete.wait(timeout=25)
    print(f"[GF Brain] splash_done={splash_done}")

    if wait_for_server(SERVER_URL):
        print(f"[GF Brain] server up, loading {SERVER_URL}")
        splash.load_url(SERVER_URL)
    else:
        fallback = f"file:///{os.path.join(BASE_DIR, 'frontend', 'index.html')}"
        print(f"[GF Brain] server down, loading {fallback}")
        splash.load_url(fallback)


splash = webview.create_window(
    title="GF Brain",
    url=os.path.join(BASE_DIR, "frontend", "splash.html"),
    js_api=api,
    width=1280,
    height=740,
    text_select=False,
    resizable=False,
    frameless=True,
    background_color="#0A0A0A"
)

threading.Thread(
    target=startup,
    daemon=True
).start()

webview.start()
