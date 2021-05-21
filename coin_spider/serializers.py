import os
import datetime
from rest_framework import serializers


def get_channel_choices():
    db_names = list()
    for db_name in os.listdir('coin_db'):
        if db_name.endswith('.py') and (db_name not in ['base.py','__init__.py']):
            db_names.append(db_name.split('.')[0])
    return db_names

def get_instrument_id_choices():
    instrument_ids = ["BTC-USDT", "ETH-USDT", "ETC-USDT", "EOS-USDT", "LTC-USDT", "BCH-USDT", "BSV-USDT", "XRP-USDT", "TRX-USDT","OKB-USDT", "DOGE-USDT", "BTT-USDT", "QTUM-USDT", "DOT-USDT", "NEO-USDT", "ONT-USDT", "XLM-USDT", "OMG-USDT", "SUSHI-USDT", "LINK-USDT", "DASH-USDT", "XTZ-USDT", "UNI-USDT", "FIL-USDT", "ZEC-USDT", "IOTA-USDT", "ATOM-USDT", "ADA-USDT", "ZIL-USDT", "WAVES-USDT", "SOL-USDT", "XMR-USDT", "THETA-USDT", "IOST-USDT", "OKT-USDT", "AAVE-USDT", "LSK-USDT", "CRV-USDT", "ALGO-USDT", "LUNA-USDT", "SC-USDT", "XEM-USDT", "GRT-USDT", "BAT-USDT", "KSM-USDT", "YFI-USDT", "BCD-USDT", "MANA-USDT", "BOX-USDT", "1INCH-USDT", "RVN-USDT", "TRB-USDT", "BTG-USDT", "MATIC-USDT", "EGLD-USDT", "CHZ-USDT", "ZRX-USDT", "FLM-USDT", "NEAR-USDT", "SRM-USDT", "MKR-USDT", "HBAR-USDT", "BAND-USDT", "COMP-USDT", "ICX-USDT", "SNX-USDT", "GHST-USDT", "NANO-USDT", "DGB-USDT"]
    return instrument_ids

class DataExportSerializer(serializers.Serializer):
    channel = serializers.ChoiceField(label="数据类型",choices=get_channel_choices())
    instrument_id = serializers.ChoiceField(label='币对名',choices=get_instrument_id_choices(),help_text="历史k线只支持前9个币种的导出")
    crypto_margined = serializers.BooleanField(label="使用币本位",default=False,help_text="暂时只对永续合约的数据有效")
    start = serializers.DateTimeField(label='开始时间',format=None)
    end = serializers.DateTimeField(label='结束时间',format=None)
    source = serializers.CharField(label='数据源',initial='okex')

    def validate(self, attrs):
        start = attrs['start']
        end = attrs['end']
        if (start>= end) or (end>datetime.datetime.now()):
            raise serializers.ValidationError("时间范围错误，start要小于end，end要小于现在时间")
        return attrs

