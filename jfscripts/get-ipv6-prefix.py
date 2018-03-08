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


def mac_to_eui64(mac, prefix=None):
    '''
    Convert a MAC address to a EUI64 address
    or, with prefix provided, a full IPv6 address
    '''
    # http://tools.ietf.org/html/rfc4291#section-2.5.1
    eui64 = re.sub(r'[.:-]', '', mac).lower()
    # 5c514fcf0a5d
    eui64 = eui64[0:6] + 'fffe' + eui64[6:]
    # 5c514ffffecf0a5d
    eui64 = hex(int(eui64[0:2], 16) ^ 2)[2:].zfill(2) + eui64[2:]
    # 5e514ffffecf0a5d

    if prefix is None:
        return ':'.join(re.findall(r'.{4}', eui64))
    else:
        try:
            net = ipaddress.ip_network(prefix, strict=False)
            euil = int('0x{0}'.format(eui64), 16)
            return str(net[euil])
        except:  # noqa: E722
            return


ipv6 = get_ipv6('wnas.jf-dyndns.cf')

prefix = ipaddress.ip_network(ipv6 + '/64', strict=False)

eui64 = mac_to_eui64('5c:51:4f:cf:0a:5d', prefix)
print(eui64)
