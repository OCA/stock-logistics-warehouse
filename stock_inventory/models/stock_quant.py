from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    to_do = fields.Boolean(default=False)

    stock_inventory_ids = fields.Many2many(
        "stock.inventory",
        "stock_inventory_stock_quant_rel",
        string="Stock Inventories",
        copy=False,
    )
    current_inventory_id = fields.Many2one(
        "stock.inventory",
        string="Current Inventory",
        store=True,
    )

    def _apply_inventory(self):
        inventories = self.current_inventory_id
        if inventories and self.env.company.stock_inventory_auto_complete:
            # Concurrent applies must conflict on the inventory row, or neither one
            # sees the other's quants as done and the inventory never auto-completes.
            inventories.write({})
        res = super(
            StockQuant, self.with_context(stock_inventory_quant_ids=self.ids)
        )._apply_inventory()
        adjustment = self.env["stock.inventory"].browse()
        for rec in self:
            adjustment = rec.current_inventory_id
            rec.to_do = False
            rec.current_inventory_id = False
        if adjustment and self.env.company.stock_inventory_auto_complete:
            adjustment.action_auto_state_to_done()
        return res

    def _get_inventory_move_values(
        self,
        qty,
        location_id,
        location_dest_id,
        package_id=False,
        package_dest_id=False,
    ):
        vals = super()._get_inventory_move_values(
            qty, location_id, location_dest_id, package_id, package_dest_id
        )
        adjustment = self.current_inventory_id
        # move_quants() builds its moves here too: only link the applied quants.
        if adjustment and self.id in self.env.context.get(
            "stock_inventory_quant_ids", []
        ):
            for command in vals["move_line_ids"]:
                command[2].update(
                    {
                        "inventory_adjustment_id": adjustment.id,
                        "reference": f"{adjustment.name}: {vals['name']}",
                    }
                )
        return vals

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
