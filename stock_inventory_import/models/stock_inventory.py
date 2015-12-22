# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, exceptions, _


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.model
    def _get_available_filters(self):
        res = super(StockInventory, self)._get_available_filters()
        res.append(('file', _('By File')))
        return res

    @api.multi
    @api.depends('import_lines')
    def _file_lines_processed(self):
        for record in self:
            processed = True
            if record.import_lines:
                processed = any((not line.fail or
                                 (line.fail and
                                  line.fail_reason != _('No processed')))
                                for line in record.import_lines)
            record.processed = processed

    imported = fields.Boolean('Imported')
    import_lines = fields.One2many('stock.inventory.import.line',
                                   'inventory_id', string='Imported Lines')
    filter = fields.Selection(_get_available_filters,
                              string='Selection Filter',
                              required=True)
    processed = fields.Boolean(string='Has been processed at least once?',
                               compute='_file_lines_processed')

    @api.multi
    def process_import_lines(self):
        """Process Inventory Load lines."""
        import_lines = self.mapped('import_lines')
        if not import_lines:
            raise exceptions.Warning(_("There must be one line at least to "
                                       "process"))
        inventory_line_obj = self.env['stock.inventory.line']
        stk_lot_obj = self.env['stock.production.lot']
        product_obj = self.env['product.product']
        for line in import_lines:
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
                inventory_line_obj.create({
                    'product_id': product.id,
                    'product_uom_id': product.uom_id.id,
                    'product_qty': line.quantity,
                    'inventory_id': line.inventory_id.id,
                    'location_id': line.location_id.id,
                    'prod_lot_id': lot_id})
                line.write({'fail': False, 'fail_reason': _('Processed')})
        return True

    @api.multi
    def action_done(self):
        for inventory in self:
            if not inventory.processed:
                raise exceptions.Warning(
                    _("Loaded lines must be processed at least one time for "
                      "inventory : %s") % (inventory.name))
            super(StockInventory, inventory).action_done()
