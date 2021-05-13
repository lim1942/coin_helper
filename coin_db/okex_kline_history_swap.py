from coin_db.base import InstrumentIdMysql
from coin_helper.settings import TZ_HOUR


class OkexKlineHistorySwapMysql(InstrumentIdMysql):
    # 插入
    insert_fields = ('open','high','low','close','volume','time')
    insert_sql = f"""INSERT IGNORE INTO table_name({','.join(insert_fields)}) VALUES({','.join(('%s' for _ in insert_fields))});"""
    insert_fields_date = [('time','%Y-%m-%dT%H:%M:%S.%fZ',TZ_HOUR)]
    insert_fields_multiple = ('open','high','low','close','volume')
    # 查询
    query_order_field = 'time'
    # 建表
    table_sql = f"""CREATE TABLE If Not Exists `table_name` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `open` bigint(20) NOT NULL,
          `high` bigint(20) NOT NULL,
          `low` bigint(20) NOT NULL,
          `close` bigint(20) NOT NULL,
          `volume` bigint(20) NOT NULL,
          `time` datetime(6) NOT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `time` (`time`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """

    @classmethod
    def get_value_by_item(cls,item):
        item = {'open':item[1],'high':item[2],'low':item[3],'close':item[4],'volume':item[5],'time':item[0]}
        return super().get_value_by_item(item)


if __name__ == "__main__":
    OkexKlineHistorySwapMysql(instrument_id='BTC-USDT').create_tables()