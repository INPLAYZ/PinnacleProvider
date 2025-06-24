import requests
import os
import threading
import time

class DataProvider(object):
    def __init__(self, send_msg):
        self.send_msg = send_msg
        self.session = None
        self.error_count = 0
        self.requests_count = 0
        self.headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        }
        self.rate_limit_time = 0
        self.rate_limit_lock = threading.Lock()


    def requests_data(self, url, method="get", format="text", post_data=[], get_status=False):
        try:
            resp_data = ""
            status_code = ""
            session = self.get_session()
            if method == "get":
                #ps3838的API需要慢到2秒call一次才不會跳429
                with self.rate_limit_lock:
                    while time.time() - self.rate_limit_time < 2:
                        time.sleep(0.1)
                    if post_data:
                        respone = session.get(url, timeout = 10, headers=self.headers, params=post_data)
                    else:
                        respone = session.get(url, timeout = 10, headers=self.headers)
                    self.rate_limit_time = time.time()
            else:
                if post_data:
                    respone = session.post(url, json=post_data, timeout = 5)
                else:
                    respone = session.post(url, timeout = 60)
            self.requests_count += 1
            status_code = respone.status_code
            if get_status: return status_code
            if status_code in [200, 204]:
                self.error_count = 0
                resp_data = eval(f"respone.{format}")
            else:
                raise
            return resp_data
        except:
            self.error_count += 1
            if self.error_count >= 30 or status_code == 503: #503通常是站台進維護了，重開爬蟲檢查狀態
                os._exit(0)
            self.close_session()
            if status_code not in [429]: #429不打log
                msg = f"url: {url}, method: {method} , format: {format}, post_data: {post_data}, status_code: {status_code}, error_count:{self.error_count}"
                self.send_msg(msg=msg, level="Warning")
            return "" if format == "text" else {}


    def get_session(self):
        if self.session is None:
            self.session = requests.Session()
        return self.session


    def close_session(self):
        if self.session is not None:
            self.session.close()
            self.session = None
