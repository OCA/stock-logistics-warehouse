# Copyright 2020 Tecnativa - Ernesto Tejeda
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

import operator as py_operator

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}


class Product(models.Model):
    _inherit = "product.product"

    """ Based on free_qty field definition in product.product
        model in Odoo v13 'stock' module. It is necessary for
        the widget.
    """
    free_qty = fields.Float(
        'Free To Use Quantity ',
        compute='_compute_free_qty',
        search='_search_free_qty',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Forecast quantity (computed as Quantity On Hand "
             "- reserved quantity)\n"
             "In a context with a single Stock Location, this includes "
             "goods stored in this location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods stored in the Stock Location of this Warehouse, or any "
             "of its children.\n"
             "Otherwise, this includes goods stored in any Stock Location "
             "with 'internal' type.")

    def _search_free_qty(self, operator, value):
        """ Based on _search_product_quantity method of product.product
            model in Odoo v13 'stock' module.
        """
        if operator not in ('<', '>', '=', '!=', '<=', '>='):
            raise UserError(_('Invalid domain operator %s') % operator)
        if not isinstance(value, (float, int)):
            raise UserError(_('Invalid domain right operand %s') % value)
        ids = self.search([], order='id').filtered(
            lambda x: OPERATORS[operator](x.incoming_qty, value)).ids
        return [('id', 'in', ids)]

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    def _compute_free_qty(self):
        """ Based on _compute_quantities_dict method of product.product
            model in Odoo v13 'stock' module.
        """
        domain_quant_loc = self._get_domain_locations()[0]
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        lot_id = self._context.get('lot_id')
        if lot_id is not None:
            domain_quant += [('lot_id', '=', lot_id)]
        owner_id = self._context.get('owner_id')
        if owner_id is not None:
            domain_quant += [('owner_id', '=', owner_id)]
        package_id = self._context.get('package_id')
        if package_id is not None:
            domain_quant += [('package_id', '=', package_id)]
        quant_obj = self.env['stock.quant']
        quants = quant_obj.read_group(
            domain_quant, ['product_id', 'reserved_quantity'], ['product_id'],
            orderby='id')
        quants_res = dict((item['product_id'][0], item['reserved_quantity'])
                          for item in quants)
        for product in self:
            rounding = product.uom_id.rounding
            reserved_quantity = quants_res.get(product.id, 0.0)
            free_qty = product.qty_available - reserved_quantity
            product.free_qty = float_round(
                free_qty, precision_rounding=rounding)
