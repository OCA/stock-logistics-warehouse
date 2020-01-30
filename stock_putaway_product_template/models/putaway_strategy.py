# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FixedPutAwayStrategy(models.Model):
    _inherit = "stock.fixed.putaway.strat"

    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        ondelete="cascade",
        readonly=True,
        related="product_id.product_tmpl_id",
        store=True
    )
