# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProductCategory(models.Model):

    _inherit = 'product.category'

    property_inventory_revaluation_increase_account_categ = fields.Many2one(
        'account.account', string='Valuation Increase Account',
        company_dependent=True,
        help="Define the Financial Accounts to be used as the balancing "
             "account in the transaction created by the revaluation. "
             "The Valuation Increase Account is used when the inventory value "
             "is increased due to the revaluation.")

    property_inventory_revaluation_decrease_account_categ = fields.Many2one(
        'account.account', string='Valuation Decrease Account',
        company_dependent=True,
        help="Define the Financial Accounts to be used as the balancing "
             "account in the transaction created by the revaluation. "
             "The Valuation Decrease Account is used when the inventory value "
             "is decreased.")


class Product(models.Model):

    _inherit = 'product.product'

    @api.multi
    def do_change_standard_price(self, new_price):
        """Override standard method, as it was not suitable."""
        reval_model = self.env["stock.inventory.revaluation"]
        for product in self:
            increase_account_id = \
                product.categ_id.\
                property_inventory_revaluation_increase_account_categ.id \
                or False
            decrease_account_id = \
                product.categ_id.\
                property_inventory_revaluation_decrease_account_categ.id \
                or False

            reval = reval_model.create({
                'revaluation_type': 'price_change',
                'product_id': product.id,
                'new_cost': new_price,
                'increase_account_id': increase_account_id,
                'decrease_account_id': decrease_account_id
            })
            reval.button_post()
        return True
