# Copyright 2020-2021 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests import SavepointCase


class StockHelperCommonCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.wh = cls.env.ref("stock.warehouse0")

        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.supplier_loc = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_loc = cls.wh.lot_stock_id
        cls.shelf1_loc = cls.env.ref("stock.stock_location_components")
        cls.shelf2_loc = cls.env.ref("stock.stock_location_14")
