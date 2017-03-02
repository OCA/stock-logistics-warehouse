# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests import common
from openerp.exceptions import ValidationError
from openerp.exceptions import AccessError


class TestStockCycleCount(common.TransactionCase):

    def setUp(self):
        super(TestStockCycleCount, self).setUp()
        self.res_users_model = self.env['res.users']
        self.stock_cycle_count_model = self.env['stock.cycle.count']
        self.stock_cycle_count_rule_model = self.env['stock.cycle.count.rule']
        self.stock_inventory_model = self.env['stock.inventory']
        self.stock_location_model = self.env['stock.location']
        self.stock_move_model = self.env['stock.move']
        self.stock_warehouse_model = self.env['stock.warehouse']

        self.company = self.env.ref('base.main_company')
        self.partner = self.env.ref('base.res_partner_1')
        self.g_stock_manager = self.env.ref('stock.group_stock_manager')
        self.g_stock_user = self.env.ref('stock.group_stock_user')

        self.stock_location1 = self.stock_location_model.create(
            {'name': 'Place', 'usage': 'production'})

        self.big_wh = self.stock_warehouse_model.create(
            {'name': 'BIG', 'code': 'B'})
        self.small_wh = self.stock_warehouse_model.create(
            {'name': 'SMALL', 'code': 'S'})

        self.user1 = self._create_user('user_1',
                                       [self.g_stock_manager],
                                       self.company)
        self.user2 = self._create_user('user_2',
                                       [self.g_stock_user],
                                       self.company)

        # rule 1: periodic rule filled
        self.stock_cycle_count_rule1 = \
            self._create_stock_cycle_count_rule_periodic(
                self.user1.id, 'rule_1', [2, 7])

        # rule 2: turnover rule filled
        self.stock_cycle_count_rule2 = \
            self._create_stock_cycle_count_rule_turnover(
                self.user1.id, 'rule_2', [100])

        # rule 3: accuracy rule filled
        self.stock_cycle_count_rule3 = \
            self._create_stock_cycle_count_rule_accuracy(
                self.user1.id, 'rule_3', [5])

        # rule 4: zero rule filled
        self.stock_cycle_count_rule4 = \
            self._create_stock_cycle_count_rule_zero(
                self.user1.id, 'rule_4')

        self.stock_cycle_count1 = self._create_stock_cycle_count(
            self.user1.id, 'cycle_count_1', self.stock_cycle_count_rule1,
            self.stock_location1)

        self.stock_cycle_count1.action_create_inventory_adjustment()
        self.stock_cycle_count1.action_view_inventory()

        self.inventory1 = self.stock_inventory_model.search([
                ('cycle_count_id', '=', self.stock_cycle_count1.id)])
        self.inventory1.prepare_inventory()

        self.inventory1.action_done()

        self.stock_cycle_count2 = self._create_stock_cycle_count(
            self.user1.id, 'cycle_count_2', self.stock_cycle_count_rule1,
            self.stock_location1)
        self.stock_cycle_count2.do_cancel()

        self.big_wh.zero_confirmation_disabled = 1

    def _create_user(self, login, groups, company):
        """Creates a user."""
        group_ids = [group.id for group in groups]
        user = self.res_users_model.create({
            'name': login,
            'login': login,
            'password': 'demo',
            'email': 'example@yourcompany.com',
            'company_id': company.id,
            'company_ids': [(4, company.id)],
            'groups_id': [(6, 0, group_ids)]
        })
        return user

    def _create_stock_cycle_count_rule_periodic(self, uid, name, values):
        """Creates a Cycle Count rule of periodic type."""
        rule = self.stock_cycle_count_rule_model.sudo(uid).create({
            'name': name,
            'rule_type': 'periodic',
            'periodic_qty_per_period': values[0],
            'periodic_count_period': values[1],
        })
        return rule

    def _create_stock_cycle_count_rule_turnover(self, uid, name, values):
        """Creates a Cycle Count rule of turnover type."""
        rule = self.stock_cycle_count_rule_model.sudo(uid).create({
            'name': name,
            'rule_type': 'turnover',
            'turnover_inventory_value_threshold': values[0],
        })
        return rule

    def _create_stock_cycle_count_rule_accuracy(self, uid, name, values):
        """Creates a Cycle Count rule of accuracy type."""
        rule = self.stock_cycle_count_rule_model.sudo(uid).create({
            'name': name,
            'rule_type': 'accuracy',
            'accuracy_threshold': values[0],
        })
        return rule

    def _create_stock_cycle_count_rule_zero(self, uid, name):
        """Creates a Cycle Count rule of zero type."""
        rule = self.stock_cycle_count_rule_model.sudo(uid).create({
            'name': name,
            'rule_type': 'zero',
        })
        return rule

    def _create_stock_cycle_count(self, uid, name, rule, location):
        """Creates a Cycle Count."""
        rule = self.stock_cycle_count_model.sudo(uid).create({
            'name': name,
            'cycle_count_rule_id': rule.id,
            'location_id': location.id,
        })
        return rule

    def test_user_security(self):
        with self.assertRaises(AccessError):
            self.stock_cycle_count_rule1b = \
                self._create_stock_cycle_count_rule_periodic(
                    self.user2.id, 'rule_1b', [2, 7])
        with self.assertRaises(AccessError):
            self.stock_cycle_count1.sudo(self.user2.id).unlink()

    def test_rule_periodic(self):
        # constrain: periodic_qty_per_period < 1
        with self.assertRaises(ValidationError):
            self.stock_cycle_count_rule0 = \
                self._create_stock_cycle_count_rule_periodic(
                    self.user1.id, 'rule_0', [0, 0])
        # constrain: periodic_count_period < 0
        with self.assertRaises(ValidationError):
            self.stock_cycle_count_rule0 = \
                self._create_stock_cycle_count_rule_periodic(
                    self.user1.id, 'rule_0', [1, -1])

    def test_rule_zero(self):
        # constrain: can only have one zero confirmation rule per warehouse
        with self.assertRaises(ValidationError):
            self.stock_cycle_count_rule5 = \
                self._create_stock_cycle_count_rule_zero(
                    self.user1.id, 'rule_5')
        # constrain: can only have one warehouse assigned
        self.stock_cycle_count_rule4.warehouse_ids = [(4, self.big_wh.id)]
        with self.assertRaises(ValidationError):
            self.stock_cycle_count_rule4.warehouse_ids = [(4, self.small_wh.id)]
