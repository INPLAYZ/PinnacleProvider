import AppSettings
from datetime import datetime
import time
import os
import json
import threading
import random

class CrawlerService(object):
    def __init__(self, service_inputs):
        self.kafka_producers = service_inputs["kafka_producers"]
        self.machine_name = service_inputs["machine_name"]
        self.environment = service_inputs["environment"]
        self.version = service_inputs["version"]
        self.send_msg = service_inputs["send_msg"]
        self.provider = service_inputs["provider"]
        self.heart_txt = service_inputs["heart_txt"]
        self.topic = service_inputs["topic"]
        self.setting = AppSettings.settings["service"]
        self.page_info = {} # {"BK":{'pregame':3, 'inplay':1}, "BS":{...}}
        self.start_time = time.time()
        self.maintenance = "F"
        threading.Thread(target=self.listen_status, args=()).start()
        threading.Thread(target=self.call_dashboard, args=()).start()
        threading.Thread(target=self.check_running_6H, args=()).start()


    def main(self):
        self.start_time = time.time()
        self.check_maintenance()
        for gametype, gametype_id in self.setting['game_type'].items():
            self.page_info[gametype] = {'pregame':0, 'inplay':0}
            if 'Total' not in gametype:
                threading.Thread(target=self.get_lang_data, args=(gametype, gametype_id)).start()
            threading.Thread(target=self.get_pregame_data, args=(gametype, gametype_id)).start()
            threading.Thread(target=self.get_inplay_data ,args=(gametype, gametype_id)).start()
            time.sleep(0.5)

    def check_maintenance(self):
        while True:
            status = self.provider.requests_data(self.setting['home_page'], get_status=True)
            if status == 503:
                print("site maintenance now!")
                self.maintenance = "T"
            else:
                self.maintenance = "F"
                return
            time.sleep(60)

    def get_pregame_data(self, game_type, game_type_id):
        payload = {
            "btg": "1",
            "c": "",
            "cl": "100",
            "d": "",
            "ec": "",
            "ev": "",
            "g": "",
            "hle": False,
            "inl": False,
            "l": "100",
            "lang": "",
            "lg": "",
            "lv": "",
            "me": "0",
            "mk": "0", #2=賽中 1=今天 0=早盤
            "more": False,
            "o": "1",
            "ot": "1",
            "pa": "0",
            "pimo": "0,1",
            "pn": "-1",
            "pv": "1",
            "sp": game_type_id, #球種
            "tm": "0",
            "v": f"", #v值寫0或留空就是輸出比賽資料，輸入13位時間戳是目前pbp
            "locale": "en_US",
            "_": f"{int(time.time() * 1000)}",
            "withCredentials": True
        }
        if 'Total' in game_type:
            payload['btg'] = '100'
            payload['cl'] = '3'
            payload['l'] = '3'
        while True:
            try:
                payload['_'] = f"{int(time.time() * 1000)}"
                if 'Total' not in game_type: self.page_info[game_type]['pregame'] = 0
                for mk in range(2):
                    payload['mk'] = str(mk)
                    if payload['mk'] == "0": page_type = f"{game_type}-FU"
                    if payload['mk'] == "1": page_type = f"{game_type}-FT"
                    data = self.provider.requests_data(self.setting['web_api'], format="json()", post_data=payload)
                    if data:
                        if 'Total' not in game_type: self.page_info[game_type]['pregame'] += len(data.get('n')[0][2])
                        self.send_data(page_type=page_type, data=data)
            except:
                self.send_msg()
            time.sleep(300)

    def get_lang_data(self, game_type, game_type_id):
        payload = {
            "btg": "1",
            "c": "",
            "cl": "100",
            "d": "",
            "ec": "",
            "ev": "",
            "g": "",
            "hle": False,
            "inl": False,
            "l": "100",
            "lang": "",
            "lg": "",
            "lv": "",
            "me": "0",
            "mk": "2", #2=賽中 1=今天 0=早盤
            "more": False,
            "o": "1",
            "ot": "1",
            "pa": "0",
            "pimo": "0,1",
            "pn": "-1",
            "pv": "1",
            "sp": game_type_id, #球種
            "tm": "0",
            "v": f"",
            "locale": "", #填語系
            "_": f"{int(time.time() * 1000)}",
            "withCredentials": True
        }
        while True:
            for lang, site_lang in self.setting['need_lang'].items():
                try:
                    payload['locale'] = site_lang
                    payload['_'] = f"{int(time.time() * 1000)}"
                    data = self.provider.requests_data(self.setting['web_api'], format="json()", post_data=payload)
                    if data != {} and len(data.get('l')[0][2]) >= 1:
                        self.send_data(page_type=f"{game_type}-FI", data=data, lang=lang)
                except:
                    self.send_msg()
            time.sleep(3600)

    def get_inplay_data(self, game_type, game_type_id):
        payload = {
            "btg": "1",
            "c": "",
            "cl": "100",
            "d": "",
            "ec": "",
            "ev": "",
            "g": "",
            "hle": False,
            "inl": False,
            "l": "100",
            "lang": "",
            "lg": "",
            "lv": "",
            "me": "0",
            "mk": "2", #2=賽中 1=今天 0=早盤
            "more": False,
            "o": "1",
            "ot": "1",
            "pa": "0",
            "pimo": "0,1",
            "pn": "-1",
            "pv": "1",
            "sp": game_type_id, #球種
            "tm": "0",
            "v": f"", #v值寫0或留空就是輸出比賽資料，輸入13位時間戳是目前pbp
            "locale": "en_US",
            "_": f"{int(time.time() * 1000)}",
            "withCredentials": True
        }
        if 'Total' in game_type:
            payload['btg'] = '100'
            payload['cl'] = '3'
            payload['l'] = '3'
        while True:
            try:
                payload['_'] = f"{int(time.time() * 1000)}"
                payload['v'] = "" #拿比賽資料
                data = self.provider.requests_data(self.setting['web_api'], format="json()", post_data=payload)
                if data != {}:
                    if 'Total' not in game_type: self.page_info[game_type]['inplay'] = len(data.get('l')[0][2])
                    if len(data.get('l')[0][2]) >= 1: #len為0就是沒比賽
                        self.send_data(page_type=f"{game_type}-FI", data=data)
                        if 'Total' not in game_type: #Total不需要call pbp(因為資料是一樣的)
                            payload['v'] = f"{int(time.time() * 1000)}" #拿pbp
                            data = self.provider.requests_data(self.setting['web_api'], format="json()", post_data=payload)
                            self.send_data(page_type=f"{game_type}-FI", data=data)
            except:
                self.send_msg()
            time.sleep(100)

    def send_data(self, page_type, data, lang=""):
        """送出資料到Game Data

        Args:
            page_type (str): BS-FU、BS-FT、BS-FI
            lang (str):如果是語系資料則放在page_type內(TW-BS-FU)
            data (Dict[str, Any]): 賽事資料
        """
        try:
            if lang:
                page_type = f"{lang}-{page_type}"
            page_type = page_type.replace("MA2", "MA")
            result = {
                "page_type": page_type,
                "timestamp": int(datetime.now().timestamp() * 1000),
                "machinename": self.machine_name,
                "data": data,
            }
            for kafka in self.kafka_producers:
                kafka.send(self.topic, json.dumps(result))
        except:
            self.send_msg(msg=page_type)


    def listen_status(self):
        while True:
            try:
                with open(self.heart_txt, 'r') as f:
                    status = f.read()
                if status == "0":
                    msg = "Control close program."
                    self.send_msg(msg=msg, level="Information")
                    os._exit(0)
                time.sleep(5)
            except:
                self.send_msg()
                time.sleep(5)
                continue


    def check_running_6H(self):
        while True:
            now = time.time()
            if self.start_time != "":
                if (now-self.start_time) > 21600:
                    msg = "Running 6H, close program."
                    self.send_msg(msg=msg, level="Information")
                    os._exit(0)
            time.sleep(5)

    def call_dashboard(self):
        need_send = random.randint(1, 9)
        while True:
            time.sleep(10)
            try:
                page_pregame = 0
                page_inplay = 0
                for page_detail in self.page_info.values():
                    page_pregame += page_detail.get('pregame', 0)
                    page_inplay += page_detail.get('inplay', 0)
                dashboard_msg = f"pregame:{page_pregame} inplay:{page_inplay}"
                print(dashboard_msg)
                need_send += 1
                if need_send == 10:
                    msg = f"{datetime.now()} program alive, version is {self.version}, requests count: {self.provider.requests_count}, dashboard_msg: {dashboard_msg}"
                    self.send_msg(msg=msg, level="Information")
                    need_send = 0
                self.provider.requests_count = 0
            except:
                self.send_msg()
            time.sleep(50)