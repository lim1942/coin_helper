import json
import redis
import requests
import traceback
from datetime import datetime,timedelta
from coin_helper.settings import REDIS_URL


class RedisTool(object):
    def __init__(self):
        self.R = redis.Redis.from_url(REDIS_URL,decode_responses=True)
        self.P = self.R.pipeline(transaction=False)

    def set(self,k,v,ex):
        self.R.set(k,v,ex=ex)

    def get(self,k):
        return self.R.get(k)


class Monitor:
    redis_obj = RedisTool()

    def __init__(self,**kwargs):
        self.kwargs = kwargs
        self.last_notify_time = {}
        self.long_before_time = datetime.now() - timedelta(days=1)

    def record(self,k,v,ex=10):
        try:
            return self.redis_obj.set(k,v,ex)
        except:
            traceback.print_exc()

    def compare(self,k,v,k2):
        pass

    def notify(self,k,message):
        notify_time = datetime.now()
        if notify_time - timedelta(hours=6) >= self.last_notify_time.get(k,self.long_before_time):
            try:
                self._notify(message)
                self.last_notify_time[k] = notify_time
            except:
                traceback.print_exc()

    def _notify(self,text):
        webhook='https://oapi.dingtalk.com/robot/send?access_token=494a793fe8aa1146b93baeef9aba96cbfa725e2ce6230c0eaa37bb682e06eea8'
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"}
        message ={
            "msgtype": "text",
            "text": {
                "content": f"触发价差信号 {text}"
            },
            "at": {
                "atMobiles":[
                    "13750872274"
                ],
                "isAtAll": False
            }}
        message_json=json.dumps(message)
        return requests.post(url=webhook,data=message_json,headers=header).text


class OkexMonitor(Monitor):

    def __init__(self,**kwargs):
        super(OkexMonitor, self).__init__(**kwargs)
        self.variance_threshold = 0.05

    def compare(self,k,v,k2):
        try:
            v = float(v)
            v2 = float(self.redis_obj.get(k2))
            variance = abs(v - v2)
            variance_rate = variance/v
            if variance_rate > self.variance_threshold:
                message = f"【{k}:{v}】与【{k2}:{v2}】差异率大于{self.variance_threshold}, 差值{round(variance,6)} 差率{round(variance_rate,6)}"
                self.notify(k,message)
        except:
            pass
            # print(k,k2)

    def okex_record(self,item):
        self.record(item['instrument_id'],item['price'])

    def okex_compare_1(self,item):
        """okex永续币本位，永续USDT 币币 三个市场两两对比"""
        instrument_id = item['instrument_id']
        if instrument_id.endswith('USDT-SWAP'):
            self.compare(instrument_id,item['price'],item['instrument_id'].split('-')[0]+'-USDT')
            self.compare(instrument_id,item['price'],item['instrument_id'].split('-')[0]+'-USD-SWAP')
        # 币本位永续和币币比较
        elif instrument_id.endswith('USD-SWAP'):
            self.compare(instrument_id,item['price'],item['instrument_id'].split('-')[0]+'-USDT')


