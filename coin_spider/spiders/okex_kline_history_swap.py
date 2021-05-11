import os
import sys
import time
import traceback
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime,timedelta
from coin_helper.settings import TZ_HOUR
from coin_spider.spiders.base import InstrumentIdSpider


class OkexKlineHistorySwapSpider(InstrumentIdSpider):
    batch_cnt = 300
    granularity = 60
    interval_days = 1
    start_end_hours = (batch_cnt * granularity) / 3600
    instrument_ids = ["BTC-USD", "ETH-USD", "LTC-USD", "ETC-USD", "XRP-USD", "EOS-USD", "BCH-USD", "BSV-USD", "TRX-USD",]
    instrument_ids += ["BTC-USDT", "ETH-USDT", "LTC-USDT", "ETC-USDT", "XRP-USDT", "EOS-USDT", "BCH-USDT", "BSV-USDT", "TRX-USDT",]

    @classmethod
    def crawl(cls,instrument_id):
        db_obj = cls.db({"instrument_id":instrument_id})
        db_obj.prepare_for_insert()
        start = datetime.now() - timedelta(hours=TZ_HOUR)
        finally_end = start - timedelta(days=cls.interval_days)
        url = f'https://www.okex.win/api/swap/v3/instruments/{instrument_id}-SWAP/history/candles'
        while True:
            try:
                end = start - timedelta(hours=cls.start_end_hours)
                start_date = start.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                end_date = end.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                params = {
                    'start':start_date,
                    'end':end_date,
                    'granularity':cls.granularity
                }
                resp = cls.download(url,params=params)
                values = [cls.db.get_value_by_item(item) for item in resp.json()]
                db_obj.save_values(values)
                print(instrument_id,end_date,'>>>',finally_end)
                start = end
                if end <= finally_end:
                    break
            except:
                traceback.print_exc()
            time.sleep(0.1)


if __name__ == "__main__":
    OkexKlineHistorySwapSpider.execute()