# Copyright (C) 2023 Syera BONNEAUX
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_supply_warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    default_resupply_warehouse_id = fields.Many2one("stock.warehouse", help="default warehouse on a partner", compute="_compute_preferred_warehouse_id")

    def _compute_preferred_warehouse_id(self):
        for rec in self:
            rec.default_resupply_warehouse_id=rec._get_warehouse()

    def _get_warehouse(self):
        warehouse = self.partner_supply_warehouse_id
        if not warehouse:
            warehouse = self.parent_id.partner_supply_warehouse_id
        return warehouse
