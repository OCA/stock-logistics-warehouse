# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestLocationWarehouse(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestLocationWarehouse, self).setUp(*args, **kwargs)
        self.wh_sf = self.env.ref("stock.warehouse0")
        self.loc_sf = self.wh_sf.lot_stock_id
        self.wh2 = self.env["stock.warehouse"].create(
            {
                "name": "WH 2",
                "code": "WH3",
                "company_id": self.wh_sf.company_id.id,
                "partner_id": self.wh_sf.partner_id.id,
                "reception_steps": "one_step",
            }
        )
        self.loc_wh2 = self.wh2.lot_stock_id
        self.location1 = self.env["stock.location"].create(
            {"name": "sunblock_1", "location_id": self.loc_sf.id}
        )
        self.location2 = self.env["stock.location"].create(
            {"name": "sunblock_2", "location_id": self.location1.id}
        )
        self.location3 = self.env["stock.location"].create(
            {"name": "sunblock_3", "location_id": self.location2.id}
        )

    def test_main_location(self):
        self.assertEqual(self.loc_sf.warehouse_id, self.wh_sf)

    def test_compute_location(self):
        self.location1.location_id = self.loc_wh2
        self.assertEqual(self.location1.warehouse_id, self.wh2)

    def test_compute_location_childs(self):
        self.location1.location_id = self.loc_wh2
        self.assertEqual(self.location2.warehouse_id, self.wh2)
        self.assertEqual(self.location3.warehouse_id, self.wh2)
