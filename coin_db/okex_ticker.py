from coin_db.base import DateSplitMysql
from coin_helper.settings import TZ_HOUR


class OkexTickerMysql(DateSplitMysql):
    # 插入
    insert_fields = ('instrument_id','last_qty','last','best_ask','best_ask_size','best_bid','best_bid_size','open_utc0','open_utc8','timestamp')
    insert_sql = f"""INSERT IGNORE INTO table_name({','.join(insert_fields)}) VALUES({','.join(('%s' for _ in insert_fields))});"""
    insert_fields_date = [('timestamp','%Y-%m-%dT%H:%M:%S.%fZ',TZ_HOUR)]
    insert_fields_multiple = ['last_qty','last','best_ask','best_ask_size','best_bid','best_bid_size','open_utc0','open_utc8']
    insert_split_field_index = 9
    # 查询
    query_order_field = 'timestamp'
    # 建表
    table_sql = f"""CREATE TABLE If Not Exists `table_name` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `instrument_id` varchar(32) NOT NULL,
          `last_qty` bigint(20) NOT NULL,
          `last` bigint(20) NOT NULL,
          `best_ask` bigint(20) NOT NULL,
          `best_ask_size` bigint(20) NOT NULL,
          `best_bid` bigint(20) NOT NULL,
          `best_bid_size` bigint(20) NOT NULL,
          `open_utc0` bigint(20) NOT NULL,
          `open_utc8` bigint(20) NOT NULL,
          `timestamp` datetime(6) NOT NULL,
          PRIMARY KEY (`id`),
          KEY `instrument_id` (`instrument_id`),
          KEY `timestamp` (`timestamp`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """


if __name__ == "__main__":
    OkexTickerMysql().create_tables()