from odoo.tests.common import TransactionCase


class TestUserRestriction(TransactionCase):

    def setUp(self):
        super(TestUserRestriction, self).setUp()
        self.stock_user = self.env['res.users'].create({
            'login': 'stock_user',
            'name': 'stock_user',
            'groups_id': [(6, 0, [self.env.ref('stock.group_stock_user').id])]
        })
        self.stock_user_assigned_type = self.env['res.users'].create({
            'login': 'stock_user_assigned_type',
            'name': 'stock_user_assigned_type',
            'groups_id': [(6, 0, [self.env.ref(
                'stock_picking_type_user_restriction.'
                'group_assigned_picking_types_user'
            ).id])]
        })
        self.picking_type_out = self.env.ref('stock.picking_type_out')
        self.picking_type_model = self.env['stock.picking.type']

    def test_access_picking_type(self):
        # assigned_user_ids is not set: both users can read
        pick_types = self.picking_type_model.sudo(self.stock_user.id).search([
            ('name', '=', 'Delivery Orders')])
        self.assertTrue(self.picking_type_out in pick_types)
        pick_types = self.picking_type_model.sudo(
            self.stock_user_assigned_type.id).search([
                ('name', '=', 'Delivery Orders')])
        self.assertTrue(self.picking_type_out in pick_types)

        self.picking_type_out.assigned_user_ids = [
            (6, 0, [self.stock_user_assigned_type.id])]
        # assigned_user_ids is set with stock_user_assigned_type: both users can read
        pick_types = self.picking_type_model.sudo(self.stock_user.id).search([
            ('name', '=', 'Delivery Orders')])
        self.assertTrue(self.picking_type_out in pick_types)
        pick_types = self.picking_type_model.sudo(
            self.stock_user_assigned_type.id).search([
                ('name', '=', 'Delivery Orders')])
        self.assertTrue(self.picking_type_out in pick_types)

        self.picking_type_out.assigned_user_ids = [
            (6, 0, [self.stock_user.id])]
        # assigned_user_ids is set with stock_user: only stock_user can read
        pick_types = self.picking_type_model.sudo(self.stock_user.id).search([
            ('name', '=', 'Delivery Orders')])
        self.assertTrue(self.picking_type_out in pick_types)
        pick_types = self.picking_type_model.sudo(
            self.stock_user_assigned_type.id).search([
                ('name', '=', 'Delivery Orders')])
        self.assertFalse(self.picking_type_out in pick_types)
