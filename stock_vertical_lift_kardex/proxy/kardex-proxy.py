#!/usr/bin/python3
import argparse
import asyncio
import logging
import os
import ssl
import time

import aiohttp

_logger = logging.getLogger(__name__)


class KardexProxyProtocol(asyncio.Protocol):
    def __init__(self, loop, queue, args):
        _logger.info("Proxy created")
        self.transport = None
        self.buffer = b""
        self.queue = queue
        self.loop = loop
        self.args = args

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
        self.loop.create_task(self.queue.put(data))
        self.buffer = b""

    def connection_lost(self, exc):
        self.transport = None
        self.buffer = b""


class KardexClientProtocol(asyncio.Protocol):
    def __init__(self, loop, queue, args):
        _logger.info("started kardex client")
        self.loop = loop
        self.queue = queue
        self.args = args
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
            await asyncio.sleep(20)

    async def send_message(self, message):
        _logger.info("SEND %r", message)
        message = message.encode("iso-8859-1")
        self.transport.write(message)

    async def process_queue(self):
        while True:
            message = await self.queue.get()
            await self.send_message(message)

    def data_received(self, data):
        data = data.replace(b"\0", b"")
        _logger.info("RECV %s", data)
        self.buffer += data
        if b"\r\n" in self.buffer:
            msg, sep, rem = self.buffer.partition(b"\r\n")
            self.buffer = rem
            msg = msg.decode("iso-8859-1", "replace").strip()
            if msg.startswith("0|ping"):
                _logger.info("ping ok")
            else:
                _logger.info("notify odoo: %s", msg)
                self.loop.create_task(self.notify_odoo(msg))

    def connection_lost(self, exc):
        self.loop.stop()

    async def notify_odoo(self, msg):
        url = self.args.odoo_url + "/vertical-lift"
        async with aiohttp.ClientSession() as session:
            params = {"answer": msg, "secret": self.args.secret}
            async with session.post(url, data=params) as resp:
                resp_text = await resp.text()
                _logger.info("Reponse from Odoo: %s %s", resp.status, resp_text)


def main(args, ssl_context=None):
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue(loop=loop)
    # create the main server
    coro = loop.create_server(
        lambda: KardexProxyProtocol(loop, queue, args), host=args.host, port=args.port
    )
    loop.run_until_complete(coro)

    # create the connection to the JMIF client
    if args.kardex_use_tls:
        if ssl_context is None:
            ssl_context = ssl.create_default_context()
    else:
        ssl_context = None
    coro = loop.create_connection(
        lambda: KardexClientProtocol(loop, queue, args),
        host=args.kardex_host,
        port=args.kardex_port,
        ssl=ssl_context,
    )
    transport, client = loop.run_until_complete(coro)
    loop.create_task(client.keepalive())
    loop.create_task(client.process_queue())
    loop.run_forever()
    loop.close()


def make_parser():
    listen_address = os.environ.get("INTERFACE", "0.0.0.0")
    listen_port = int(os.environ.get("PORT", "7654"))
    secret = os.environ.get("ODOO_CALLBACK_SECRET", "")
    odoo_url = os.environ.get("ODOO_URL", "http://localhost:8069")
    odoo_db = os.environ.get("ODOO_DB", "odoodb")
    kardex_host = os.environ.get("KARDEX_HOST", "kardex")
    kardex_port = int(os.environ.get("KARDEX_PORT", "9600"))
    kardex_use_tls = (
        False
        if os.environ.get("KARDEX_TLS", "") in ("", "0", "False", "FALSE")
        else True
    )
    parser = argparse.ArgumentParser()
    arguments = [
        ("--host", listen_address, str),
        ("--port", listen_port, int),
        ("--odoo-url", odoo_url, str),
        ("--odoo-db", odoo_db, str),
        ("--secret", secret, str),
        ("--kardex-host", kardex_host, str),
        ("--kardex-port", kardex_port, str),
        ("--kardex-use-tls", kardex_use_tls, bool),
    ]
    for name, default, type_ in arguments:
        parser.add_argument(name, default=default, action="store", type=type_)
    return parser


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args()
    main(args)
