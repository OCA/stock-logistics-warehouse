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
        cls.tray_type_small_8x = cls.env.ref(
            'stock_kardex.kardex_tray_type_small_8x'
        )
        cls.tray_type_small_32x = cls.env.ref(
            'stock_kardex.kardex_tray_type_small_32x'
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

    @classmethod
    def _create_simple_picking_out(cls, product, quantity):
        stock_loc = cls.env.ref('stock.stock_location_stock')
        customer_loc = cls.env.ref('stock.stock_location_customers')
        picking_type = cls.env.ref('stock.picking_type_out')
        partner = cls.env.ref('base.res_partner_1')
        return cls.env['stock.picking'].create(
            {
                'picking_type_id': picking_type.id,
                'partner_id': partner.id,
                'location_id': stock_loc.id,
                'location_dest_id': customer_loc.id,
                'move_lines': [
                    (
                        0,
                        0,
                        {
                            'name': product.name,
                            'product_id': product.id,
                            'product_uom': product.uom_id.id,
                            'product_uom_qty': quantity,
                            'picking_type_id': picking_type.id,
                            'location_id': stock_loc.id,
                            'location_dest_id': customer_loc.id,
                        },
                    )
                ],
            }
        )
