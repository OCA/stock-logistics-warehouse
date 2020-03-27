# Copyright 2020 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from __future__ import division
from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    value = fields.Monetary(compute='_compute_value',
                            groups='stock.group_stock_manager')
    currency_id = fields.Many2one(related='product_id.currency_id',
                                  groups='stock.group_stock_manager')

    @api.depends('quantity')
    def _compute_value(self):
        """ For FIFO valuation, compute the current accounting valuation
        using the stock moves of the product with remaining value filled,
        the accounting valuation is computed to global level, and then will
        be divided for the quantity on hand.

        Then, the value obtained from the division is an average valuation
        of the product.

        That value will be multiplied by the quantity available in the quant.

        For standard and avg method, the standard price will be multiplied
        by the quantity available in the quant.
        """

        # Just take into account the quants with usage internal and
        # that belong to the company
        quants_to_evaluate = self.filtered(
            lambda qua: qua.location_id._should_be_valued() and not
            (qua.owner_id and qua.owner_id != qua.company_id.partner_id))

        product_ids = quants_to_evaluate.mapped('product_id')
        product_valuation = dict.fromkeys(product_ids._ids, 0.0)
        product_quantity = dict.fromkeys(product_ids._ids, 0.0)

        # Get the sum of remaining value and remaining qty of the stock moves
        # with the current product. The total by product is saved in a
        # dictionary that will be used to calculate the inventory value
        # by quant
        if product_ids:
            self.env.cr.execute("""SELECT product_id,
                                COALESCE(SUM(remaining_value),0)
                                FROM stock_move WHERE remaining_value > 0
                                and product_id IN %s group by product_id;""",
                                (tuple(product_ids._ids),))
            product_valuation.update(dict(self.env.cr.fetchall()))

            self.env.cr.execute("""SELECT product_id,
                                COALESCE(SUM(remaining_qty),0)
                                FROM stock_move WHERE remaining_value > 0
                                and product_id IN %s group by product_id;""",
                                (tuple(product_ids._ids),))
            product_quantity.update(dict(self.env.cr.fetchall()))

        # For standard and avg method, the move does not save accounting
        # information (remaining qty and remaining value). For this
        # case the standard price will be used
        for product in product_ids.filtered(lambda prod:
                                            prod.cost_method != 'fifo'):
            product_valuation[product.id] = product.standard_price

        for quant in quants_to_evaluate:
            prod = quant.product_id
            quant.value = 0.0

            # There is no average value for the standard method. Then, the
            # standard price is multiplied directly by the quantity in the
            # quant
            if prod.cost_method != 'fifo':
                quant.value = product_valuation[prod.id] * quant.quantity
                continue

            # In case of FIFO, the average value of the product in the
            # moves -> sum(total_valuation) / sum(qty_on_hand), will be
            # multiplied by quantity in the quant.
            if product_quantity[prod.id] > 0:
                quant.value = (product_valuation[prod.id] /
                               product_quantity[prod.id] * quant.quantity)

    @api.model
    def read_group(self, domain, fields, groupby,
                   offset=0, limit=None, orderby=False,
                   lazy=True):
        """ This override is done in order for the grouped
        list view to display the total value of
        the quants inside a location. This doesn't work
        out of the box because `value` is a computed
        field.
        """
        res = super(StockQuant, self).read_group(
            domain, fields, groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy)
        if 'value' not in fields:
            return res
        for group in res:
            if group.get('__domain'):
                quants = self.search(group['__domain'])
                group['value'] = sum(quant.value for quant in quants)
        return res
