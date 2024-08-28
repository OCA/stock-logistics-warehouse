from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    to_do = fields.Boolean(default=False)
    virtual_in_progress_inventory_id = fields.Many2one(
        comodel_name="stock.inventory",
        compute="_compute_virtual_in_progress_inventory_id",
    )
    stock_inventory_ids = fields.Many2many(
        comodel_name="stock.inventory",
        string="Inventory Adjustment",
        readonly=True,
    )

    def _compute_virtual_in_progress_inventory_id(self):
        locations = self.mapped("location_id")
        inventories = self.env["stock.inventory"].search(
            self._get_virtual_in_progress_inventory_domain(locations),
            limit=1,
        )
        for rec in self:
            filtered_inventories = inventories.filtered_domain(
                self._get_virtual_in_progress_inventory_domain(rec.location_id)
            )
            rec.virtual_in_progress_inventory_id = (
                filtered_inventories[0] if filtered_inventories else False
            )

    stock_inventory_ids = fields.Many2many(
        "stock.inventory",
        "stock_inventory_stock_quant_rel",
        string="Stock Inventories",
        copy=False,
    )

    def _apply_inventory(self):
        context = dict(self.env.context)
        context.pop("default_to_do", False)
        context.pop("default_stock_inventory_ids", False)
        res = super(
            StockQuant, self.with_context(context)  # pylint: disable=W8121
        )._apply_inventory()
        record_moves = self.env["stock.move.line"]
        adjustment = self.env["stock.inventory"].browse()
        for rec in self:
            adjustment = rec.virtual_in_progress_inventory_id
            move = record_moves.search(
                [
                    ("id", "in", adjustment.stock_move_ids.ids),
                    ("product_id", "=", rec.product_id.id),
                    ("lot_id", "=", rec.lot_id.id),
                    "|",
                    ("location_id", "=", rec.location_id.id),
                    ("location_dest_id", "=", rec.location_id.id),
                ],
                order="create_date asc",
                limit=1,
            ).filtered(
                lambda x: not x.company_id.id
                or not rec.company_id.id
                or rec.company_id.id == x.company_id.id
            )
            if not move:
                continue
            reference = move.reference
            if adjustment.name and move.reference:
                reference = adjustment.name + ": " + move.reference
            elif adjustment.name:
                reference = adjustment.name
            move.write(
                {
                    "reference": reference,
                }
            )
            rec.to_do = False
        if adjustment and adjustment.company_id.stock_inventory_auto_complete:
            adjustment.action_auto_state_to_done()
        return res

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        res = super()._get_inventory_move_values(
            qty, location_id, location_dest_id, out=out
        )
        inventory = self.virtual_in_progress_inventory_id
        if self.virtual_in_progress_inventory_id:
            for move_line_item in res.get("move_line_ids", []):
                move_line_values = move_line_item[-1]
                move_line_values.update(
                    {
                        "inventory_adjustment_id": inventory.id,
                    }
                )
        return res

    def _get_inventory_fields_write(self):
        return super()._get_inventory_fields_write() + ["to_do"]

    @api.model
    def _get_virtual_in_progress_inventory_domain(self, locations):
        return [
            ("state", "=", "in_progress"),
            "|",
            "&",
            ("exclude_sublocation", "=", False),
            ("location_ids", "parent_of", locations.ids),
            "&",
            ("exclude_sublocation", "=", True),
            ("location_ids", "in", locations.ids),
        ]
