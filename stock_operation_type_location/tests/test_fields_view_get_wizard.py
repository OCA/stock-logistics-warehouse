# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from lxml import etree


class TestOnchangeLocation(TransactionCase):
    def setUp(self, *args, **kwargs):
        result = super(TestOnchangeLocation, self).setUp(*args, **kwargs)
        self.obj_stock_picking = self.env['stock.picking']
        self.obj_picking_type = self.env['stock.picking.type']
        self.obj_stock_location = self.env['stock.location']
        self.obj_stock_move = self.env['stock.move']
        self.obj_res_partner = self.env['res.partner']
        self.obj_product = self.env['product.product']
        self.obj_ir_sequence = self.env['ir.sequence']
        self.wiz =\
            self.env['stock.transfer_details']

        self.wh_main = self.browse_ref('stock.warehouse0')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.loc01 = self.env.ref('stock.stock_location_3')
        self.loc02 = self.env.ref('stock.stock_location_4')
        self.dest_loc01 = self.env.ref('stock.stock_location_5')
        self.dest_loc02 = self.env.ref('stock.stock_location_7')

        return result

    def _prepare_picking_type_data(self):
        allowed_location_ids = [self.loc01.id, self.loc02.id]
        allowed_dest_location_ids = [self.dest_loc01.id, self.dest_loc02.id]

        sequence_id = self.obj_ir_sequence.create({
            'name': 'Sequence 1',
            'prefix': '/Test/',
            'padding': 5
        })

        data_picking_type = {
            'name': 'Picking Type',
            'warehouse_id': self.wh_main.id,
            'sequence_id': sequence_id.id,
            'code': 'incoming',
            'default_location_src_id': self.supplier_location.id,
            'default_location_dest_id': self.stock_location.id,
            'allowed_location_ids': [(6, 0, allowed_location_ids)],
            'allowed_dest_location_ids': [(6, 0, allowed_dest_location_ids)]
        }

        return data_picking_type

    def _create_picking_type(self):
        data = self._prepare_picking_type_data()
        picking_type = self.obj_picking_type.create(data)

        return picking_type

    def _prepare_picking_data(self, picking_type_id):
        partnerA = self.obj_res_partner.create({'name': 'Partner A'})

        data_picking = {
            'partner_id': partnerA.id,
            'picking_type_id': picking_type_id
        }

        return data_picking

    def _create_picking(self, picking_type_id):
        data = self._prepare_picking_data(picking_type_id)
        picking = self.obj_stock_picking.create(data)

        return picking

    def _prepare_move_data(self, picking_id, picking_type_id):
        productA = self.obj_product.create({'name': 'Product A'})

        data_move = {
            'name': productA.name,
            'product_id': productA.id,
            'product_uom_qty': 1,
            'product_uom': productA.uom_id.id,
            'picking_type_id': picking_type_id,
            'picking_id': picking_id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id
        }

        return data_move

    def _create_move(self, picking_id, picking_type_id):
        data = self._prepare_move_data(picking_id, picking_type_id)
        move = self.obj_stock_move.create(data)

        return move

    def test_fields_view_get(self):
        # Create stock picking type
        picking_type = self._create_picking_type()
        # Check create stock picking type
        self.assertIsNotNone(picking_type)
        # Create stock picking
        picking = self._create_picking(picking_type.id)
        # Check create stock picking
        self.assertIsNotNone(picking)
        # Create stock move
        move = self._create_move(picking.id, picking_type.id)
        # Check create stock move
        self.assertIsNotNone(move)

        # Get Data Location
        scr_id = picking_type.default_location_src_id.id
        dest_id = picking_type.default_location_dest_id.id
        allowed_location = picking_type.allowed_location_ids
        location_ids = [x.id for x in allowed_location]
        location_ids.append(scr_id)
        allowed_dest_location = picking_type.allowed_dest_location_ids
        dest_location_ids = [y.id for y in allowed_dest_location]
        dest_location_ids.append(dest_id)

        # Check Fields View Get
        active_ids = picking.id
        domain_destinationloc = []
        domain_sourceloc = []

        wiz_id = self.wiz.with_context(
            default_picking_type_id=picking_type.id,
            active_model="stock.picking",
            active_ids=[active_ids],).create({})

        view = wiz_id.fields_view_get()

        if 'item_ids' in view['fields']:
            arch = view['fields']['item_ids'][
                'views']['tree']['arch']
            doc = etree.XML(arch)
            for node in doc.xpath("//field[@name='destinationloc_id']"):
                domain_destinationloc = node.get('domain')
                self.assertEquals(
                    domain_destinationloc,
                    "[('id', 'in', %s)]" % dest_location_ids
                )
            for node in doc.xpath("//field[@name='sourceloc_id']"):
                domain_sourceloc = node.get('domain')
                self.assertEquals(
                    domain_sourceloc,
                    "[('id', 'in', %s)]" % location_ids
                )
        return True
