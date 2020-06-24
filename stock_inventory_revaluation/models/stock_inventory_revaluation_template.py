# Copyright 2020 Matt Taylor

from odoo import api, fields, models, _


class StockInventoryRevaluationTemplate(models.Model):

    _name = 'stock.inventory.revaluation.template'
    _description = 'Inventory revaluation template'

    name = fields.Char(
        string='Name',
        required=True)

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        help="Select a journal for the accounting entry.  Leave blank to use"
             "the default journal for the product.")

    increase_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Increase Account',
        help="Define the G/L accounts to be used as the balancing account in "
             "the transaction created by the revaluation. The Increase "
             "Account is used when the inventory value is increased due to "
             "the revaluation.")

    decrease_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Decrease Account',
        help="Define the G/L accounts to be used as the balancing account in "
             "the transaction created by the revaluation. The Decrease "
             "Account is used when the inventory value is decreased.")

    revaluation_type = fields.Selection(
        selection=[
            ('price_change', 'Unit Price Change'),
            ('inventory_value', 'Total Value Change'),
        ],
        string="Revaluation Type",
        required=True,
        default='inventory_value',
        help="'Unit Price Change': Change the per-unit price of the product. "
             "Inventory value is recalculated according to the new price and "
             "available quantity.\n"
             "'Total Value Change': Change the total value of the inventory. "
             "Unit price is recalculated according to the new total value and "
             "available quantity.")

    remarks = fields.Text(
        string='Remarks',
        required=True,
        help="This text is copied to the notes on the journal entry.")

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)',
         'You cannot have two templates with the same name.'),
    ]

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (copy)") % self.name
        return super(StockInventoryRevaluationTemplate, self).copy(
            default=default)
