# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import SavepointCase
import logging

_logger = logging.getLogger(__name__)


class TestSaleProductPack(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pack_dc = cls.env.ref(
            'product_pack.product_pack_cpu_detailed_components')
        cls.pack_dc.type = 'product'
        cls.pack_dc.pack_line_ids.mapped('product_id').write(
            {'type': 'product'})

    def test_compute_quantities_dict(self):
        location_id = self.env.ref('stock.stock_location_suppliers').id,
        location_dest_id = self.env.ref('stock.stock_location_stock').id,
        components = self.pack_dc.pack_line_ids.mapped('product_id')
        picking = self.env['stock.picking'].create({
            'partner_id': self.env.ref('base.res_partner_4').id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'move_lines': [
                (0, 0, {
                    'name': 'incoming_move_test_01',
                    'product_id': components[0].id,
                    'product_uom_qty': 5,
                    'product_uom': components[0].uom_id.id,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                }),
                (0, 0, {
                    'name': 'incoming_move_test_02',
                    'product_id': components[1].id,
                    'product_uom_qty': 7,
                    'product_uom': components[1].uom_id.id,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                }),
                (0, 0, {
                    'name': 'incoming_move_test_03',
                    'product_id': components[2].id,
                    'product_uom_qty': 10,
                    'product_uom': components[2].uom_id.id,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                }),
            ]
        })
        picking.action_confirm()
        self.assertEqual(self.pack_dc.virtual_available, 5)
        self.assertEqual(self.pack_dc.qty_available, 0)
        wizard_dict = picking.button_validate()
        wizard = self.env[wizard_dict['res_model']].browse(
            wizard_dict['res_id'])
        wizard.process()
        self.assertEqual(self.pack_dc.virtual_available, 5)
        self.assertEqual(self.pack_dc.qty_available, 5)
