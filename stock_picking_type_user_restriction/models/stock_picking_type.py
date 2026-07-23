from odoo import fields, models


class PickingType(models.Model):
    _inherit = "stock.picking.type"
    assigned_user_ids = fields.Many2many(
        "res.users",
        string="Assigned users",
        help="Restrict some users to only access their assigned operation types. "
        "In order to apply the restriction, the user needs the "
        "'User: Assigned Operation Types Only' group",
    )
