import sys
import time
import MySQLdb
import traceback
import MySQLdb.cursors
from queue import Queue
from threading import Thread
from datetime import datetime, timedelta
from tools import logger


class BaseMysqlMeta(type):
    def __new__(cls, *args, **kwargs):
        new_cls = type.__new__(cls, *args, **kwargs)
        # 获取类所在的模块名
        try:
            module_name = new_cls.__module__.split('.')[-1]
            assert module_name != '__main__'
        except:
            module_name = sys.argv[0].split('/')[-1].replace('.py','')
        if module_name not in ['base','__init__']:
            new_cls.mysql_db = module_name
            # 支持自定义表前缀
            if new_cls.table_prefix is None:
                new_cls.table_prefix = module_name.split('_')[1]
        return new_cls


class BaseMysql(metaclass=BaseMysqlMeta):
    # 数据库连接
    mysql_host = "192.168.30.185"
    mysql_user = 'root'
    mysql_db = None
    mysql_pwd = '123456'
    # 插入
    insert_sql = None
    insert_fields = tuple()
    insert_fields_date = []
    insert_fields_multiple = []
    insert_fields_multiple_cnt = 100000000
    # 建表
    table_sql = None
    table_prefix = None
    # 查询排序字段
    query_order_field = None

    # 通过数据字典获取插入value的元组
    @classmethod
    def get_value_by_item(cls,item):
        for field in cls.insert_fields_multiple:
            item[field] = int(float(item[field])*cls.insert_fields_multiple_cnt)
        for field, format, tz_hour in cls.insert_fields_date:
            item[field] = datetime.strptime(item[field],format) + timedelta(hours=tz_hour)
        return tuple(item[k] for k in cls.insert_fields)

    def __init__(self,kwargs=None):
        self.kwargs = kwargs or {}
        self.do_connect()

    # 连接数据库，获取连接对象
    def do_connect(self):
        try:
            self.connect = MySQLdb.connect(self.mysql_host, self.mysql_user, self.mysql_pwd,
                                           self.mysql_db, charset='utf8mb4', cursorclass=MySQLdb.cursors.DictCursor,)
            self.cursor = self.connect.cursor()
        except Exception as e:
            traceback.print_exc()
            logger('db_connect',self.__class__.__name__,'do_connect','error',traceback.format_exc())
            raise e

    # 断开数据库对象连接
    def close(self):
        self.cursor.close()
        self.connect.close()

    # 该表名是否存在
    def table_exists(self,table_name):
        sql = f"select * from information_schema.TABLES where TABLE_SCHEMA=(select database()) and `table_name` ='{table_name}'"
        self.cursor.execute(sql)
        return bool(self.cursor.fetchall())

    # 创建表
    def create_tables(self):
        raise NotImplementedError

    # 插入单个数据字典对象
    def save_item(self,item):
        raise NotImplementedError

    # 批量插入数据values元组
    def save_values(self,values):
        raise NotImplementedError

    # sql查询，并对查询结果进行时间和单位转化，迭代器输出
    def _query(self,sql,args):
        self.cursor.execute(sql,args=args)
        for item in self.cursor:
            for field in self.insert_fields_multiple:
                item[field] = item[field]/self.insert_fields_multiple_cnt
            for field, format, tz_hour in self.insert_fields_date:
                item[field] = item[field].strftime(format)
            yield item

    # 查询得到json结果
    def query(self,instrument_id,start,end):
        raise NotImplementedError

    # 查询得到csv结果
    def query_csv(self,instrument_id,start,end):
        yield ','.join(self.insert_fields) + '\n'
        for item in self.query(instrument_id,start,end):
            yield ','.join([str(item[k]) for k in self.insert_fields]) + '\n'

    # 数据插入前准备
    def prepare_for_insert(self):
        self.create_tables()

    # sql 执行失败重连再执行
    def re_connect_execute(self,sql,values):
        while True:
            try:
                if isinstance(values,list):
                    self.cursor.executemany(sql,args=values)
                elif isinstance(values,tuple):
                    self.cursor.execute(sql,values)
                else:
                    self.cursor.execute(sql)
                return self.connect.commit()
            except:
                traceback.print_exc()
                time.sleep(2)
                self.do_connect()
                logger('db',self.__class__.__name__,'re_connect_execute','error',traceback.format_exc())



class InstrumentIdMysql(BaseMysql):
    """不分表，一个对象根据 instrument_id 创建一张表"""
    def __init__(self,kwargs):
        self.instrument_id = kwargs['instrument_id']
        self.table_name = f"{self.table_prefix}_{self.instrument_id.replace('-','_')}"
        self.table_sql = self.table_sql.replace('table_name',self.table_name)
        self.insert_sql = self.insert_sql.replace('table_name',self.table_name)
        super().__init__(kwargs)

    def create_tables(self):
        self.re_connect_execute(self.table_sql,[])

    def save_values(self,values):
        self.re_connect_execute(self.insert_sql,values)

    def query(self,instrument_id,start,end):
        sql = f"SELECT * FROM {self.table_name} WHERE (time BETWEEN %s and %s) ORDER BY {self.query_order_field} desc;"
        for item in self._query(sql,[start,end]):
            yield item


class DateSplitMysql(BaseMysql):
    """按日期分表，每天创建一张新表，插入时要判断数据日期插入哪张表，
    查询时要根据筛选时间段，遍历时间范围内的表输出所有表的查询结果
    1.守护创建表线程，监控日期变化创建新表用于数据插入。
    2.守护线程插入数据， 主线程往结果队列丢数据，守护线程不停从队列获取数据插入数据库
    """
    # 插入分表字段
    insert_split_field_index =  None
    # 批量插入数量
    demons_save_value_size = 200

    def __init__(self,kwargs=None):
        super().__init__(kwargs)
        self.async_save_queue = Queue()

    def get_table_name_by_date(self,datetime):
        return f"{self.table_prefix}_{datetime.strftime('%Y_%m_%d')}"

    def create_tables(self):
        now = datetime.now()
        for date in [now,now+timedelta(days=1)]:
            date_table_sql = self.table_sql.replace('table_name',self.get_table_name_by_date(date))
            self.re_connect_execute(date_table_sql,[])

    def save_item(self,item):
        value = self.get_value_by_item(item)
        sql = self.insert_sql.replace('table_name',self.get_table_name_by_date(value[self.insert_split_field_index]))
        self.cursor.execute(sql,value)
        self.connect.commit()
        return value

    def query(self,instrument_id,start,end):
        cur = end
        while 1:
            table_name = self.get_table_name_by_date(cur)
            if self.table_exists(table_name):
                sql = f"SELECT * FROM {table_name} WHERE (instrument_id=%s) and (timestamp BETWEEN %s and %s) ORDER BY {self.query_order_field} desc;"
                for item in self._query(sql,[instrument_id,start,end]):
                    yield item
            cur = cur -timedelta(days=1)
            if cur.date() < start.date():
                break

    def async_save_item(self,item):
        value = self.get_value_by_item(item)
        table_name = self.get_table_name_by_date(value[self.insert_split_field_index])
        self.async_save_queue.put((table_name,value,))

    def demons_save_value(self):
        cnt = 0
        temp_dict = {}
        while True:
            table_name,value = self.async_save_queue.get()
            if table_name in temp_dict:
                temp_dict[table_name].append(value)
            else:
                temp_dict[table_name] = [value]
            cnt +=1
            if cnt == self.demons_save_value_size:
                # 达到阈值，进行入库
                for table_name,values in temp_dict.items():
                    sql = self.insert_sql.replace('table_name',table_name)
                    self.re_connect_execute(sql,values)
                cnt = 0
                temp_dict = {}

    @classmethod
    def demons_create_tables(cls):
        while 1:
            now = datetime.now()
            hour = now.hour
            # 0点的时候建表
            if hour == 0:
                obj = cls()
                obj.create_tables()
                obj.close()
                time.sleep(4000)
            else:
                time.sleep(10)

    def prepare_for_insert(self):
        # 初始建表
        self.create_tables()
        # 监控日期变化建表
        thread = Thread(target=self.demons_create_tables)
        thread.start()
        # 异步存储时从缓存中存储到数据库
        thread = Thread(target=self.demons_save_value)
        thread.start()
