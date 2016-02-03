#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import sys
from optparse import OptionParser

usage = ""
parser = OptionParser(usage=usage)
parser.add_option("-s", "--states", dest="states", default='ESTABLISHED,')
parser.add_option("-c", "--critical", dest="critical", type="int", default=1000)
parser.add_option("-w", "--warning", dest="warning", type="int", default=500)

(opts, args) = parser.parse_args()

TCP_STATES = {
    '00': 'UNKNOWN',  # Bad state ... Impossible to achieve ...
    'FF': 'UNKNOWN',  # Bad state ... Impossible to achieve ...
    '01': 'ESTABLISHED',
    '02': 'SYN_SENT',
    '03': 'SYN_RECV',
    '04': 'FIN_WAIT1',
    '05': 'FIN_WAIT2',
    '06': 'TIME_WAIT',
    '07': 'CLOSE',
    '08': 'CLOSE_WAIT',
    '09': 'LAST_ACK',
    '0A': 'LISTEN',
    '0B': 'CLOSING'
}


def netstat(protocols=['tcp']):
    state_counts = {}
    for p in protocols:
        if os.path.isfile('/proc/net/' + p):
            with open('/proc/net/' + p) as fn:
                for line in fn.readlines():
                    m = re.match(
                        '^\s*\d+:\s+(.{8}|.{32}):(.{4})\s+(.{8}|.{32}):(.{4})\s+(.{2})', line)
                    if m:
                        connection_state = m.groups()[4]
                        # connection_port = int(m.groups()[1], 16)
                        connection_state = TCP_STATES[connection_state]
                                if not state_counts.has_key(connection_state):
                                    state_counts[connection_state] = 0
                                else:
                                    state_counts[connection_state] += 1
    return state_counts


def main():
    states_counts = netstat(['tcp', 'tcp6'])
    exit_code, msg = 0, ''
    for state in opts.states.split(','):
        if states_counts.has_key(state):
            if states_counts[state] >= opts.critical:
                exit_code, msg = 2, "CTITICAL: %s " % states_counts
                break
            elif states_counts[state] >= opts.warning:
                exit_code, msg = 1, "WARNING: %s" % states_counts
                break
            else:
                exit_code, msg = 0, "OK: %s" % states_counts
    print msg
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
