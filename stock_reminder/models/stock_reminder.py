# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, models, fields, exceptions, _
from openerp.addons import decimal_precision as dp
from openerp.tools import safe_eval


class StockReminder(models.Model):
    _name = 'stock.reminder'

    res_user_id = fields.Many2one(
        'res.users',
        string='User',
        help='User that will be notified',
        required=True
    )
    product_product_id = fields.Many2one(
        'product.product',
        string='Product',
        help='Product to be notified for.',
        required=True,
    )
    rule = fields.Selection(
        [
            ('<', 'Less Than'),
            ('<=', 'Less or Equal Than'),
            ('=', 'Equals'),
            ('>', 'Greater Than'),
            ('>=', 'Greater or Equal Than'),
        ],
        string='Rule',
        help='The rule that the quantity needs to satisfy',
        required=True,
    )
    quantity = fields.Float(
        required=True,
        digits_compute=dp.get_precision('Product Unit of Measure'),
    )

    @api.constrains('res_user_id')
    def _check_user(self):
        for rec in self:
            if self.env.user.has_group('stock.group_stock_user'):
                if rec.res_user_id != self.env.user:
                    raise exceptions.ValidationError(_(
                        'You can only set reminders for yourself.'))

    @api.model
    def create(self, vals):
        """ Make the user a follower of the product
        """
        res = super(StockReminder, self).create(vals)
        partner_id = self.env['res.users'].browse(
            vals.get('res_user_id')).partner_id
        self.env['product.product'].browse(
            vals['product_product_id']).write({
                'message_follower_ids': [(4, partner_id.id, False)],
            })
        return res

    @api.multi
    def write(self, vals):
        """ Make the user a follower of the product
        """
        res = super(StockReminder, self).write(vals)
        model_product_product = self.env['product.product']
        user_id = vals.get('res_user_id')
        product_id = model_product_product.browse(
            vals.get('product_product_id'))
        if user_id and product_id:
            model_product_product.browse(product_id).message_subscribe_users(
                user_ids=user_id)
        elif user_id:
            self.mapped('product_product_id').message_subscribe_users(
                user_ids=user_id)
        elif product_id:
            model_product_product.browse(product_id).message_subscribe_users(
                user_ids=self.mapped('res_user_id').ids)
        return res

    @api.model
    def _check_reminders(self):
        """
        Go through all the reminders and see if they evaluate to true.
        If yes go ahead and send reminders to the interested users.
        """
        for rec in self.search([]):
            qty_available = rec.product_product_id._product_available()[
                rec.product_product_id.id]['qty_available']
            result = safe_eval(
                ' '.join([
                    str(qty_available),
                    rec.rule,
                    str(rec.quantity),
                ])
            )
            if result:
                rec.product_product_id.message_post(
                    subject=_('Product Reminder'),
                    body=_('Product\'s %s quantity %s is %s %s') % (
                        rec.product_product_id.name,
                        str(qty_available),
                        # given rec.rule get the descriptive string
                        [x[1] for x in rec._fields[
                            'rule'].selection if x[0] == rec.rule][0],
                        str(rec.quantity),
                    ),
                    type='email',
                )
