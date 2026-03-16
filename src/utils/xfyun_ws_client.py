# utils/xfyun_ws_client.py
import websocket
import ssl
import json
import base64
import hashlib
import hmac
from urllib.parse import urlencode, urlparse
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
import _thread as thread

class XFYunWSClient:
    def __init__(self, appid, api_key, api_secret, url, domain):
        self.appid = appid
        self.api_key = api_key
        self.api_secret = api_secret
        self.url = url
        self.domain = domain
        self.answer = ""

    def _create_url(self):
        host = urlparse(self.url).netloc
        path = urlparse(self.url).path
        date = format_date_time(mktime(datetime.now().timetuple()))

        signature_origin = f"host: {host}\n"
        signature_origin += f"date: {date}\n"
        signature_origin += f"GET {path} HTTP/1.1"

        signature_sha = hmac.new(
            self.api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()

        signature = base64.b64encode(signature_sha).decode("utf-8")
        authorization_origin = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature}"'
        )
        authorization = base64.b64encode(
            authorization_origin.encode("utf-8")
        ).decode("utf-8")

        params = {
            "authorization": authorization,
            "date": date,
            "host": host
        }
        return self.url + "?" + urlencode(params)

    def chat(self, messages):
        self.answer = ""
        ws_url = self._create_url()

        def on_message(ws, message):
            data = json.loads(message)
            if data["header"]["code"] != 0:
                ws.close()
                return

            text = data["payload"]["choices"]["text"][0]
            if "content" in text:
                self.answer += text["content"]

            if data["payload"]["choices"]["status"] == 2:
                ws.close()

        def on_open(ws):
            def run(*args):
                payload = {
                    "header": {
                        "app_id": self.appid,
                        "uid": "library-user"
                    },
                    "parameter": {
                        "chat": {
                            "domain": self.domain,
                            "temperature": 0.7,
                            "max_tokens": 4096
                        }
                    },
                    "payload": {
                        "message": {
                            "text": messages
                        }
                    }
                }
                ws.send(json.dumps(payload))
            thread.start_new_thread(run, ())

        ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_open=on_open
        )
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        return self.answer