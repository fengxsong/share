#-coding:utf-8-*-

import sys
from optparse import OptionParser
from tasks import JOBS, r

parser = OptionParser()
parser.add_option("-c", "--critical",
                  dest="critical_max_fails", type="int", default=3)
(opts, args) = parser.parse_args()

errors = []

for j in JOBS.keys():
    rst = r.hgetall(j)
    if rst:
        fails = int(rst['fails'])
        if fails >= opts.critical_max_fails:
            errors.append('JOB %s:FAILED %d TIMES' % (j, fails))
if len(errors) > 0:
    print "CRITICAL | " + ";".join(errors)
    sys.exit(2)
else:
    print "OK | ALL TASKS HAVE BEEN EXECUTED."
    sys.exit(0)
