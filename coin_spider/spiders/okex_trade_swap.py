import os
import sys
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from coin_spider.spiders.base import OkexWebsocket


class OkexTradeSwap(OkexWebsocket):
    cnt = 0
    total_cnt = 0
    instrument_ids = ["ETC-USD", "OKB-USD", "DOGE-USD", "BTT-USD", "BCH-USD", "BTC-USD", "EOS-USD", "ETH-USD", "LTC-USD", "QTUM-USD", "DOT-USD", "NEO-USD", "ONT-USD", "XLM-USD", "BSV-USD", "OMG-USD", "XRP-USD", "SUSHI-USD", "LINK-USD", "DASH-USD", "XTZ-USD", "UNI-USD", "FIL-USD", "ZEC-USD", "TRX-USD", "IOTA-USD", "ATOM-USD", "ADA-USD", "ZIL-USD", "WAVES-USD", "SOL-USD", "XMR-USD", "THETA-USD", "IOST-USD", "OKT-USD", "AAVE-USD", "LSK-USD", "CRV-USD", "ALGO-USD", "LUNA-USD", "SC-USD", "XEM-USD", "GRT-USD", "BAT-USD", "KSM-USD", "YFI-USD", "BCD-USD", "MANA-USD", "BOX-USD", "1INCH-USD", "RVN-USD", "TRB-USD", "BTG-USD", "MATIC-USD", "EGLD-USD", "CHZ-USD", "ZRX-USD", "FLM-USD", "NEAR-USD", "SRM-USD", "MKR-USD", "HBAR-USD", "BAND-USD", "COMP-USD", "ICX-USD", "SNX-USD", "GHST-USD", "NANO-USD", "DGB-USD"]
    instrument_ids += ["ETC-USDT", "OKB-USDT", "DOGE-USDT", "BTT-USDT", "BCH-USDT", "BTC-USDT", "EOS-USDT", "ETH-USDT", "LTC-USDT", "QTUM-USDT", "DOT-USDT", "NEO-USDT", "ONT-USDT", "XLM-USDT", "BSV-USDT", "OMG-USDT", "XRP-USDT", "SUSHI-USDT", "LINK-USDT", "DASH-USDT", "XTZ-USDT", "UNI-USDT", "FIL-USDT", "ZEC-USDT", "TRX-USDT", "IOTA-USDT", "ATOM-USDT", "ADA-USDT", "ZIL-USDT", "WAVES-USDT", "SOL-USDT", "XMR-USDT", "THETA-USDT", "IOST-USDT", "OKT-USDT", "AAVE-USDT", "LSK-USDT", "CRV-USDT", "ALGO-USDT", "LUNA-USDT", "SC-USDT", "XEM-USDT", "GRT-USDT", "BAT-USDT", "KSM-USDT", "YFI-USDT", "BCD-USDT", "MANA-USDT", "BOX-USDT", "1INCH-USDT", "RVN-USDT", "TRB-USDT", "BTG-USDT", "MATIC-USDT", "EGLD-USDT", "CHZ-USDT", "ZRX-USDT", "FLM-USDT", "NEAR-USDT", "SRM-USDT", "MKR-USDT", "HBAR-USDT", "BAND-USDT", "COMP-USDT", "ICX-USDT", "SNX-USDT", "GHST-USDT", "NANO-USDT", "DGB-USDT"]
    on_open_message = [{'channel':'trades','instId':f"{instrument_id}-SWAP"} for instrument_id in instrument_ids]

    def on_message(self,ws, message):
        for _ in json.loads(message).get('data',[]):
            item = {'instrument_id':_['instId'],'trade_id':_['tradeId'],'price':_['px'],'size':_['sz'],'side':_['side'],'timestamp':datetime.fromtimestamp(int(_['ts'])/1000)}
            # 缓存最新价格到redis
            self.okex_monitor.okex_record(item)
            self.okex_monitor.okex_compare_1(item)
            item['instrument_id'] = item['instrument_id'].replace('-SWAP','')
            self.db_obj.async_save_item(item)
            if item['instrument_id'].startswith('BTC-'):
                self.cnt +=1
                print(f"Message:{self.message_cnt} BTC:{self.cnt} Total:{self.total_cnt}",item)


if __name__ == "__main__":
    obj = OkexTradeSwap()
    obj.run()
