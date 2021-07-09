# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockPutawayRule(models.Model):
    _inherit = "stock.putaway.rule"

    method = fields.Selection(
        selection="_get_putaway_options",
        string="Method",
        default="fixed",
        required=True,
    )

    @api.model
    def _get_putaway_options(self):
        return [("fixed", "Fixed Location")]
