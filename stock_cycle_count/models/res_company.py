from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    auto_start_inventory_from_cycle_count = fields.Boolean(
        string="Auto Start Inventory Adjustment from Cycle Count",
        help="If enabled, confirming a Cycle Count will "
        "start the related Inventory Adjustment.",
    )

    inventory_adjustment_counted_quantities = fields.Selection(
        selection=[
            ("counted", "Default to stock on hand"),
            ("zero", "Default to zero"),
        ],
        string="Inventory Adjustment Counted quantities from Cycle Count",
        help="If enabled, confirming a Cycle Count will start the related "
        "Inventory Adjustment.",
    )
