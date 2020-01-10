#!/usr/bin/python3
# pylint: disable=print-used,attribute-deprecated
"""Stub a Cubiscan server

Allow testing the connection to Cubiscan from Odoo
without real hardware.
"""

import asyncio
import random


@asyncio.coroutine
def handle_cubiscan(reader, writer):
    message = yield from reader.readline()
    addr = writer.get_extra_info("peername")

    print("Received {!r} from {!r}".format(message, addr))
    # print("Expecting {!r} from {!r}".format(message, addr))
    print("{!r}".format(message == b"\x02M\x03\r\n"))
    if message == b"\x02M\x03\r\n":
        length = random.uniform(0, 1000)
        width = random.uniform(0, 1000)
        height = random.uniform(0, 1000)
        weight = random.uniform(0, 10000)
        answer = (
            b"\x02MAH123456,L%05.1f,W%05.1f,H%05.1f,M,K%06.1f,D%06.1f,M,F0000,I\x03\r\n"
            % (length, width, height, weight, weight)
        )
    else:
        answer = b"\x02\x03\r\n"
    print("Send: {!r}".format(answer))
    writer.write(answer)
    yield from writer.drain()


def main():
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle_cubiscan, "0.0.0.0", 9876, loop=loop)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    addr = server.sockets[0].getsockname()
    print("Serving on {}".format(addr))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == "__main__":
    main()
