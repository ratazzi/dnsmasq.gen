#!/usr/bin/env python
# coding=utf-8

import sys
import subprocess
import re
import yaml
import Queue
import dns.resolver
import socket
from optparse import OptionParser
socket.setdefaulttimeout(30)

# ping 测试次数
NUMBER_OF_PING = 5

# 一个未被污染的以及一个本地 DNS
DEFAULT_DNS = ('208.67.222.222', '202.96.134.133')

def _o(output):
    sys.stdout.write(output + '\n')
    sys.stdout.flush()

class DnsmasqGen(object):
    def __init__(self):
        self.verbose = False
        self.debug = False
        self.output = False

    def avg(self, times):
        sum = 0
        for t in times:
            sum += float(t)
        return sum / len(times)

    def _nslookup(self, domain, nameserver, queue):
        """
        get all A records
        """
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [nameserver]
        try:
            for row in resolver.query(domain):
                queue.put(str(row))
        except dns.resolver.NoNameservers:
            pass
        except Exception:
            pass
        return

    def nslookup(self, domain, nameservers):
        items = []
        rs_queue = Queue.Queue()
        for nameserver in nameservers:
            self._nslookup(domain, nameserver, rs_queue)
        while rs_queue.qsize():
            items.append(rs_queue.get())
        return set(items)

    def ping(self, ip, queue):
        cmd = 'ping -c %d %s' % (NUMBER_OF_PING, ip)
        try:
            p = subprocess.Popen(cmd, shell=True,
                    stdout=subprocess.PIPE)
            p.wait()
            output = p.stdout.read()
        except Exception, e:
            sys.stderr.write('%s\n' % str(e))
            sys.stderr.flush()
            return
        times = re.findall(r'time=([0-9\.]{1,7})\sms', output)
        if len(times):
            _avg = self.avg(times)
            queue.put((_avg, ip))

    def _section(self, line, dns):
        domain = line.rstrip()
        pan_analytic = False
        if domain.startswith('*'):
            pan_analytic = True
            domain = domain.split(',')[1]

        # 获取每条记录的平均响应时间
        rows = {domain: dict()}
        rs_queue = Queue.Queue()
        for record in self.nslookup(domain, dns):
            self.ping(record, rs_queue)
        while rs_queue.qsize():
            (avg, ip) = rs_queue.get()
            rows[domain][avg] = ip

        if len(rows[domain]) == 0:
            return

        _rows = rows[domain].items()
        _rows.sort()
        if len(_rows) == 1:
            _o('server=/%s/%s\n' % (domain, dns[0]))
            _o('')
            return

        # 泛解析
        if pan_analytic:
            _domain = '.'.join(domain.split('.')[1:])
            _o('address=/.%s/%s # %.2f ms' % \
                    (_domain, _rows[0][1], float(_rows[0][0])))
        else:
            _o('address=/%s/%s # %.2f ms' % \
                    (domain, _rows[0][1], float(_rows[0][0])))

        # 输出所有结果
        if self.verbose:
            for _row in _rows[1:]:
                _o('# address=/%s/%s # %.2f ms' % \
                        (domain, _row[1], float(_row[0])))
        _o('')

    def section(self, name, domains, dns=DEFAULT_DNS):
        if not name:
            name = domains[0]
        _o('# %s' % name)

        for line in domains:
            self._section(line, dns)

def parse_command_line():
    # command line options
    parser = OptionParser()

    parser.add_option('--verbose', dest='verbose', action='store_true',
        help='output all recoreds', default=False)

    parser.add_option('--debug', dest='debug', action='store_true',
        help='output to standard output', default=False)

    parser.add_option('--list', dest='list', action='store_true',
        help='list all sections', default=False)

    parser.add_option('--input', dest='input', type='string', action='store',
        help='read domains from file')

    # parser.add_option('--output', dest='output', type='string',
    #     action='store', help='output to file')

    parser.add_option('--section', dest='section', type='string',
        action='store', help='only process special section')

    parser.add_option('--all', dest='all', action='store_true',
        help='process all sections')

    return parser.parse_args()

def main():
    (options, args) = parse_command_line()
    domains = None

    dnsmasq_gen = DnsmasqGen()
    dnsmasq_gen.debug = options.debug
    dnsmasq_gen.verbose = options.verbose
    # dnsmasq_gen.output = options.output

    if options.input:
        with open(options.input, 'r') as fp:
            domains = yaml.load(fp)
    else:
        if not sys.stdin.isatty():
            domain = sys.stdin.read().rstrip()
        else:
            domain = sys.argv[1]

        dnsmasq_gen.section(None, (domain, ))
        sys.exit(0)

    if options.list:
        for name in domains.keys():
            _o(' \033[01;32m*\033[00m %s' % name)
        _o('')
        sys.exit(0)

    if options.section:
        section = options.section
        dnsmasq_gen.section(options.section, domains[section]['items'],
                domains[section]['dns'])
        sys.exit(0)

    if options.all:
        for name, items in domains.items():
            dnsmasq_gen.section(name, items['items'], items['dns'])
        sys.exit(0)

if __name__ == '__main__':
    main()
