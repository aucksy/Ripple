"""The guard that makes "offline" a fact rather than a claim.

A build machine has internet. That is exactly how an offline build ships with
something in it that quietly reaches out: on the machine where it was tested
the call succeeded, so nothing looked wrong, and the first time anyone finds
out is on the locked-down machine where it hangs instead.

So outbound connections are blocked outright, in the running application and in
the tests. Loopback is allowed, because Ripple talks to itself: the web server
listens on 127.0.0.1 and the browser connects to it. Anything else raises, and
the message says what was attempted, so a reach-out is a loud failure with an
address in it rather than a silent success.
"""
from __future__ import annotations

import ipaddress
import socket

LOOPBACK_NAMES = {"localhost", "localhost.localdomain", "ip6-localhost", ""}


class OutboundBlocked(RuntimeError):
    """Something tried to reach the network. Offline, that is a defect."""


_installed = False
_original: dict[str, object] = {}
attempts: list[str] = []              # every address that was refused


def _host_is_local(host: object) -> bool:
    if isinstance(host, bytes):
        host = host.decode("utf-8", "ignore")
    if not isinstance(host, str):
        return False
    name = host.strip().strip("[]").lower()
    if name in LOOPBACK_NAMES:
        return True
    try:
        return ipaddress.ip_address(name).is_loopback
    except ValueError:
        # A name that is not an address would have to be looked up to be
        # judged, and looking it up is itself a call off this machine.
        return False


def _address_is_local(address: object) -> bool:
    if not isinstance(address, tuple) or not address:
        return True                    # a unix socket or a pipe, not the network
    return _host_is_local(address[0])


def _describe(address: object) -> str:
    if isinstance(address, tuple) and len(address) >= 2:
        return f"{address[0]}:{address[1]}"
    return str(address)


def _refuse(address: object) -> OutboundBlocked:
    where = _describe(address)
    attempts.append(where)
    return OutboundBlocked(
        f"Ripple Offline tried to reach {where}. This copy of Ripple must never "
        f"call out — nothing here should need the network."
    )


def install() -> None:
    """Block every outbound connection from this process. Loopback still works."""
    global _installed
    if _installed:
        return
    _original.update({
        "connect": socket.socket.connect,
        "connect_ex": socket.socket.connect_ex,
        "create_connection": socket.create_connection,
        "getaddrinfo": socket.getaddrinfo,
    })

    def connect(self, address, *a, **kw):
        if not _address_is_local(address):
            raise _refuse(address)
        return _original["connect"](self, address, *a, **kw)

    def connect_ex(self, address, *a, **kw):
        if not _address_is_local(address):
            raise _refuse(address)
        return _original["connect_ex"](self, address, *a, **kw)

    def create_connection(address, *a, **kw):
        if not _address_is_local(address):
            raise _refuse(address)
        return _original["create_connection"](address, *a, **kw)

    def getaddrinfo(host, port, *a, **kw):
        # Looking a name up is a call off the machine in its own right, so it
        # is refused here rather than at the connection it would lead to.
        if not _host_is_local(host):
            raise _refuse((host, port))
        return _original["getaddrinfo"](host, port, *a, **kw)

    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex
    socket.create_connection = create_connection
    socket.getaddrinfo = getaddrinfo
    _installed = True


def uninstall() -> None:
    """Put the real socket functions back. For tests that need to undo this."""
    global _installed
    if not _installed:
        return
    socket.socket.connect = _original["connect"]
    socket.socket.connect_ex = _original["connect_ex"]
    socket.create_connection = _original["create_connection"]
    socket.getaddrinfo = _original["getaddrinfo"]
    _installed = False


def installed() -> bool:
    return _installed
