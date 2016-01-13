#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import sys
from optparse import OptionParser

usage = "usage: %prog -o arg1 -w arg2 -c arg3"
parser = OptionParser(usage=usage)
parser.add_option("-o", "--origin", dest="origin_mem_size",
                  help="Initialization memory value,e.g.2048m(b) 8G(b)")
parser.add_option("-w", "--warning",
                  dest="warning_per", help="Exit with WARNING status if less than PERCENT of memory space is free", )
parser.add_option("-c", "--critical",
                  dest="critical_per", help="Exit with CRITICAL status if less than PERCENT of memory space is free")
(opts, args) = parser.parse_args()

if not opts.warning_per or not opts.critical_per:
    print "Unknow - '-w' and '-c' must define!"
    sys.exit(3)

with open("/proc/meminfo") as fn:
    mem_info = fn.readlines()


def get_value(item):
    for i in mem_info:
        m = re.match(r'{0}:\s+(\d+) kB'.format(item), i)
        if m:
            return float(m.groups()[0])


def get_opts_origin_mem_size(parameter):
    mb = re.findall(r'(\d+)m|mb$', parameter, re.I)
    mg = re.findall(r'(\d+)G|Gb$', parameter, re.I)
    if mb:
        return float(mb[0]) * 1024
    elif mg:
        return float(mg[0]) * 1024 * 1024
    else:
        return None

cw = lambda x: float(re.findall(r'(\d+)%', x)[0])
warning_per = cw(opts.warning_per)
critical_per = cw(opts.critical_per)

if warning_per < critical_per:
    print "WARNING - WARNING percent should't less than CRITICAL percent!"
    sys.exit(1)

origin_mem_size = get_opts_origin_mem_size(opts.origin_mem_size)
if not origin_mem_size:
    print "Unknow - '-o' arg should endswith mb/gb."
    sys.exit(3)
mem_total = get_value('MemTotal')

if mem_total < origin_mem_size * 0.90:
    print "CRITICAL - Original memory is {:.2f} kB, but now is {:.2f} kB.".format(origin_mem_size, mem_total)
    sys.exit(2)

mem_free = get_value('MemFree')
perc = mem_free / mem_total
if perc >= warning_per / 100.00:
    print "OK - Current memory free is {:.2f} mB, percentage of free is {:.2f}%".format(mem_free / 1024, perc * 100)
    sys.exit(0)
elif warning_per / 100.00 > perc >= critical_per / 100.00:
    print "WARNING - Current memory free is {:.2f} mB, percentage of free is {:.2f}%".format(mem_free / 1024, perc * 100)
    sys.exit(1)
elif critical_per / 100.00 > perc:
    print "CRITICAL - Current memory free is {:.2f} mB, percentage of free is {:.2f}%".format(mem_free / 1024, perc * 100)
    sys.exit(2)
else:
    print "Unknow."
    sys.exit(3)
