import asyncio
from datetime import datetime
from coin_spider.async_spider.base import BaseWS

class OkexTrade(BaseWS):
    instrument_ids = ["ETC-USDT", "OKB-USDT", "DOGE-USDT", "BTT-USDT", "BCH-USDT", "BTC-USDT", "EOS-USDT", "ETH-USDT", "LTC-USDT", "QTUM-USDT", "DOT-USDT", "NEO-USDT", "ONT-USDT", "XLM-USDT", "BSV-USDT", "OMG-USDT", "XRP-USDT", "SUSHI-USDT", "LINK-USDT", "DASH-USDT", "XTZ-USDT", "UNI-USDT", "FIL-USDT", "ZEC-USDT", "TRX-USDT", "IOTA-USDT", "ATOM-USDT", "ADA-USDT", "ZIL-USDT", "WAVES-USDT", "SOL-USDT", "XMR-USDT", "THETA-USDT", "IOST-USDT", "OKT-USDT", "AAVE-USDT", "LSK-USDT", "CRV-USDT", "ALGO-USDT", "LUNA-USDT", "SC-USDT", "XEM-USDT", "GRT-USDT", "BAT-USDT", "KSM-USDT", "YFI-USDT", "BCD-USDT", "MANA-USDT", "BOX-USDT", "1INCH-USDT", "RVN-USDT", "TRB-USDT", "BTG-USDT", "MATIC-USDT", "EGLD-USDT", "CHZ-USDT", "ZRX-USDT", "FLM-USDT", "NEAR-USDT", "SRM-USDT", "MKR-USDT", "HBAR-USDT", "BAND-USDT", "COMP-USDT", "ICX-USDT", "SNX-USDT", "GHST-USDT", "NANO-USDT", "DGB-USDT"]
    on_open_message = [{'channel':'trades','instId':f"{instrument_id}-SWAP"} for instrument_id in instrument_ids]

    def on_message(self,ws,msg):
        data = msg.json()
        for _ in data.get('data',[]):
            item = {'instrument_id':_['instId'],'trade_id':_['tradeId'],'price':_['px'],'size':_['sz'],'side':_['side'],'timestamp':datetime.fromtimestamp(int(_['ts'])/1000)}
            print(item)


if __name__ == "__main__":
    obj = OkexTrade()
    asyncio.run(obj.forever_run())
