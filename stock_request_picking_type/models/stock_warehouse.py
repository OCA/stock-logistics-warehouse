
from odoo import fields, models, api, SUPERUSER_ID

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    stock_request_type_id = fields.Many2one(
        'stock.picking.type',
        string='Stock Request Type',
        ondelete='cascade'
    )

    @api.model
    def create(self, vals):
        warehouse = super(StockWarehouse, self).create(vals)
        if not warehouse.stock_request_type_id:
            picking_type = self.env['stock.picking.type'].create({
                'name': f'Stock Request {warehouse.name}',
                'code': 'stock_request_order',
                'warehouse_id': warehouse.id,
                'sequence_code': 'SRO',
                'company_id': warehouse.company_id.id,
            })
            warehouse.stock_request_type_id = picking_type.id
        return warehouse

    def write(self, vals):
        res = super(StockWarehouse, self).write(vals)
        for warehouse in self:
            if not warehouse.stock_request_type_id:
                picking_type = self.env['stock.picking.type'].create({
                    'name': f'Stock Request {warehouse.name}',
                    'code': 'stock_request_order',
                    'warehouse_id': warehouse.id,
                    'sequence_code': 'SRO',
                    'company_id': warehouse.company_id.id,
                })
                warehouse.stock_request_type_id = picking_type.id
        return res

def update_stock_request_type(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    warehouses = env['stock.warehouse'].search([('stock_request_type_id', '=', False)])
    for warehouse in warehouses:
        picking_type = env['stock.picking.type'].create({
            'name': f'Stock Request {warehouse.name}',
            'code': 'stock_request_order',
            'warehouse_id': warehouse.id,
            'sequence_code': 'SRO',
            'company_id': warehouse.company_id.id,
        })
        warehouse.stock_request_type_id = picking_type.id
