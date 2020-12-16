#!/usr/bin/python3
import argparse
import asyncio
import logging
import os
import random
import ssl
import sys
import time

import aiohttp  # pylint: disable=missing-manifest-dependency

_logger = logging.getLogger(__name__)


class KardexProxyProtocol(asyncio.Protocol):
    def __init__(self, queue, loop, args):
        _logger.info("Proxy: created")
        self.transport = None
        self.buffer = b""
        self.queue = queue
        self.loop = loop
        self.args = args

    def connection_made(self, transport):
        _logger.info("Proxy: incoming cnx made")
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
        if exc:
            _logger.error("Proxy: incoming cnx lost: %s", exc)
        else:
            _logger.info("Proxy: incoming cnx closed")
        self.transport = None
        self.buffer = b""


class ReconnectingTCPClientProtocol(asyncio.Protocol):
    # source: https://stackoverflow.com/a/49452683/1504003
    max_delay = 3600
    initial_delay = 1.0
    factor = 2.7182818284590451
    jitter = 0.119626565582
    max_retries = None

    def __init__(self, *args, loop=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self._args = args
        self._kwargs = kwargs
        self._retries = 0
        self._delay = self.initial_delay
        self._continue_trying = True
        self._call_handle = None
        self._connector = None

    def connection_lost(self, exc):
        if self._continue_trying:
            self.retry()

    def connection_failed(self, exc):
        if self._continue_trying:
            self.retry()

    def retry(self):
        if not self._continue_trying:
            return

        self._retries += 1
        if self.max_retries is not None and (self._retries > self.max_retries):
            self.stop_trying()
            return

        self._delay = min(self._delay * self.factor, self.max_delay)
        if self.jitter:
            self._delay = random.normalvariate(self._delay, self._delay * self.jitter)
        _logger.info("%s: will retry connection after %ss", self, self._delay)
        self._call_handle = self._loop.call_later(self._delay, self.connect)

    def connect(self):
        if self._connector is None:
            self._connector = self._loop.create_task(self._connect())

    async def _connect(self):
        try:
            await self._loop.create_connection(
                lambda: self, *self._args, **self._kwargs
            )
        except Exception as exc:
            self._loop.call_soon(self.connection_failed, exc)
        else:
            self._delay = self.initial_delay
            self._retries = 0
        finally:
            self._connector = None

    def stop_trying(self):
        if self._call_handle:
            self._call_handle.cancel()
            self._call_handle = None
        self._continue_trying = False
        if self._connector is not None:
            self._connector.cancel()
            self._connector = None


class KardexClientProtocol(ReconnectingTCPClientProtocol):

    max_delay = 15
    initial_delay = 0.5
    factor = 1.7182818284590451
    jitter = 0.119626565582
    # if we set a number of retries, after N failed
    # retries, it will stop the event loop and exit
    max_retries = None

    initial_keepalive_delay = 20
    keepalive_delay = 50

    def __init__(self, queue, args, loop, **kwargs):
        super().__init__(loop=loop, **kwargs)
        _logger.info("started kardex client")
        self.queue = queue
        self.transport = None
        self.buffer = b""
        self.args = args

    def connection_made(self, transport):
        self.transport = transport
        _logger.info("connected to kardex server %r", transport)

    async def keepalive(self):
        await asyncio.sleep(self.initial_keepalive_delay)
        while True:
            t = int(time.time())
            msg = "61|ping%d|SH1-1|0|0||||||||\r\n" % t
            await self.send_message(msg)
            await asyncio.sleep(self.keepalive_delay)

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
                self._loop.create_task(self.notify_odoo(msg))

    def connection_lost(self, exc):
        _logger.error("Kardex client: connection lost: %s", exc)
        super().connection_lost(exc)

    def connection_failed(self, exc):
        _logger.error("Kardex client: failed to open connection: %s", exc)
        super().connection_failed(exc)

    def stop_trying(self):
        super().stop_trying()
        self._loop.stop()

    async def notify_odoo(self, msg):
        url = self.args.odoo_url + "/vertical-lift"
        async with aiohttp.ClientSession() as session:
            params = {"answer": msg, "secret": self.args.secret}
            async with session.post(url, data=params) as resp:
                resp_text = await resp.text()
                _logger.info("Reponse from Odoo: %s %s", resp.status, resp_text)


def main(args, ssl_context=None):
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    loop = asyncio.get_event_loop()

    if args.debug:
        loop.set_debug(True)

    queue = asyncio.Queue(loop=loop)
    # create the main server
    coro = loop.create_server(
        lambda: KardexProxyProtocol(queue, loop, args),
        host=args.host,
        port=args.port,
    )
    loop.run_until_complete(coro)

    # create the connection to the JMIF client
    if args.kardex_use_tls:
        if ssl_context is None:
            ssl_context = ssl.create_default_context()
    else:
        ssl_context = None
    client = KardexClientProtocol(
        queue,
        args,
        loop,
        host=args.kardex_host,
        port=args.kardex_port,
        ssl=ssl_context,
    )
    client.connect()
    loop.create_task(client.keepalive())
    loop.create_task(client.process_queue())
    loop.run_forever()


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
        if os.environ.get("KARDEX_TLS", "") in ("", "0", "false", "False", "FALSE")
        else True
    )
    debug = (
        True if os.environ.get("DEBUG", "") in ("1", "true", "True", "TRUE") else False
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
        ("--debug", debug, bool),
    ]
    for name, default, type_ in arguments:
        parser.add_argument(name, default=default, action="store", type=type_)
    return parser


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args()
    res = main(args)
    sys.exit(res)
