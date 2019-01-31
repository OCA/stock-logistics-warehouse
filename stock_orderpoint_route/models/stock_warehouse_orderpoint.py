# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    route_ids = fields.Many2many(
        'stock.location.route', string='Allowed routes',
        compute='_compute_route_ids',
    )
    route_id = fields.Many2one('stock.location.route', string='Route',
                               domain="[('id', 'in', route_ids)]",
                               ondelete='restrict')

    @api.depends('product_id', 'warehouse_id', 'location_id')
    def _compute_route_ids(self):
        route_obj = self.env['stock.location.route']
        for wh in self.mapped('warehouse_id'):
            wh_routes = route_obj.search(
                [('warehouse_ids', '=', wh.id)])
            for record in self.filtered(lambda r: r.warehouse_id == wh):
                routes = route_obj
                if record.product_id:
                    routes += record.product_id.mapped(
                        'route_ids'
                    ) | record.product_id.mapped(
                        'categ_id'
                    ).mapped('total_route_ids')
                if record.warehouse_id:
                    routes |= wh_routes
                parents = record.get_parents().ids
                record.route_ids = routes.filtered(lambda r: any(
                    p.location_id.id in parents for p in r.pull_ids))

    def get_parents(self):
        location = self.location_id
        result = location
        while location.location_id:
            location = location.location_id
            result |= location
        return result

    def _prepare_procurement_values(self, product_qty, date=False,
                                    group=False):

        res = super(StockWarehouseOrderpoint,
                    self)._prepare_procurement_values(product_qty, date=date,
                                                      group=group)
        res['route_ids'] = self.route_id
        return res
