# dnsmasq.gen

## 概述
dnsmasq.gen 是一个辅助工具，用于根据域名自动生成 [Dnsmasq][dnsmasq] 配置文件，主要适用于使用 VPN 结合 [chnroutes][chnroutes] 的情况，因为 DNS 污染的问题，不得不使用 [OpenDNS][opendns] 之类的国外 DNS，以至于解析国内域名，本程序通过使用不同地区的 DNS 来解析同一域名，然后通过简单的 ping 测试来初步判断选择最快的服务器以达到优化目的。

## 数据源
数据源为 yaml 格式，示例：

    apple: # 为保持生成的文件可读性
      dns: ['168.95.192.1', '208.67.222.222'] # 用来解析域名的 DNS 服务器
      items:
        - swcdn.apple.com # address=/swcdn.apple.com/203.69.113.35 # 97.33 ms
        - '*,a1.phobos.apple.com' # address=/.phobos.apple.com/203.69.113.136 # 66.27 ms

## 使用

    # 单个域名
    dnsmasq.gen a1.phobos.apple.com
    echo 'a1.phobos.apple.com' | dnsmasq.gen

    # 多个域名
    dnsmasq.gen --input internet.yaml --section apple --verbose
    dnsmasq.gen --input internet.yaml --section apple --verbose > dnsmasq.conf
    dnsmasq.gen --input internet.yaml --all --verbose > dnsmasq.conf

    # 使用 python 实现的 ping，速度会快一些，但是需要 root 权限
    dnsmasq.gen --input internet.yaml --section apple --verbose --python-ping

## 备注
本程序仅仅为辅助工具，因为仅仅通过 ping 来测试速度，不能保证一定准确。
某些网站不适合通过这种方案优化，比如远程服务器禁止 ping，Dropbox 没有 CDN 并且同一域名经常解析出来不是同一 ip 等。

[dnsmasq]: http://www.thekelleys.org.uk/dnsmasq/doc.html "Dnsmasq"
[chnroutes]: http://code.google.com/p/chnroutes/ "chnroutes"
[opendns]: http://www.opendns.com/ "OpenDNS"
