# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError
from openerp import SUPERUSER_ID


class TestStockReminder(TransactionCase):

    post_install = True
    at_install = False

    def test_stock_reminder(self):
        """ The routine is the following:
        1) Create userA as simple stock user and verify their rights on
        reminder creation.
        2) Create userB as manager and verify their rights on reminder
        creation.
        3) Vefify that they are properly subscribed to the products
        4) Run the scheduler and see whether the notification is send
        """
        model_res_users = self.env['res.users']
        model_stock_reminder = self.env['stock.reminder']
        product_a = self.env['product.product'].create({'name': 'productA'})
        # 1)
        user_a = model_res_users.create({
            'login': 'userA@example.com',
            'email': 'userA@example.com',
            'password': 'hackerman',
            'name': 'user_a',
            'groups_id': [(6, False, self.env.ref(
                'stock.group_stock_user').ids)],
        })
        model_stock_reminder.sudo(user_a).create({
            'res_user_id': user_a.id,
            'product_product_id': product_a.id,
            'rule': '<',
            'quantity': 5,
        })
        with self.assertRaises(ValidationError):
            model_stock_reminder.sudo(user_a).create({
                'res_user_id': SUPERUSER_ID,
                'product_product_id': product_a.id,
                'rule': '<',
                'quantity': 5,
            })
        # 2)
        user_b = model_res_users.create({
            'login': 'userB@example.com',
            'email': 'userB@example.com',
            'password': 'hackerman',
            'name': 'user_b',
            'groups_id': [(6, False, self.env.ref(
                'stock.group_stock_manager').ids)],
        })
        model_stock_reminder.sudo(user_b).create({
            'res_user_id': user_b.id,
            'product_product_id': product_a.id,
            'rule': '<',
            'quantity': 5,
        })
        model_stock_reminder.sudo(user_b).create({
            'res_user_id': user_b.id,
            'product_product_id': product_a.id,
            'rule': '<',
            'quantity': 5,
        })
        # 3)
        self.assertTrue(user_a.partner_id in product_a.message_follower_ids)
        self.assertTrue(user_b.partner_id in product_a.message_follower_ids)
        # 4)

        def _mail_search():
            return self.env['mail.message'].search_count([
                ('subject', '=', 'Product Reminder')])
        self.assertFalse(_mail_search())
        model_stock_reminder._check_reminders()
        self.assertEquals(_mail_search(), 4)
