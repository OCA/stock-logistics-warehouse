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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class StockInventoryEmptyLines(orm.Model):
    _name = 'stock.inventory.line.empty'

    _columns = {
        'product_code': fields.char('Product Code', size=64, required=True),
        'product_qty': fields.float('Quantity', required=True),
        'inventory_id': fields.many2one('stock.inventory', 'Inventory',
                                        required=True, ondelete="cascade"),
    }

    _defaults = {
        'product_qty': 1.0,
    }


class StockInventoryFake(object):
    def __init__(self, inventory, product=None, lot=None):
        self.id = inventory.id
        self.location_id = inventory.location_id
        self.product_id = product
        self.lot_id = lot
        self.partner_id = inventory.partner_id
        self.package_id = inventory.package_id


class StockInventory(orm.Model):
    _inherit = 'stock.inventory'

    def _get_available_filters(self, cr, uid, context=None):
        """This function will return the list of filter allowed according to
        the options checked in 'Settings/Warehouse'.

        :return: list of tuple
        """
        res_filters = super(StockInventory, self)._get_available_filters(
            cr, uid, context=context)
        res_filters.append(('categories', _('Selected Categories')))
        res_filters.append(('products', _('Selected Products')))
        for res_filter in res_filters:
            if res_filter[0] == 'lot':
                res_filters.append(('lots', _('Selected Lots')))
        res_filters.append(('empty', _('Empty list')))
        return res_filters

    _columns = {
        'filter': fields.selection(_get_available_filters, 'Selection Filter',
                                   required=True),
        'categ_ids': fields.many2many('product.category',
                                      'rel_inventories_categories',
                                      'inventory_id', 'category_id',
                                      'Categories'),
        'product_ids': fields.many2many('product.product',
                                        'rel_inventories_products',
                                        'inventory_id', 'product_id',
                                        'Products'),
        'lot_ids': fields.many2many('stock.production.lot',
                                    'rel_inventories_lots', 'inventory_id',
                                    'lot_id', 'Lots'),
        'empty_line_ids': fields.one2many('stock.inventory.line.empty',
                                          'inventory_id', 'Capture Lines'),
    }

    def _get_inventory_lines(self, cr, uid, inventory, context=None):
        vals = []
        product_tmpl_obj = self.pool['product.template']
        product_obj = self.pool['product.product']
        if inventory.filter in ('categories', 'products'):
            product_ids = []
            if inventory.filter == 'categories':
                product_tmpl_ids = product_tmpl_obj.search(
                    cr, uid, [('categ_id', 'in', inventory.categ_ids.ids)],
                    context=context)
                product_ids = product_obj.search(
                    cr, uid, [('product_tmpl_id', 'in', product_tmpl_ids)],
                    context=context)
            elif inventory.filter == 'products':
                product_ids = inventory.product_ids.ids
            for product in product_obj.browse(cr, uid, product_ids,
                                              context=context):
                fake_inventory = StockInventoryFake(inventory, product=product)
                vals += super(StockInventory, self)._get_inventory_lines(
                    cr, uid, fake_inventory, context=context)
        elif inventory.filter == 'lots':
            for lot in inventory.lot_ids:
                fake_inventory = StockInventoryFake(inventory, lot=lot)
                vals += super(StockInventory, self)._get_inventory_lines(
                    cr, uid, fake_inventory, context=context)
        elif inventory.filter == 'empty':
            values = []
            tmp_lines = {}
            empty_line_obj = self.pool['stock.inventory.line.empty']
            for line in inventory.empty_line_ids:
                if line.product_code in tmp_lines:
                    tmp_lines[line.product_code] += line.product_qty
                else:
                    tmp_lines[line.product_code] = line.product_qty
            empty_line_obj.unlink(cr, uid, inventory.empty_line_ids.ids,
                                  context=context)
            for product_code in tmp_lines.keys():
                product_ids = product_obj.search(
                    cr, uid, [('default_code', '=', product_code)],
                    context=context)
                if product_ids:
                    product = product_obj.browse(cr, uid, product_ids[0],
                                                 context=context)
                    fake_inventory = StockInventoryFake(inventory,
                                                        product=product)
                    values = super(StockInventory, self)._get_inventory_lines(
                        cr, uid, fake_inventory, context=context)
                    if values:
                        values[0]['product_qty'] = tmp_lines[product_code]
                    else:
                        empty_line_obj.create(
                            cr, uid, {
                                'product_code': product_code,
                                'product_qty': tmp_lines[product_code],
                                'inventory_id': inventory.id,
                            }, context=context)
                    vals += values
        else:
            vals = super(StockInventory, self)._get_inventory_lines(
                cr, uid, inventory, context=context)
        return vals
