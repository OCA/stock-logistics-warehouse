# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class KardexCase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kardex = cls.env.ref('stock_kardex.stock_kardex_demo_shuttle_1')
        cls.product_socks = cls.env.ref('stock_kardex.product_running_socks')
        cls.kardex_view = cls.env.ref('stock_kardex.stock_location_kardex')
        cls.tray_type_klein_8x = cls.env.ref(
            'stock_kardex.kardex_tray_type_klein_8x'
        )
        cls.tray_type_klein_32x = cls.env.ref(
            'stock_kardex.kardex_tray_type_klein_32x'
        )

    def _cell_for(self, tray, x=1, y=1):
        cell = self.env['stock.location'].search(
            [('location_id', '=', tray.id), ('posx', '=', x), ('posy', '=', y)]
        )
        self.assertEqual(
            len(cell),
            1,
            "Cell x{}y{} not found for {}".format(x, y, tray.name),
        )
        return cell

    def _update_quantity_in_cell(self, cell, product, quantity):
        self.env['stock.quant']._update_available_quantity(
            product, cell, quantity
        )
