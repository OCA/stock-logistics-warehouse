# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ProductCategory(models.Model):

    _inherit = 'product.category'

    property_inventory_revaluation_increase_account_categ = fields.Many2one(
        'account.account', string='Valuation Increase Account',
        company_dependent=True,
        help="Define the G/L accounts to be used as the balancing account in "
             "the transaction created by the revaluation. The G/L Increase "
             "Account is used when the inventory value is increased due to "
             "the revaluation.")

    property_inventory_revaluation_decrease_account_categ = fields.Many2one(
        'account.account', string='Valuation Decrease Account',
        company_dependent=True,
        help="Define the G/L accounts to be used as the balancing account in "
             "the transaction created by the revaluation. The G/L Decrease "
             "Account is used when the inventory value is decreased.")
