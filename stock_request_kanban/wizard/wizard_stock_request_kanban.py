# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, _


class WizardStockRequestOrderKanbanAbstract(models.TransientModel):
    _name = "wizard.stock.request.kanban"
    _inherit = "wizard.stock.request.kanban.abstract"

    stock_request_id = fields.Many2one(
        'stock.request',
        readonly=True,
    )

    def barcode_ending(self):
        super().barcode_ending()
        self.stock_request_id = self.env['stock.request'].create(
            self.stock_request_kanban_values()
        )
        self.status_state = 0
        self.status = _('Added kanban %s for product %s' % (
            self.stock_request_id.kanban_id.name,
            self.stock_request_id.product_id.display_name
        ))
        self.stock_request_ending()

    def stock_request_ending(self):
        self.stock_request_id.action_confirm()

    def stock_request_kanban_values(self):
        return {
            'company_id': self.kanban_id.company_id.id,
            'procurement_group_id':
                self.kanban_id.procurement_group_id.id or False,
            'location_id': self.kanban_id.location_id.id or False,
            'warehouse_id': self.kanban_id.warehouse_id.id or False,
            'product_id': self.kanban_id.product_id.id,
            'product_uom_id': self.kanban_id.product_uom_id.id or False,
            'route_id': self.kanban_id.route_id.id or False,
            'product_uom_qty': self.kanban_id.product_uom_qty,
            'kanban_id': self.kanban_id.id,
        }
