#!/usr/bin/env python
# coding=utf-8

import sys
import re
import ping
import subprocess
import multiprocessing

def avg(times):
    sum = 0
    for t in times:
        sum += float(t)
    return sum / len(times)

class LocalPing(object):
    def _ping(self, addr, number_of_ping):
        cmd = 'ping -c %d %s' % (number_of_ping, addr)
        try:
            p = subprocess.Popen(cmd, shell=True,
                    stdout=subprocess.PIPE)
            return (addr, p)
        except Exception, e:
            sys.stderr.write('%s\n' % str(e))
            sys.stderr.flush()

    def __call__(self, addrs, max_ping_process=5, number_of_ping=5):
        """local ping"""
        rs = []

        for i in range(0, len(addrs), max_ping_process):
            items = addrs[i:i + max_ping_process]
            pool = []
            for addr in items:
                (addr, p) = self._ping(addr, number_of_ping)
                pool.append((addr, p))
            for addr, p in pool:
                p.wait()
                output = p.stdout.read()
                times = re.findall(r'time=([0-9\.]{1,7})\sms', output)
                if len(times):
                    _avg = avg(times)
                    rs.append((round(_avg, 3), addr))
        return rs

class Ping(object):
    def _ping(self, addr, q, number_of_ping):
        (_lost, _max, _avg) = ping.quiet_ping(addr, number_of_ping)
        q.put((_avg, addr))

    def __call__(self, addrs, max_ping_process=5, number_of_ping=5):
        """pure python ping, must run with root privilege"""
        rs = []
        queue = multiprocessing.Queue()

        for i in range(0, len(addrs), max_ping_process):
            items = addrs[i:i + max_ping_process]
            pool = []
            for addr in items:
                p = multiprocessing.Process(target=self._ping,
                        args=(addr, queue, number_of_ping))
                p.start()
                pool.append(p)
            for p in pool:
                p.join()
        while not queue.empty():
            (avg, addr) = queue.get()
            if not avg:
                continue
            rs.append((round(avg, 3), addr))
        return rs
