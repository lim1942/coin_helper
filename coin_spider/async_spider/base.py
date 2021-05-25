import json
import sys
import aiohttp
import traceback
from common.tools import logger
from coin_db import get_db_by_name


class ImportDbMeta(type):
    def __new__(cls, *args, **kwargs):
        new_cls = type.__new__(cls, *args, **kwargs)
        name = sys.argv[0].split('/')[-1].split('.')[0]
        new_cls.db = get_db_by_name(name)
        return new_cls


class BaseWS(metaclass=ImportDbMeta):
    heartbeat=5
    proxies = 'http://127.0.0.1:3080/'
    url = "wss://ws.okex.com:8443/ws/v5/public"
    instrument_ids = None
    on_open_message = None

    def __init__(self,**kwargs):
        self.db_obj = self.db(**kwargs)
        self.db_obj.prepare_for_insert()
        self.kwargs = kwargs

    async def on_open(self,ws):
        return await ws.send_json({"op": "subscribe","args":self.on_open_message})

    def on_cont_message(self,ws,msg):
        print(msg.data)

    def on_message(self,ws,msg):
        print(msg.data)

    def on_binary_msg(self, ws, msg):
        print(msg.data)

    def on_ping(self, ws, msg):
        print(msg.data)

    def on_pong(self,ws,msg):
        print(msg.data)

    def on_close(self,ws,msg):
        logger('async_spider',self.__class__.__name__,'on_close','close',f"{str(msg.data)}-{str(msg.extra)}")

    def on_error(self,ws,msg):
        logger('async_spider',self.__class__.__name__,'on_error','error',str(msg.data))

    async def run(self):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.url,proxy=self.proxies,ssl=False,heartbeat=self.heartbeat) as ws:
                await self.on_open(ws)
                async for msg in ws:
                    msg_type_name = msg.type.name
                    # 断续消息
                    if msg_type_name == 'CONTINUATION':
                        self.on_cont_message(ws,msg)
                    # 普通消息
                    elif msg_type_name == 'TEXT':
                        self.on_message(ws,msg)
                    # 二进制消息
                    elif msg_type_name == 'BINARY':
                        self.on_binary_msg(ws,msg)
                    # ping消息
                    elif msg_type_name == 'PING':
                        self.on_ping(ws,msg)
                    # pong消息
                    elif msg_type_name == 'PONG':
                        self.on_pong(ws,msg)
                    # close消息
                    elif msg_type_name == 'CLOSE':
                        self.on_close(ws,msg)
                    # closing消息
                    elif msg_type_name == 'CLOSING':
                        self.on_close(ws,msg)
                    # closed消息
                    elif msg_type_name == 'CLOSED':
                        self.on_close(ws,msg)
                    # error消息
                    elif msg_type_name == 'ERROR':
                        self.on_error(ws,msg)

    async def forever_run(self):
        while True:
            try:
                await self.run()
            except:
                traceback.print_exc()
                logger('async_spider',self.__class__.__name__,'forever_run','main',json.dumps(traceback.format_exc()))

