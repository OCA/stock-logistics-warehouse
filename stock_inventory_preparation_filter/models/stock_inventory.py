# Copyright 2015 AvanzOSC - Oihane Crucelaegi
# Copyright 2015 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools.safe_eval import safe_eval


class StockInventoryEmptyLines(models.Model):
    _name = 'stock.inventory.line.empty'
    _description = 'Inventory Line Empty'

    product_code = fields.Char(
        string='Product Code',
        required=True,
    )
    product_qty = fields.Float(
        string='Quantity',
        required=True,
        default=1.0,
        digits=dp.get_precision('Product Unit of Measure'),
    )
    inventory_id = fields.Many2one(
        comodel_name='stock.inventory',
        string='Inventory',
        required=True,
        ondelete="cascade",
    )


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def _selection_filter(self):
        """This function will return the list of filters allowed according to
        the options checked in 'Settings/Warehouse'.

        :return: list of tuple
        """
        res_filters = super(StockInventory, self)._selection_filter()
        res_filters.append(('categories', _('Selected Categories')))
        res_filters.append(('products', _('Selected Products')))
        res_filters.append(('domain', _('Filtered Products')))
        for res_filter in res_filters:
            if res_filter[0] == 'lot':
                res_filters.append(('lots', _('Selected Lots')))
                break
        res_filters.append(('empty', _('Empty list')))
        return res_filters

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
    product_domain = fields.Char('Domain', default=[('name', 'ilike', '')])

    @api.model
    def _get_inventory_lines_values(self):
        self.ensure_one()
        vals = []
        product_obj = self.env['product.product']
        if self.filter in ('categories', 'products'):
            if self.filter == 'categories':
                products = product_obj.search([
                    ('product_tmpl_id.categ_id', 'in', self.categ_ids.ids)
                ])
            else:  # filter = 'products'
                products = self.product_ids
            inventory = self.new(self._convert_to_write(self.read()[0]))
            inventory.filter = 'product'
            for product in products:
                inventory.product_id = product
                vals += super(StockInventory,
                              inventory)._get_inventory_lines_values()
        elif self.filter == 'lots':
            inventory = self.new(self._convert_to_write(self.read()[0]))
            inventory.filter = 'lot'
            for lot in self.lot_ids:
                inventory.lot_id = lot
                vals += super(StockInventory,
                              inventory)._get_inventory_lines_values()
        elif self.filter == 'domain':
            domain = safe_eval(self.product_domain)
            products = self.env['product.product'].search(domain)
            inventory = self.new(self._convert_to_write(self.read()[0]))
            inventory.filter = 'product'
            for product in products:
                inventory.product_id = product
                vals += super(
                    StockInventory, inventory)._get_inventory_lines_values()
        elif self.filter == 'empty':
            tmp_lines = {}
            for line in self.empty_line_ids:
                tmp_lines.setdefault(line.product_code, 0)
                tmp_lines[line.product_code] += line.product_qty
            self.empty_line_ids.unlink()
            inventory = self.new(self._convert_to_write(self.read()[0]))
            inventory.filter = 'product'
            # HACK: Make sure location is preserved
            inventory.location_id = self.location_id
            for product_code in tmp_lines.keys():
                product = product_obj.search([
                    '|',
                    ('default_code', '=', product_code),
                    ('barcode', '=', product_code),
                ], limit=1)
                if not product:
                    continue
                inventory.product_id = product
                values = super(StockInventory,
                               inventory)._get_inventory_lines_values()
                if values:
                    values[0]['product_qty'] = tmp_lines[product_code]
                else:
                    vals += [{
                        'product_id': product.id,
                        'product_qty': tmp_lines[product_code],
                        'location_id': self.location_id.id,
                    }]
                vals += values
        else:
            vals = super()._get_inventory_lines_values()
        return vals
