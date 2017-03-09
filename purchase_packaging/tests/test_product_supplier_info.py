# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import odoo.tests.common as common


class TestProductSupplierInfo(common.TransactionCase):

    def setUp(self):
        """ Create a packagings with uom product_uom_dozen on
            product_supplierinfo_1'product (uom is product_uom_unit)
        """
        super(TestProductSupplierInfo, self).setUp()
        self.product_supplier_info = self.env.ref(
            'product.product_supplierinfo_1')
        self.product_tmpl_id = self.product_supplier_info.product_tmpl_id
        self.product_supplier_info.product_tmpl_id.uom_po_id = self.env.ref(
            'product.product_uom_unit')
        self.product_packaging_dozen = self.env['product.packaging'].create(
            {'product_tmpl_id': self.product_tmpl_id.id,
             'uom_id': self.env.ref('product.product_uom_dozen').id,
             'name': 'Packaging Dozen'}
        )

    def test_supplierinfo_product_uom(self):
        """ Check product_uom of product_supplierinfo_30 is product_uom_unit
            Set packaging_id product_packaging_3 on product_supplierinfo_30
            Check product_uom of product_supplierinfo_30 is product_uom_dozen
        """
        self.assertEqual(self.product_supplier_info.product_uom.id,
                         self.env.ref('product.product_uom_unit').id)
        self.product_supplier_info.write(
            {'packaging_id': self.product_packaging_dozen.id})
        self.assertEqual(self.product_supplier_info.product_uom.id,
                         self.env.ref('product.product_uom_dozen').id)
