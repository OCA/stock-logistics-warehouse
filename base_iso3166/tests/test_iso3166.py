# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestBaseIso3166(common.TransactionCase):
    def test_iso_3166(self):
        country = self.env.ref("base.ad")
        self.assertEqual(country.code_alpha3, "AND")
        self.assertEqual(country.code_numeric, "020")

    def test_historic_countries(self):
        ussr = self.env["res.country"].create(
            {"code": "SU", "name": "USSR, Union of Soviet Socialist Republics"}
        )
        self.assertEqual(ussr.code_alpha3, "SUN")
        self.assertEqual(ussr.code_numeric, "810")
