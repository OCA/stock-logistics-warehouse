# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields
from odoo.tests import RecordCapturer

from odoo.addons.base.tests.common import BaseCommon


class CommonOutPull(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "TEST", "code": "TEST"}
        )
        cls.customers_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {"name": "TEST", "is_storable": True}
        )
        # Put some stock
        cls.env["stock.quant"]._update_available_quantity(
            cls.product,
            cls.warehouse.lot_stock_id,
            10,
        )

    def _run_procurement(self, product, qty):
        uom = product.uom_id
        proc_qty, proc_uom = uom._adjust_uom_quantities(qty, product.uom_id)
        today = fields.Date.today()
        values = {
            "date_planned": today,
            "date_deadline": today,
            "warehouse_id": self.warehouse or False,
            "company_id": self.company,
        }
        procurement = self.env["stock.rule"].Procurement(
            product,
            proc_qty,
            proc_uom,
            self.customers_location,
            product.name,
            "PROC TEST",
            self.company,
            values,
        )
        with RecordCapturer(self.env["stock.move"]) as capt:
            self.env["stock.rule"].run([procurement])
        return capt.records

    def _validate_picking(self, picking):
        picking.move_line_ids.write({"picked": True})
        picking._action_done()
