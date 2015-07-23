# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp.tests.common as common


class TestPackaging(common.TransactionCase):

    def setUp(self):
        super(TestPackaging, self).setUp()

    def test_compute_quantity_by_package(self):
        """ Create a packagings with uom  product_uom_dozen on
                * product_product_35 (uom is product_uom_dozen)
                * product_product_34 (uom is product_uom_unit)
            Result should be :
                * product_product_35 -> qty by package : 1
                * product_product_34 -> qty by package : 12
            Create product_uom_24
            Update product_product_35 to set this new uom
            Result should be :
                * product_product_35 -> qty by package : 0.5
            Update product_package_34 to set this new uom
            Result should be :
                * product_product_34 -> qty by package : 24
            Create product_uom 6
            Update product_product_35 to set this new uom
            Result should be :
                * product_product_35 -> qty by package : 2
            Update product_package_34 to set this new uom
            Result should be :
                * product_product_34 -> qty by package : 6
        """
        packaging_obj = self.env['product.packaging']
        product_packaging_35 = packaging_obj.create(
            {'product_tmpl_id': self.env.ref('product.product_product_35'
                                             ).product_tmpl_id.id,
             'uom_id': self.env.ref('product.product_uom_dozen').id})
        self.assertAlmostEqual(product_packaging_35.qty, 1)
        product_packaging_34 = packaging_obj.create(
            {'product_tmpl_id': self.env.ref('product.product_product_34'
                                             ).product_tmpl_id.id,
             'uom_id': self.env.ref('product.product_uom_dozen').id})
        self.assertAlmostEqual(product_packaging_34.qty, 12)
        product_uom_24 = self.env['product.uom'].create(
            {'category_id': self.env.ref('product.product_uom_categ_unit').id,
             'name': 'Double Dozens',
             'factor_inv': 24,
             'uom_type': 'bigger'
             })
        self.env.ref('product.product_product_35').uom_id = product_uom_24
        self.assertAlmostEqual(product_packaging_35.qty, 0.5)
        product_packaging_34.uom_id = product_uom_24
        self.assertAlmostEqual(product_packaging_34.qty, 24)
        product_uom_6 = self.env['product.uom'].create(
            {'category_id': self.env.ref('product.product_uom_categ_unit').id,
             'name': 'Demi Dozens',
             'factor_inv': 6,
             'uom_type': 'bigger'
             })
        self.env.ref('product.product_product_35').uom_id = product_uom_6
        self.assertAlmostEqual(product_packaging_35.qty, 2)
        product_packaging_34.uom_id = product_uom_6
        self.assertAlmostEqual(product_packaging_34.qty, 6)
