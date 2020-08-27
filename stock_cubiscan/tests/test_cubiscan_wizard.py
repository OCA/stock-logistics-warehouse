# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from cubiscan.cubiscan import CubiScan
from mock import patch

from odoo.tests.common import SavepointCase


class TestCubiscanWizard(SavepointCase):
    @staticmethod
    def get_measure_result(length, width, height, weight):
        return {
            "origin": "1",
            "location": "dev001",
            "length": (length, None),
            "width": (width, None),
            "height": (height, None),
            "space_metric": True,
            "weight": (weight, None),
            "dim_weight": (weight, None),
            "weight_metric": True,
            "factor": 1,
            "intl_unit": True,
        }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.device_obj = cls.env["cubiscan.device"]
        cls.cs_wizard = cls.env["cubiscan.wizard"]
        PackType = cls.env["product.packaging.type"]
        pack_type_data = [
            ("internal", 3, 1, 0),
            ("retail", 10, 1, 1),
            ("transport", 20, 1, 1),
            ("pallet", 30, 1, 1),
        ]
        for name, seq, gtin, req in pack_type_data:
            PackType.create(
                {
                    "name": name,
                    "code": name.upper(),
                    "sequence": seq,
                    "has_gtin": gtin,
                    "required": req,
                }
            )

        cls.device = cls.device_obj.create(
            {
                "name": "Test Device",
                "device_address": "192.168.21.42",
                "port": 4242,
                "state": "ready",
            }
        )

        cls.wizard = cls.cs_wizard.create({"device_id": cls.device.id})

        cls.product_1 = cls.env.ref("product.product_product_6")
        cls.product_2 = cls.env.ref("product.product_product_7")

        cls.product_1.barcode = "424242"
        PackType.cron_check_create_required_packaging()

    def test_product_onchange(self):
        self.wizard.product_id = self.product_1.id

        self.assertEqual(len(self.wizard.line_ids), 0)
        self.wizard.onchange_product_id()
        self.assertEqual(len(self.wizard.line_ids), 6)

    def test_product_onchange_barcode(self):
        self.assertFalse(self.wizard.product_id)
        self.assertFalse(self.wizard.line_ids)

        self.wizard.on_barcode_scanned("424242")

        self.assertEqual(self.wizard.product_id, self.product_1)
        self.assertEqual(len(self.wizard.line_ids), 6)

    def test_cubiscan_measures(self):
        self.wizard.product_id = self.product_1.id
        self.wizard.onchange_product_id()

        with patch.object(CubiScan, "_make_request") as request:
            for idx, line in enumerate(self.wizard.line_ids):
                request.return_value = TestCubiscanWizard.get_measure_result(
                    2 ** idx, 1, 1, 2 ** idx
                )
                line.cubiscan_measure()
                self.assertEqual(
                    line.read(["lngth", "width", "height", "max_weight", "volume"])[0],
                    {
                        "id": line.id,
                        "lngth": (2 ** idx) * 1000,
                        "width": 1000,
                        "height": 1000,
                        "max_weight": 2.0 ** idx,
                        "volume": 2.0 ** idx,
                    },
                )

        self.wizard.action_save()
        mm_uom = self.env.ref("stock_cubiscan.product_uom_mm")
        self.assertEqual(
            self.product_1.read(
                [
                    "product_length",
                    "product_width",
                    "product_height",
                    "weight",
                    "volume",
                    "dimensional_uom_id",
                ]
            )[0],
            {
                "id": self.product_1.id,
                "product_length": 1000,
                "product_width": 1000,
                "product_height": 1000,
                "weight": 1.0,
                "volume": 1.0,
                "dimensional_uom_id": (mm_uom.id, mm_uom.name),
            },
        )
        packagings = self.product_1.packaging_ids.sorted()
        self.assertEqual(len(packagings), 5)
        for idx, packaging in enumerate(packagings, 1):
            self.assertEqual(
                packaging.read(["lngth", "width", "height", "max_weight", "volume"])[0],
                {
                    "id": packaging.id,
                    "lngth": (2 ** idx) * 1000,
                    "width": 1000,
                    "height": 1000,
                    "max_weight": 2.0 ** idx,
                    "volume": 2.0 ** idx,
                },
            )
