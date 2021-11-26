# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
import unittest
from ..context import ContextVar

class TestContextVar(unittest.TestCase):

    def test_simple_set(self):
        ctx = ContextVar("test1")
        token = ctx.set("toto")
        self.assertIsNotNone(token)
        value = ctx.get()
        self.assertEqual("toto", value)
        ctx.reset(token)
        with self.assertRaises(LookupError):
            ctx.get()

    def test_default(self):
        ctx = ContextVar("test1", "default")
        self.assertEqual("default", ctx.get())
        token = ctx.set("toto")
        self.assertEqual("toto", ctx.get())
        ctx.reset(token)
        self.assertEqual("default", ctx.get())

    def test_nested(self):
        ctx = ContextVar("test1", "default")
        token1 = ctx.set("toto")
        token2 = ctx.set("toto2")
        self.assertEqual("toto2", ctx.get())
        ctx.reset(token2)
        self.assertEqual("toto", ctx.get())
        ctx.reset(token1)
        self.assertEqual("default", ctx.get())

    def test_nested_2(self):
        ctx = ContextVar("test1", "default")
        token1 = ctx.set("toto")
        token2 = ctx.set("toto2")
        self.assertEqual("toto2", ctx.get())
        ctx.reset(token1)
        self.assertEqual("default", ctx.get())
        ctx.reset(token2)
        self.assertEqual("toto", ctx.get())
