# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import odoo.tests.common as common


class TestProductPackaging(common.TransactionCase):

    def setUp(self):
        super(TestProductPackaging, self).setUp()
        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.uom_dozen = self.env.ref('product.product_uom_dozen')
        self.product_tmpl_dozen = self.env[
            'product.template'].new(
            {'uom_id': self.uom_dozen})
        self.product_tmpl_unit = self.env[
            'product.template'].new(
            {'uom_id': self.uom_unit})

    def test_compute_quantity_by_package(self):
        """ Create a packagings with uom product_uom_dozen on
                * product_tmpl_dozen (uom is product_uom_dozen)
                * product_tmpl_unit (uom is product_uom_unit)
            Result should be :
                * product_tmpl_dozen -> qty by package : 1
                * product_tmpl_unit -> qty by package : 12
            Create product_uom_24
            Update product_tmpl_dozen to set this new uom
            Result should be :
                * product_tmpl_dozen -> qty by package : 0.5
            Update product_package_unit to set this new uom
            Result should be :
                * product_packaging_unit -> qty by package : 24
            Create product_uom 6
            Update product_tmpl_dozen to set this new uom
            Result should be :
                * product_packaging_dozen -> qty by package : 2
            Update product_packaging_unit to set this new uom
            Result should be :
                * product_packaging_unit -> qty by package : 6
        """

        packaging_obj = self.env['product.packaging']
        product_packaging_dozen = packaging_obj.new(
            {'product_tmpl_id': self.product_tmpl_dozen,
             'uom_id': self.uom_dozen})
        self.assertAlmostEqual(product_packaging_dozen.qty, 1)
        product_packaging_unit = packaging_obj.new(
            {'product_tmpl_id': self.product_tmpl_unit,
             'uom_id': self.uom_dozen})
        self.assertAlmostEqual(product_packaging_unit.qty, 12)
        product_uom_24 = self.env['product.uom'].create(
            {'category_id': self.env.ref('product.product_uom_categ_unit').id,
             'name': 'Double Dozens',
             'factor_inv': 24,
             'uom_type': 'bigger'
             })
        self.product_tmpl_dozen.uom_id = product_uom_24
        self.assertAlmostEqual(product_packaging_dozen.qty, 0.5)
        product_packaging_unit.uom_id = product_uom_24
        self.assertAlmostEqual(product_packaging_unit.qty, 24)
        product_uom_6 = self.env['product.uom'].create(
            {'category_id': self.env.ref('product.product_uom_categ_unit').id,
             'name': 'Demi Dozens',
             'factor_inv': 6,
             'uom_type': 'bigger'
             })
        self.product_tmpl_dozen.uom_id = product_uom_6
        self.assertAlmostEqual(product_packaging_dozen.qty, 2)
        product_packaging_unit.uom_id = product_uom_6
        self.assertAlmostEqual(product_packaging_unit.qty, 6)
