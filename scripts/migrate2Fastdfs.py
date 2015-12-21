#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os


class TestFastdfs():
    def __init__(self, base_dir, tmpfile, fdfs_conf, redis_host="localhost", redis_port=6379, redis_db=0):
        import redis
        import fdfs_client.client as fdfs

        self.base_dir = base_dir
        self.tmpfile = tmpfile
        pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=redis_db)
        self.r = redis.Redis(connection_pool=pool)
        self.client = fdfs.Fdfs_client(fdfs_conf)

    def upload(self):
        for parent, dirnames, filenames in os.walk(self.base_dir):
            for filename in filenames:
                rel_filename = os.path.join(parent, filename)
                if not self.r.get(rel_filename):
                    ret = self.client.upload_by_filename(rel_filename)
                    with open(self.tmpfile, 'a+') as fn:
                        fn.write(rel_filename + '\n')
                    self.r.set(rel_filename, ret['Remote file_id'])

    def delete(self):
        with open(self.tmpfile) as fn:
            for rel_filename in fn:
                remote_file_id = self.r.get((rel_filename.strip()))
                if remote_file_id:
                    try:
                        self.client.delete_file(remote_file_id)
                        self.r.delete(rel_filename.strip())
                    except Exception:
                        pass
        os.remove(self.tmpfile)


if __name__ == '__main__':
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 10
    FDFS_CLIENT_CONF = "/etc/fdfs/client.conf"
    BASEDIR = "data/files"
    TMPFILE = "/tmp/test_tmpfile"
    test = TestFastdfs(BASEDIR, TMPFILE, FDFS_CLIENT_CONF, redis_db=REDIS_DB)
    test.upload()
    test.delete()