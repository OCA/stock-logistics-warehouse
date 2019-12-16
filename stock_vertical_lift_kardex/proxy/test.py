# pylint: disable=W8116
import asyncio
import logging
import socket
import time

_logger = logging.getLogger("kardex.proxy")
logging.basicConfig(level=logging.DEBUG)


class KardexProxyProtocol(asyncio.Protocol):
    def __init__(self, loop, queue):
        _logger.info("Proxy created")
        self.transport = None
        self.buffer = b""
        self.queue = queue
        self.loop = loop

    def connection_made(self, transport):
        _logger.info("Proxy incoming cnx")
        self.transport = transport
        self.buffer = b""

    def data_received(self, data):
        self.buffer += data
        _logger.info("Proxy: received %s", data)
        if len(self.buffer) > 65535:
            # prevent buffer overflow
            self.transport.close()

    def eof_received(self):
        _logger.info("Proxy: received EOF")
        if self.buffer[-1] != b"\n":
            # bad format -> close
            self.transport.close()
        data = (
            self.buffer.replace(b"\r\n", b"\n")
            .replace(b"\n", b"\r\n")
            .decode("iso-8859-1", "replace")
        )
        task = self.loop.create_task(self.queue.put(data))
        self.buffer = b""
        print("toto", task)

    def connection_lost(self, exc):
        self.transport = None
        self.buffer = b""


class KardexClientProtocol(asyncio.Protocol):
    def __init__(self, loop, queue):
        _logger.info("started kardex client")
        self.loop = loop
        self.queue = queue
        self.transport = None
        self.buffer = b""

    def connection_made(self, transport):
        self.transport = transport
        _logger.info("connected to kardex server %r", transport)

    async def keepalive(self):
        while True:
            t = int(time.time())
            msg = "61|ping%d|SH1-1|0|0||||||||\r\n" % t
            await self.send_message(msg)
            await asyncio.sleep(5)

    async def send_message(self, message):
        _logger.info("SEND %s", message)
        message = message.encode("iso-8859-1").ljust(1024, b"\0")
        self.transport.write(message)

    async def process_queue(self):
        while True:
            message = await self.queue.get()
            await self.send_message(message)

    def data_received(self, data):
        data = data.replace(b"\0", b"")
        _logger.info("RECV %s", data)
        self.buffer += data

    def connection_lost(self, exc):
        self.loop.stop()


if __name__ == "__main__":
    _logger.info("starting")
    loop = asyncio.get_event_loop()
    loop.set_debug(1)
    queue = asyncio.Queue(loop=loop)
    coro = loop.create_server(
        lambda: KardexProxyProtocol(loop, queue), port=3000, family=socket.AF_INET
    )
    server = loop.run_until_complete(coro)
    coro = loop.create_connection(
        lambda: KardexClientProtocol(loop, queue), "localhost", 9600
    )
    transport, client = loop.run_until_complete(coro)
    print("%r" % transport)
    loop.create_task(client.keepalive())
    loop.create_task(client.process_queue())
    _logger.info("run loop")
    loop.run_forever()
    loop.close()
