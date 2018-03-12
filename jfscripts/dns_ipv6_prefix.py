#! /usr/bin/env python3

import socket
import ipaddress
import re


def get_ipv6(dns_name):
    result = socket.getaddrinfo(dns_name, port=None)

    for entry in result:
        #
        # entry:
        #
        # (family, type, proto, canonname, sockaddr)
        #
        # (
        #     <AddressFamily.AF_INET6: 10>,
        #     <SocketKind.SOCK_RAW: 3>,
        #     0,
        #     '',
        #     ('2003:68:4c06:3300:1e98:ecff:fe0f:d330', 0, 0, 0)
        # )
        if entry[0] == 10 and entry[2] == 0:
            return entry[4][0]


ipv6 = get_ipv6('wnas.jf-dyndns.cf')

prefix = ipaddress.ip_network(ipv6 + '/64', strict=False)

eui64 = mac_to_eui64('5c:51:4f:cf:0a:5d', prefix)
print(eui64)
