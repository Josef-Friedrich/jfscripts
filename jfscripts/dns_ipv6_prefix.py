#! /usr/bin/env python3

import socket
import ipaddress


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


def main():
    ipv6 = get_ipv6('wnas.jf-dyndns.cf')

    prefix = ipaddress.ip_network(ipv6 + '/64', strict=False)

    print(prefix)