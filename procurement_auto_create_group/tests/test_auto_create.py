# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProcurementAutoCreateGroup(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestProcurementAutoCreateGroup, self).setUp(*args, **kwargs)
        self.po_model = self.env['procurement.order']
        self.pr_model = self.env['procurement.rule']
        self.product_12 = self.env.ref('product.product_product_12')
        # Needed to avoid the dependency with stock:
        if self.env.registry.models.get('stock.picking'):
            picking_type_id = self.env.ref('stock.picking_type_internal').id
        else:
            picking_type_id = False

        # Create rules:
        self.no_auto_create = self.pr_model.create({
            'name': 'rule without autocreate',
            'auto_create_group': False,
            'action': [],
            'picking_type_id': picking_type_id,
        })
        self.auto_create = self.pr_model.create({
            'name': 'rule with autocreate',
            'auto_create_group': True,
            'action': [],
            'picking_type_id': picking_type_id,
        })

    def test_auto_create_group(self):
        """Test auto creation of group."""
        proc1 = self.po_model.create({
            'name': 'proc01',
            'product_id': self.product_12.id,
            'product_qty': 1.0,
            'product_uom': self.product_12.uom_id.id,
            'rule_id': self.no_auto_create.id,
        })
        self.assertFalse(proc1.group_id,
                         "Procurement Group should not have been assigned.")
        proc2 = self.po_model.create({
            'name': 'proc02',
            'product_id': self.product_12.id,
            'product_qty': 1.0,
            'product_uom': self.product_12.uom_id.id,
            'rule_id': self.auto_create.id,
        })
        self.assertTrue(proc2.group_id,
                        "Procurement Group has not been assigned.")

    def test_onchange_method(self):
        """Test onchange method for procurement rule."""
        proc_rule = self.auto_create
        proc_rule.write({'group_propagation_option': 'none'})
        proc_rule._onchange_group_propagation_option()
        self.assertFalse(proc_rule.auto_create_group)
