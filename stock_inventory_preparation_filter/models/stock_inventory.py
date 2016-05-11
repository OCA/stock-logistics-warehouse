# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api, _


class StockInventoryEmptyLines(models.Model):
    _name = 'stock.inventory.line.empty'

    product_code = fields.Char(
        string='Product Code', size=64, required=True)
    product_qty = fields.Float(
        string='Quantity', required=True, default=1.0)
    inventory_id = fields.Many2one(
        comodel_name='stock.inventory', string='Inventory',
        required=True, ondelete="cascade")


class StockInventoryFake(object):
    def __init__(self, inventory, product=None, lot=None):
        self.id = inventory.id
        self.location_id = inventory.location_id
        self.product_id = product
        self.lot_id = lot
        self.partner_id = inventory.partner_id
        self.package_id = inventory.package_id

    def default_value(self):
        value = {}
        value.update({
            'theoretical_qty': 0.0,
            'product_id': self.product_id.id,
            'location_id': self.location_id.id if self.location_id else False,
            'prod_lot_id': self.lot_id.id if self.lot_id else False,
            'inventory_id': self.id,
            'package_id': self.package_id.id if self.package_id else False,
            'product_qty': 0.0,
            'product_uom_id': self.product_id.uom_id.id,
            'partner_id': False
        })
        return [value]


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def _get_available_filters(self):
        """This function will return the list of filters allowed according to
        the options checked in 'Settings/Warehouse'.

        :return: list of tuple
        """
        res_filters = super(StockInventory, self)._get_available_filters()
        res_filters.append(('categories', _('Selected Categories')))
        res_filters.append(('products', _('Selected Products')))
        for res_filter in res_filters:
            if res_filter[0] == 'lot':
                res_filters.append(('lots', _('Selected Lots')))
        res_filters.append(('empty', _('Empty list')))
        return res_filters

    filter = fields.Selection(
        selection=_get_available_filters, string='Selection Filter',
        required=True)
    categ_ids = fields.Many2many(
        comodel_name='product.category', relation='rel_inventories_categories',
        column1='inventory_id', column2='category_id', string='Categories')
    product_ids = fields.Many2many(
        comodel_name='product.product', relation='rel_inventories_products',
        column1='inventory_id', column2='product_id', string='Products')
    lot_ids = fields.Many2many(
        comodel_name='stock.production.lot', relation='rel_inventories_lots',
        column1='inventory_id', column2='lot_id', string='Lots')
    empty_line_ids = fields.One2many(
        comodel_name='stock.inventory.line.empty', inverse_name='inventory_id',
        string='Capture Lines')
    import_products = fields.Selection(
        [('only_with_stock', 'Only With Stock'), ('all', 'All')],
        default='only_with_stock')

    @api.model
    def _get_inventory_lines(self, inventory):
        vals = []
        product_tmpl_obj = self.env['product.template']
        product_obj = self.env['product.product']

        if inventory.filter in ('categories', 'products'):
            products = product_obj
            if inventory.filter == 'categories':
                product_tmpls = product_tmpl_obj.search(
                    [('categ_id', 'in', inventory.categ_ids.ids)])
                products = product_obj.search(
                    [('product_tmpl_id', 'in', product_tmpls.ids)])
            elif inventory.filter == 'products':
                products = inventory.product_ids
            for product in products:
                fake_inventory = StockInventoryFake(inventory, product=product)
                value = super(StockInventory, self)._get_inventory_lines(
                    fake_inventory)
                if inventory.import_products == 'all' and not value:
                    value = fake_inventory.default_value()

                vals += value
        elif inventory.filter == 'lots':
            for lot in inventory.lot_ids:
                fake_inventory = StockInventoryFake(inventory, lot=lot)

                value = super(StockInventory, self)._get_inventory_lines(
                    fake_inventory)
                if inventory.import_products == 'all' and not value:
                    value = fake_inventory.default_value()

                vals += value
        elif inventory.filter == 'empty':
            tmp_lines = {}
            empty_line_obj = self.env['stock.inventory.line.empty']
            for line in inventory.empty_line_ids:
                if line.product_code in tmp_lines:
                    tmp_lines[line.product_code] += line.product_qty
                else:
                    tmp_lines[line.product_code] = line.product_qty
            inventory.empty_line_ids.unlink()
            for product_code in tmp_lines.keys():
                products = product_obj.search([
                    '|', ('default_code', '=', product_code),
                    ('ean13', '=', product_code),
                ])
                if products:
                    product = products[0]
                    fake_inventory = StockInventoryFake(
                        inventory, product=product)
                    values = super(StockInventory, self)._get_inventory_lines(
                        fake_inventory)
                    if values:
                        values[0]['product_qty'] = tmp_lines[product_code]
                    else:
                        empty_line_obj.create(
                            {
                                'product_code': product_code,
                                'product_qty': tmp_lines[product_code],
                                'inventory_id': inventory.id,
                            })
                    vals += values
        else:
            products = product_obj.search([])
            for product in products:
                fake_inventory = StockInventoryFake(inventory, product=product)
                value = super(StockInventory, self)._get_inventory_lines(
                    fake_inventory)
                if inventory.import_products == 'all' and not value:
                    value = fake_inventory.default_value()
                vals += value

        return vals
