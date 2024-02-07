from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    virtual_in_progress_inventory_id = fields.Many2one(
        comodel_name="stock.inventory",
        compute="_compute_virtual_in_progress_inventory_id",
    )
    to_do = fields.Boolean(default=True)

    def _compute_virtual_in_progress_inventory_id(self):
        Inventory = self.env["stock.inventory"]
        for rec in self:
            rec.virtual_in_progress_inventory_id = Inventory.search(
                [
                    ("state", "=", "in_progress"),
                    ("location_ids", "parent_of", rec.location_id.ids),
                ],
                limit=1,
            )

    def _apply_inventory(self):
        res = super()._apply_inventory()
        self.write(
            {
                "to_do": False,
            }
        )
        return res

    def _get_inventory_fields_write(self):
        return super()._get_inventory_fields_write() + ["to_do"]

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        res = super()._get_inventory_move_values(
            qty, location_id, location_dest_id, out=out
        )
        inventory = self.virtual_in_progress_inventory_id
        if self.virtual_in_progress_inventory_id:
            for move_line_item in res.get("move_line_ids", []):
                move_line_values = move_line_item[-1]
                move_line_values["inventory_adjustment_id"] = inventory.id
        return res
