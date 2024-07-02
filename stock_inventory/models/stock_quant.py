from odoo import _, api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    to_do = fields.Boolean(default=False)

    def _apply_inventory(self):
        res = super()._apply_inventory()
        record_moves = self.env["stock.move.line"]
        adjustment = self.env["stock.inventory"].browse()
        for rec in self:
            adjustment = (
                self.env["stock.inventory"]
                .search([("state", "=", "in_progress")])
                .filtered(
                    lambda x, rec=rec: rec.location_id in x.location_ids
                    or (
                        rec.location_id in x.location_ids.child_internal_location_ids
                        and not x.exclude_sublocation
                    )
                )
            )
            moves = record_moves.search(
                [
                    ("product_id", "=", rec.product_id.id),
                    ("lot_id", "=", rec.lot_id.id),
                    "|",
                    ("location_id", "=", rec.location_id.id),
                    ("location_dest_id", "=", rec.location_id.id),
                ],
                order="create_date asc",
            ).filtered(
                lambda x, rec=rec: not x.company_id.id
                or not rec.company_id.id
                or rec.company_id.id == x.company_id.id
            )
            if len(moves) == 0:
                raise ValueError(_("No move lines have been created"))
            move = moves[len(moves) - 1]
            adjustment.stock_move_ids |= move
            reference = move.reference
            if adjustment.name and move.reference:
                reference = adjustment.name + ": " + move.reference
            elif adjustment.name:
                reference = adjustment.name
            move.write(
                {
                    "inventory_adjustment_id": adjustment.id,
                    "reference": reference,
                }
            )
            rec.to_do = False
        if adjustment and self.env.company.stock_inventory_auto_complete:
            adjustment.action_auto_state_to_done()
        return res

    def _get_inventory_fields_write(self):
        return super()._get_inventory_fields_write() + ["to_do"]

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if self.env.context.get(
            "active_model", False
        ) == "stock.inventory" and self.env.context.get("active_id", False):
            self.env["stock.inventory"].browse(
                self.env.context.get("active_id")
            ).refresh_stock_quant_ids()
        return res
