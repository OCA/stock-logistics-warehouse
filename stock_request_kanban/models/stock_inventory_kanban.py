# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, fields


class StockInventoryKanban(models.Model):
    _name = 'stock.inventory.kanban'
    _description = 'Inventory for Kanban'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        readonly=True, states={'draft': [('readonly', False)]}
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('on_progress', 'On progress'),
        ('finished', 'Finished'),
        ('closed', 'Closed')
    ], required=True, default='draft', readonly=True)
    warehouse_ids = fields.Many2many(
        'stock.warehouse', string='Warehouse',
        ondelete="cascade",
        readonly=True, states={'draft': [('readonly', False)]},
    )
    location_ids = fields.Many2many(
        'stock.location', string='Location',
        domain=[('usage', 'in', ['internal', 'transit'])],
        ondelete="cascade",
        readonly=True, states={'draft': [('readonly', False)]},
    )
    product_ids = fields.Many2many(
        'product.product', string='Product',
        domain=[('type', 'in', ['product', 'consu'])],
        ondelete='cascade',
        readonly=True, states={'draft': [('readonly', False)]},
    )
    kanban_ids = fields.Many2many(
        'stock.request.kanban',
        relation='stock_inventory_kanban_kanban',
        readonly=True,
    )
    scanned_kanban_ids = fields.Many2many(
        'stock.request.kanban',
        relation='stock_inventory_kanban_scanned_kanban',
        readonly=True,
    )
    missing_kanban_ids = fields.Many2many(
        'stock.request.kanban',
        readonly=True,
        compute='_compute_missing_kanban'
    )

    @api.depends('kanban_ids', 'scanned_kanban_ids')
    def _compute_missing_kanban(self):
        for rec in self:
            rec.missing_kanban_ids = rec.kanban_ids.filtered(
                lambda r: r.id not in rec.scanned_kanban_ids.ids
            )

    def _get_inventory_kanban_domain(self):
        domain = []
        if self.warehouse_ids:
            domain.append(('warehouse_id', 'in', self.warehouse_ids.ids))
        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))
        if self.location_ids:
            domain.append(('location_id', 'in', self.location_ids.ids))
        return domain

    def _start_inventory_values(self):
        return {
            'state': 'on_progress'
        }

    def _finish_inventory_values(self):
        return {
            'state': 'finished'
        }

    def _close_inventory_values(self):
        return {
            'state': 'closed'
        }

    @api.multi
    def calculate_kanbans(self):
        for rec in self:
            if rec.state == 'draft':
                rec.kanban_ids = self.env['stock.request.kanban'].search(
                    rec._get_inventory_kanban_domain()
                )

    @api.multi
    def start_inventory(self):
        self.calculate_kanbans()
        self.write(self._start_inventory_values())

    @api.multi
    def finish_inventory(self):
        self.write(self._finish_inventory_values())

    @api.multi
    def close_inventory(self):
        self.write(self._close_inventory_values())

    @api.multi
    def print_missing_kanbans(self):
        """ Print the missing kanban cards in order to restore them
        """
        self.ensure_one()
        return self.env.ref(
            'stock_request_kanban.action_report_kanban').report_action(
            self.missing_kanban_ids
        )
