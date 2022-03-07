from dbutils.pooled_db import PooledDB
import pymysql

from sina.settings import MYSQL_SETTING as db_config


class ConnectionPool:
    __pool = None

    def __init__(self):
        self.conn = self._get_conn()
        self.cursor = self.conn.cursor()

    def _get_conn(self):
        if self.__pool is None:
            self.__pool = PooledDB(
                creator=pymysql,
                mincached=db_config['DB_MIN_CACHED'],
                maxcached=db_config['DB_MAX_CACHED'],
                maxshared=db_config['DB_MAX_SHARED'],
                maxconnections=db_config['DB_MAX_CONNECYIONS'],
                blocking=db_config['DB_BLOCKING'],
                maxusage=db_config['DB_MAX_USAGE'],
                setsession=db_config['DB_SET_SESSION'],
                host=db_config['HOST'],
                port=db_config['PORT'],
                user=db_config['USER'],
                passwd=db_config['PASSWORD'],
                db=db_config['NAME'],
                use_unicode=True,
                charset=db_config['DB_CHARSET']
            )
        return self.__pool.connection()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

    def get_conn(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        return cursor, conn


def get_conn():
    return ConnectionPool()