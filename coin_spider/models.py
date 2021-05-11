from datetime import datetime,timedelta
from django.db import models

SPECIAL_FIELDS = ['last_qty','last','best_ask','best_ask_size','best_bid','best_bid_size','open_utc0','open_utc8']
SPECIAL_FIELDS_MULTIPLE = 100000000

class CoinTrick(models.Model):
    product_id = models.CharField("币对",max_length=32,db_index=True)
    last_qty = models.BigIntegerField('最新成交的数量')
    last = models.BigIntegerField('最新成交价')
    best_ask = models.BigIntegerField('卖一价')
    best_ask_size = models.BigIntegerField('卖一价对应的量')
    best_bid = models.BigIntegerField('买一价',max_length=32)
    best_bid_size = models.BigIntegerField('买一价对应的数量')
    open_utc0 = models.BigIntegerField('UTC+0时开盘价')
    open_utc8 = models.BigIntegerField('UTC+8时开盘价')
    timestamp = models.DateTimeField("时间",db_index=True)

    class meta:
        ordering = ('-timestamp',)
        unique_together = ("product_id", "timestamp")

    def __str__(self):
            return '-'.join([self.product_id , str(self.last)])

    def before_create(self):
        for attr in SPECIAL_FIELDS:
            value = getattr(self,attr,None)
            setattr(self,attr,int(float(value)*SPECIAL_FIELDS_MULTIPLE))
        self.timestamp = datetime.strptime(self.timestamp,'%Y-%m-%dT%H:%M:%S.%fZ',) + timedelta(hours=8)

    @classmethod
    def field_list(cls):
        return list(key.name for key in cls._meta.fields if key.name !='id')

    def __getattribute__(self, item):
        value = super(CoinTrick, self).__getattribute__(item)
        if item in SPECIAL_FIELDS :
            return value/SPECIAL_FIELDS_MULTIPLE
        return value