site = 'ps3838'
project_name = f"PS3838Provider"
topic = "test02"
heart = f'C:\Heart\heartPS3838V2.txt'

#kafka集群
kafka_9 = []
kafka_10 = []
kafka_11 = []

environment_path = {
    "Local":{
        "send_html_data": [kafka_9]
    },
    "PRD":{
        "send_html_data": [kafka_9]
    },
    "PRD2":{
        "send_html_data": [kafka_10]
    },
    "PRD3":{
        "send_html_data": [kafka_11]
    },
}
settings = {
    "service":{
        "home_page": "",
        "price_center_api":{
            "dashboard":"",
        },
        "game_type":{
            "SC": "29",
            "BK": "4",
            "BS": "3",
            "FL": "15",
            "HL": "19",
            "TN": "33",
            "ES": "12",
            "MA": "6",
            "MA2": "22",
            "VB": "34",
            # "VBTotal": "34", #不需要
            "BM": "1",
            "CK": "8",
            "WP": "36",
            "HB": "18",
            "SN": "28",
            "DT": "10",
            "BSTotal": "3",
            "BKTotal": "4",
            "FLTotal": "15",
            "HLTotal": "19",
            "HBTotal": "18",
            # "ESMap1": "12",#應該不需要(ES就有需要的資料)
            # "ESMap2": "12",
            # "ESMap3": "12",
            # "ESMap4": "12",
            # "ESMap5": "12"
        },
        "need_lang": {
            "TW": "zh-TW",
            "KO": "ko-KR",
            "JA": "ja-JP",
            "VI": "vi-VN",
            "TH": "th-TH",
            "ES": "es-ES",
            "FR": "fr-FR",
            "DE": "de-DE",
        },
        "home_page": "https://www.ps3838.com/",
        "web_api": "https://www.ps3838.com/sports-service/sv/compact/events",
    },
    "transformer":{},
}
