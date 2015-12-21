#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import fnmatch
import re
import logging
import yaml
import pyinotify

_DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
_LOGGER = logging.getLogger(__name__)


def _configure_logging():
    _LOGGER.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter(_DEFAULT_LOG_FORMAT)
    ch.setFormatter(formatter)
    _LOGGER.addHandler(ch)


class EventHandler(pyinotify.ProcessEvent):
    def my_init(self, base_dir, ignore):
        self.abs_dir = os.path.abspath(base_dir)
        self.ssw = ignore['startswith'].split(',')
        self.esw = ignore['endswith'].split(',')

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

    def process_IN_ATTRIB(self, event):
        # do something.
        _LOGGER.info("metadata changed:%s", event.pathname)

    def process_IN_CREATE(self, event):
        # do something.
        _LOGGER.info("creating:%s", event.pathname)

    def process_IN_MODIFY(self, event):
        # do something.
        _LOGGER.info("modify:%s", event.pathname)

    def process_IN_DELETE(self, event):
        # do something.
        _LOGGER.info("delete:%s", event.pathname)

    def process_IN_MOVED_FROM(self, event):
        # do something.
        _LOGGER.info("move:%s", event.pathname)

    def process_IN_MOVED_TO(self, event):
        # do something.
        _LOGGER.info("move to:%s", event.pathname)


def monitor(path, ignore):
    wm = pyinotify.WatchManager()
    handler = EventHandler(base_dir=path, ignore=ignore)
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    wm.add_watch(path, pyinotify.ALL_EVENTS, rec=True, auto_add=True)
    print '==> Start monitoring %s (type c^c to exit)' % path
    notifier.loop()


if __name__ == '__main__':
    config = yaml.load(file('config.yml'))
    path = config['path']
    ignore = config['ignore']
    _configure_logging()
    monitor(path, ignore)
