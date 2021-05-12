import os
import sys
import time
import traceback
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from coin_spider.spiders.base import DateSplitSpider


class OkexTickerSpider(DateSplitSpider):
    instrument_ids = ["BTC-USDT", "ETH-USDT", "ETC-USDT", "EOS-USDT", "LTC-USDT", "BCH-USDT", "BSV-USDT", "XRP-USDT", "TRX-USDT",]

    def crawl(self):
        patch_num = 1
        url = 'https://www.okex.win/api/spot/v3/instruments/ticker'
        while 1:
            try:
                value_print = []
                resp = self.download(url)
                for item in resp.json():
                    if item['instrument_id'] in self.instrument_ids:
                        value_print.append(f'{item["product_id"]}:{item["last"]}')
                        self.db_obj.async_save_item(item)
                print(patch_num,time.strftime("%Y-%m-%d %H:%M:%S"),' | '.join(value_print))
            except:
                traceback.print_exc()
            time.sleep(0.1)
            patch_num +=1


if __name__ == "__main__":
    OkexTickerSpider.execute()

