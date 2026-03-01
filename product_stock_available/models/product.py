from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    available_warehouse_ids = fields.Many2many(
        'stock.warehouse',
        'product_warehouse_availability_rel',
        'product_id',
        'warehouse_id',
        string='Available in Warehouses'
    )

    available_location_ids = fields.Many2many(
        'stock.location',
        'product_location_availability_rel',
        'product_id',
        'location_id',
        string='Available in Locations'
    )

    def _update_available_warehouses(self):
        for product in self:
            quant = self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('quantity', '>', 0)
                ])
            available_whs = self.env['stock.warehouse']
            for q in quant:
                warehouse_id = q.location_id.get_warehouse()
                available_whs |= warehouse_id
            product.available_warehouse_ids = available_whs

    def _update_available_locations(self):
        for product in self:
            quant = self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('quantity', '>', 0)
                ])
            product_location = self.env['stock.location']
            for q in quant:
                product_location |= q.location_id
            product.available_location_ids = product_location


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    available_warehouse_ids = fields.Many2many(
        'stock.warehouse',
        compute='_compute_available_warehouse_ids',
        store=True,
        string='Available in Warehouses'
    )

    available_location_ids = fields.Many2many(
        'stock.location',
        compute='_compute_available_location_ids',
        store=True,
        string='Available in Locations'
    )

    @api.depends('product_variant_ids', 'product_variant_ids.available_warehouse_ids')
    def _compute_available_warehouse_ids(self):
        for template in self:
            warehouses = self.env['stock.warehouse']
            for variant in template.product_variant_ids:
                warehouses |= variant.available_warehouse_ids
            template.available_warehouse_ids = warehouses

    @api.depends('product_variant_ids', 'product_variant_ids.available_location_ids')
    def _compute_available_location_ids(self):
        for template in self:
            locations = self.env['stock.location']
            for variant in template.product_variant_ids:
                locations |= variant.available_location_ids
            template.available_location_ids = locations
