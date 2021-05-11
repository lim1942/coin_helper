from coin_db.base import DateSplitMysql
from coin_helper.settings import TZ_HOUR


class OkexTradeMysql(DateSplitMysql):
    # 插入
    insert_fields = ('side','trade_id','price','size','instrument_id','timestamp')
    insert_sql = f"""INSERT IGNORE INTO table_name({','.join(insert_fields)}) VALUES({','.join(('%s' for _ in insert_fields))});"""
    insert_fields_date = [('timestamp','%Y-%m-%dT%H:%M:%S.%fZ',TZ_HOUR)]
    insert_fields_multiple = ['price','size']
    insert_split_field_index = 5
    # 查询
    query_order_field = 'timestamp'
    # 建表
    table_sql = f"""CREATE TABLE If Not Exists `table_name` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `side` char(10) NOT NULL,
          `trade_id` char(20) NOT NULL,
          `price` bigint(20) NOT NULL,
          `size` bigint(20) NOT NULL,
          `instrument_id` char(20) NOT NULL,          
          `timestamp` datetime(6) NOT NULL,
          PRIMARY KEY (`id`),
          KEY `instrument_id` (`instrument_id`),
          KEY `timestamp` (`timestamp`),
          UNIQUE KEY `trade_id` (`instrument_id`, `trade_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """


if __name__ == "__main__":
    obj = OkexTradeMysql()
    # obj.create_tables()
    print(obj.table_exists('trade_2021_04_28'))