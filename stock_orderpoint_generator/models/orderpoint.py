# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    orderpoint_template_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint.template"
    )
