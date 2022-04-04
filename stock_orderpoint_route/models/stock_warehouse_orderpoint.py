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

    @api.depends('product_id', 'warehouse_id',
                 'warehouse_id.route_ids', 'location_id')
    def _compute_route_ids(self):
        route_obj = self.env['stock.location.route']
        for wh in self.mapped('warehouse_id'):
            wh_routes = wh.route_ids
            for record in self.filtered(lambda r: r.warehouse_id == wh):
                routes = route_obj.browse()
                if record.product_id:
                    routes += record.product_id.mapped(
                        'route_ids'
                    ) | record.product_id.mapped(
                        'categ_id'
                    ).mapped('total_route_ids')
                if record.warehouse_id:
                    routes |= wh_routes
                parents = record.get_parents()
                record.route_ids = routes.filtered(
                    lambda route: any(
                        p.location_id in parents
                        for p in route.rule_ids.filtered(
                            lambda rule: rule.action in ('pull', 'pull_push')
                        ).mapped('location_src_id')
                    )
                )

    def get_parents(self):
        location = self.location_id
        result = location
        while location.location_id:
            location = location.location_id
            result |= location
        return result

    def _prepare_procurement_values(self, product_qty, date=False,
                                    group=False):
        res = super()._prepare_procurement_values(
            product_qty, date=date, group=group
        )
        res['route_ids'] = self.route_id
        return res
