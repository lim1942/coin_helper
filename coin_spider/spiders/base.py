import sys
import ssl
import time
import hmac
import json
import zlib
import base64
import hashlib
import requests
import websocket
import traceback
from threading import Thread
from coin_db import get_db_by_name
from tools import logger


# 元类自动导入数据库模块
class ImportDbMeta(type):
    def __new__(cls, *args, **kwargs):
        new_cls = type.__new__(cls, *args, **kwargs)
        name = sys.argv[0].split('/')[-1].split('.')[0]
        new_cls.db = get_db_by_name(name)
        return new_cls


class BaseWebsocket(metaclass=ImportDbMeta):
    db = None
    url = None
    run_kwargs = {'sslopt':{"cert_reqs": ssl.CERT_NONE},'http_proxy_host':'127.0.0.1','http_proxy_port':3080,'ping_interval':5}

    def __init__(self,**kwargs):
        self.db_obj = self.db()
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.url,on_open= self.on_open,on_message=self.on_message,
                                         on_error=self.on_error,on_close=self.on_close,)
    def on_error(self,ws, error):
        logger('spider',self.__class__.__name__,'on_error','error',error.__class__.__name__ + '-'+str(error))

    def on_close(self,ws):
        logger('spider',self.__class__.__name__,'on_close','warning','websocket close !!!!')

    def on_message(self,ws,message):
        print(message)

    def on_open(self,ws):
        print("### open ###")

    def run(self):
        self.ws.run_forever(**self.run_kwargs,)


class OkexWebsocket(BaseWebsocket):
    message_cnt = 0
    on_open_message = None
    url = "wss://real.okex.com:8443/ws/v3"

    def subscribe(self,ws,args):
        open_msg = {"op": "subscribe", "args": args}
        ws.send(json.dumps(open_msg).encode())

    def login(self,ws,key,passphrase,secret):
        timestamp = str(time.time())
        msg = timestamp + "GET" + "/users/self/verify"
        sign = hmac.new(secret.encode('utf-8'), msg.encode('utf-8'), digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(sign).decode('utf-8')
        data = {"op": "login", "args":[key, passphrase, timestamp, sign]}
        ws.send_msg(data)

    def on_open(self,ws):
        self.subscribe(ws,self.on_open_message)

    def on_message(self,ws,message):
        self.message_cnt += 1
        decompress = zlib.decompressobj(-zlib.MAX_WBITS)
        inflated = decompress.decompress(message)
        inflated += decompress.flush()
        return json.loads(inflated.decode())

    def run(self):
        self.db_obj.prepare_for_insert()
        while 1:
            try:
                self.message_cnt = 0
                self.ws.run_forever(**self.run_kwargs)
            except:
                traceback.print_exc()
                time.sleep(3)


class BaseSpider(metaclass=ImportDbMeta):
    timeout = 3
    db = None

    @classmethod
    def download(cls,url,meth='get',**kwargs):
        resp = requests.request(meth,url=url,timeout=cls.timeout,**kwargs)
        resp.encoding = 'utf-8'
        return resp

    @classmethod
    def retry_download(cls,url,meth='get',retry=3,**kwargs):
        for r in range(retry):
            try:
                return cls.download(url,meth,**kwargs)
            except Exception as e:
                pass
        raise e

    @classmethod
    def crawl(cls,*args,**kwargs):
        pass

    @classmethod
    def execute(cls):
        pass


class InstrumentIdSpider(BaseSpider):
    instrument_ids = []

    @classmethod
    def execute(cls):
        while True:
            threads = list()
            for instrument_id in cls.instrument_ids:
                thread = Thread(target=cls.crawl,args=(instrument_id,))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
            print("Process will sleep 1 hour ~~~\n")
            time.sleep(3600)


class DateSplitSpider(BaseSpider):
    work_num = 1
    @classmethod
    def execute(cls):
        for _ in range(cls.work_num):
            thread = Thread(target=cls.crawl)
            thread.start()