# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 - Present Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.tests import common
from openerp.osv.orm import except_orm


class TestRetainedStock(common.TransactionCase):

    def setUp(self):
        super(TestRetainedStock, self).setUp()

        self.prodlot_model = self.registry('stock.production.lot')
        self.stock_move_model = self.registry('stock.move')
        self.location_model = self.registry("stock.location")

    def create_lot(self, vals):
        return self.prodlot_model.create(self.cr, self.uid, vals)

    def create_move(self, vals):
        return self.stock_move_model.create(self.cr, self.uid, vals)

    def create_location(self, vals):
        return self.location_model.create(self.cr, self.uid, vals)

    def test_retained_stock_constraint(self):
        lot_id = self.create_lot({
            "name": "Monitors",
            "product_id": self.ref("product.product_product_6"),
            "retained_stock": 10
        })

        self.assertNotEqual(lot_id, 0)

        lot_id = self.create_lot({
            "name": "Monitors",
            "product_id": self.ref("product.product_product_6"),
            "retained_stock": 0
        })

        self.assertNotEqual(lot_id, 0)

        with self.assertRaises(except_orm):
            self.create_lot({
                "name": "Monitors 2",
                "product_id": self.ref("product.product_product_6"),
                "retained_stock": -1
            })

    def test_retained_stock_calculated(self):
        from_location_id = self.create_location({
            "name": "StockSupplier",
            "usage": "inventory",
        })

        location_id = self.create_location({
            "name": "Stock",
            "usage": "internal",
        })

        lot_id = self.create_lot({
            "name": "Monitors",
            "product_id": self.ref("product.product_product_6"),
            "retained_stock": 10,
            "location_id": location_id,
        })

        self.create_move({
            "name": "move_name",
            "product_id": self.ref("product.product_product_6"),
            "product_uom": self.ref("product.product_uom_kgm"),
            "product_qty": 50,
            "location_id": from_location_id,
            "location_dest_id": location_id,
            "prodlot_id": lot_id,
            "state": "done",
        })

        prodlot = self.prodlot_model.browse(self.cr, self.uid, lot_id)
        self.assertEqual(prodlot.stock_available, 40)

        prodlot.write({"retained_stock": 40})
        prodlot.refresh()
        self.assertEqual(prodlot.stock_available, 10)

        prodlot.write({"retained_stock": 0})
        prodlot.refresh()
        self.assertEqual(prodlot.stock_available, 50)
