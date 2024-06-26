#! /usr/bin/env python3

import argparse
import ipaddress
import socket

from jfscripts import __version__


def get_ipv6(dns_name: str) -> str | None:
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
    return None


def get_parser() -> argparse.ArgumentParser:
    """The argument parser for the command line interface.

    :return: A ArgumentParser object.
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description="Get the ipv6 prefix from a DNS name.")

    parser.add_argument(
        "dnsname",
        help="The DNS name, e. g. josef-friedrich.de",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    return parser


def main() -> None:
    args = get_parser().parse_args()
    ipv6 = get_ipv6(args.dnsname)
    if not ipv6:
        raise Exception("No ipv6 address found.")
    prefix = ipaddress.ip_network(ipv6 + "/64", strict=False)
    print(prefix)


if __name__ == "__main__":
    main()
