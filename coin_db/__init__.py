import importlib
from coin_db.okex_trade import OkexTradeMysql
from coin_db.okex_ticker import OkexTickerMysql
from coin_db.okex_kline_history import OkexKlineHistoryMysql


def get_db_by_name(name):
    db_module = importlib.import_module(f'coin_db.{name}')
    db_class_name = ''.join(map(lambda x:x.capitalize() ,name.split('_')))+"Mysql"
    db = getattr(db_module,db_class_name)
    return db

def get_db_by_channel_source(channel,source,instrument_id):
    kwargs = {'source':source,'instrument_id':instrument_id}
    db_class = get_db_by_name(channel)
    return db_class(**kwargs)

