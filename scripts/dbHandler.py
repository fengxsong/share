# /usr/bin/env python
# coding:utf-8

import os, time
import json
import MySQLdb


class DataHandler():
    def __init__(self, **kwargs):
        """must define 'host', 'user', 'password'."""
        self.host = kwargs['host']
        self.user = kwargs['user']
        self.password = kwargs['password']
        if 'port' not in kwargs:
            self.port = 3306
        else:
            self.port = int(kwargs['port'])
        self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, port=self.port,
                                    connect_timeout=8, charset='utf8')

    def query(self, **kwargs):
        if 'db' in kwargs:
            self.conn.select_db(kwargs['db'])
        cursor = self.conn.cursor()
        count = cursor.execute(kwargs['sql'])
        if count == 0:
            result = None
        else:
            result = cursor.fetchall()
        cursor.close()
        return result

    def handler(self, **kwargs):
        if 'db' in kwargs:
            self.conn.select_db(kwargs['db'])
        cursor = self.conn.cursor()
        try:
            cursor.execute(kwargs['sql'])
            self.conn.commit()
            return True
        except MySQLdb.Error:
            return False
        finally:
            cursor.close()

    def __del__(self):
        self.conn.close()


def get_conf(fn):
    with open(fn) as f:
        s = json.load(f)
    return s


def update_record(db_name, tb_name):
    """initial:
    CREATE TABLE update_record(
    id int(2) unsigned NOT NULL AUTO_INCREMENT,
    update_time TIMESTAMP NOT NULL,
    dump_time TIMESTAMP NOT NULL,
    PRIMARY KEY (id)
    );
    usage:
    insert into update_record set id=1;
    update update_record set dump_time=NOW() where id=1;"""

    fn = os.getcwd() + '/config.json'
    s = get_conf(fn)
    master = s["master_mysql"]
    dbh = DataHandler(host=master["host"], user=master["user"], password=master["password"])
    is_equal = \
        dbh.query(sql='select case when update_time=dump_time then 1 else 0 end from update_record where id = 1;',
                  db=db_name)[0][0]
    if is_equal == 1:
        pass
    else:
        cmd = '/usr/local/mysql/bin/mysqldump -u%s -p%s %s %s >%s_%s_%s.sql' % (
            master['user'], master['password'], db_name, tb_name, db_name, tb_name,
            time.strftime('%Y%m%d_%H%M', time.localtime()))
        os.system(cmd)
        dbh.handler(sql='update update_record set dump_time=NOW() where id=1;', db=db_name)


if __name__ == '__main__':
    pass