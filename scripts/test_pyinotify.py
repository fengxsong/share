#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import time
import fnmatch
import re
import logging
import yaml
import pyinotify
import redis
from subprocess import call

_DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
_LOGGER = logging.getLogger(__name__)


def _configure_logging():
    _LOGGER.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter(_DEFAULT_LOG_FORMAT)
    ch.setFormatter(formatter)
    _LOGGER.addHandler(ch)


class EventHandler(pyinotify.ProcessEvent):

    def my_init(self, base_dir, exclusion, target, password_file, redis_c):
        self.abs_dir = os.path.abspath(base_dir)
        self.ssw = exclusion['startswith']
        self.esw = exclusion['endswith']
        self.targets = target
        self.password_file = password_file
        pool = redis.ConnectionPool(host=redis_c['host'], port=redis_c[
                                    'port'], db=redis_c['db'])
        self.redis_conn = redis.Redis(connection_pool=pool)
        self.pipe = self.redis_conn.pipeline()

    def filter_swap(self, fn):
        if re.match(r'.(.*).sw*', fn):
            return True
        return False

    def notifier_filter(self, fn):
        if all(not fnmatch.fnmatch(fn.pathname, self.abs_dir + "/" + start) for start in self.ssw) and all(
                not fn.name.endswith(end) for end in self.esw) and fn.name != "4913" and not self.filter_swap(fn.name):
            return True
        return False

    def __call__(self, event):
        if self.notifier_filter(event):
            super(EventHandler, self).__call__(event)

    def comfirm_rsync(self, fn, status_code):
        self.pipe.hset(fn.pathname, 'timestamp', time.time()).hset(
            fn.pathname, 'status_code', status_code).execute()
        for target in self.targets:
            call(["rsync", "-avH", "--delete", "--progress",
                  "--password-file={0}".format(self.password_file), fn.pathname, target])
        self.pipe.hset(fn.pathname, 'rsync', 1).execute()

    def process_IN_ATTRIB(self, event):
        _LOGGER.info("metadata changed:%s", event.pathname)

    def process_IN_CREATE(self, event):
        _LOGGER.info("creating:%s", event.pathname)
        if not self.redis_conn.hgetall(event.pathname):
            self.comfirm_rsync(event, 1)

    def process_IN_MODIFY(self, event):
        _LOGGER.info("modify:%s", event.pathname)
        if time.time() - float(self.redis_conn.hget(event.pathname, 'timestamp')) >= 3:
            self.comfirm_rsync(event, 2)

    def process_IN_DELETE(self, event):
        _LOGGER.info("delete:%s", event.pathname)
        self.redis_conn.delete(event.pathname)

    def process_IN_MOVED_FROM(self, event):
        _LOGGER.info("move:%s", event.pathname)

    def process_IN_MOVED_TO(self, event):
        _LOGGER.info("move to:%s", event.pathname)


def monitor(source, exclusion, target, password_file, redis_c):
    wm = pyinotify.WatchManager()
    handler = EventHandler(
        base_dir=source, exclusion=exclusion, target=target, password_file=password_file, redis_c=redis_c)
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    wm.add_watch(source, pyinotify.ALL_EVENTS, rec=True, auto_add=True)
    print '==> Start monitoring %s (type c^c to exit)' % source
    notifier.loop()


if __name__ == '__main__':
    config = yaml.load(file('config.yml'))
    source = config['source']
    exclusion = config['exclusion']
    target = config['target']
    password_file = config['password_file']
    if int(oct(os.stat(password_file).st_mode)[-3:]) > 600:
        import stat
        os.chmod(password_file, stat.S_IREAD + stat.S_IWRITE)
    redis_c = config['redis']
    _configure_logging()
    monitor(source, exclusion, target, password_file, redis_c)
