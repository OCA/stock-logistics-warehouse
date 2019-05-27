# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockRule(models.Model):

    _inherit = 'stock.rule'

    propagate_product_packaging = fields.Boolean(
        default=True,
    )

    def _get_stock_move_values(
            self, product_id, product_qty, product_uom, location_id, name,
            origin, values, group_id):
        """
        If stock rule has propagate_product_packaging enabled, update
        stock move with it.
        :param product_id:
        :param product_qty:
        :param product_uom:
        :param location_id:
        :param name:
        :param origin:
        :param values:
        :param group_id:
        :return:
        """
        res = super()._get_stock_move_values(
            product_id, product_qty, product_uom, location_id, name, origin,
            values, group_id)
        if 'product_packaging' in values:
            res.update({
                'product_packaging': values.get('product_packaging')
            })
        return res
