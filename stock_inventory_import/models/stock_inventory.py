#
from openerp import models, fields, api, exceptions, _


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.model
    def _get_available_filters(self):
        res = super(StockInventory, self)._get_available_filters()
        res.append(('file', _('By File')))
        return res

    imported = fields.Boolean('Imported')
    import_lines = fields.One2many('stock.inventory.import.line',
                                   'inventory_id', string='Imported Lines')
    filter = fields.Selection(_get_available_filters,
                              string='Selection Filter',
                              required=True)

    @api.one
    def process_import_lines(self):
        """Process Inventory Load lines."""
        if not self.import_lines:
            raise exceptions.Warning(_("There must be one line at least to "
                                       "process"))
        inventory_line_obj = self.env['stock.inventory.line']
        stk_lot_obj = self.env['stock.production.lot']
        product_obj = self.env['product.product']
        for line in self.import_lines:
            if line.fail:
                if not line.product:
                    prod_lst = product_obj.search([('default_code', '=',
                                                    line.code)])
                    if prod_lst:
                        product = prod_lst[0]
                    else:
                        line.fail_reason = _('No product code found')
                    continue
                else:
                    product = line.product
                lot_id = None
                if line.lot:
                    lot_lst = stk_lot_obj.search([('name', '=', line.lot)])
                    if lot_lst:
                        lot_id = lot_lst[0].id
                    else:
                        lot = stk_lot_obj.create({'name': line.lot,
                                                  'product_id': product.id})
                        lot_id = lot.id
                inventory_line_obj.create({'product_id': product.id,
                                           'product_uom_id': product.uom_id.id,
                                           'product_qty': line.quantity,
                                           'inventory_id': self.id,
                                           'location_id': line.location_id.id,
                                           'prod_lot_id': lot_id})
                line.write({'fail': False, 'fail_reason': _('Processed')})
        return True
