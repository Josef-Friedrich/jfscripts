#! /usr/bin/env python3

import argparse
import ipaddress
import re


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


def get_parser():
    parser = argparse.ArgumentParser(
        description='Convert mac addresses to EUI64 ipv6 addresses.',
    )

    parser.add_argument(
        'mac',
        help='The mac address.',
    )

    parser.add_argument(
        'prefix',
        help='The ipv6 /64 prefix.',
    )

    return parser


def main():
    args = get_parser().parse_args()

    print(mac_to_eui64(args.mac, args.prefix))


if __name__ == '__main__':
    main()
