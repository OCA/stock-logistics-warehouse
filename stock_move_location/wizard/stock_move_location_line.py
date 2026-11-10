# Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StockMoveLocationWizardLine(models.TransientModel):
    _name = "wiz.stock.move.location.line"
    _description = "Wizard move location line"

    move_location_wizard_id = fields.Many2one(
        string="Move location Wizard",
        comodel_name="wiz.stock.move.location",
    )
    product_id = fields.Many2one(comodel_name="product.product", required=True)
    origin_location_id = fields.Many2one(comodel_name="stock.location")
    destination_location_id = fields.Many2one(
        comodel_name="stock.location",
        compute="_compute_destination_location_id",
    )
    product_uom_id = fields.Many2one(
        string="Product Unit of Measure", comodel_name="uom.uom"
    )
    lot_id = fields.Many2one(
        string="Lot/Serial Number",
        comodel_name="stock.lot",
        domain="[('product_id','=',product_id)]",
    )
    package_id = fields.Many2one(
        string="Package Number",
        comodel_name="stock.package",
        domain="[('location_id', '=', origin_location_id)]",
    )
    owner_id = fields.Many2one(comodel_name="res.partner", string="From Owner")
    move_quantity = fields.Float(string="Quantity to move", digits="Product Unit")
    max_quantity = fields.Float(
        string="Maximum available quantity", digits="Product Unit"
    )
    total_quantity = fields.Float(
        string="Total existence quantity", digits="Product Unit"
    )
    reserved_quantity = fields.Float(digits="Product Unit")
    custom = fields.Boolean(string="Custom line", default=True)

    @api.depends("move_location_wizard_id.destination_location_id")
    def _compute_destination_location_id(self):
        for record in self:
            record.destination_location_id = (
                record.move_location_wizard_id.destination_location_id
            )

    @api.constrains("max_quantity", "move_quantity")
    def _constraint_max_move_quantity(self):
        for record in self:
            uom = record.product_uom_id
            move_qty_gt_max_qty = (
                uom.compare(record.move_quantity, record.max_quantity) == 1
            )
            move_qty_lt_0 = uom.compare(record.move_quantity, 0.0) == -1
            if move_qty_gt_max_qty or move_qty_lt_0:
                raise ValidationError(
                    self.env._(
                        "Move quantity can not exceed max quantity or be negative"
                    )
                )

    def create_move_lines(self, picking, move):
        for line in self:
            values = line._get_move_line_values(picking, move)
            if not self.env.context.get("planned") and values.get("quantity") <= 0:
                continue
            self.env["stock.move.line"].create(values)
        return True

    def _get_move_line_values(self, picking, move):
        self.ensure_one()
        location_dest_id = (
            self.move_location_wizard_id.apply_putaway_strategy
            and self.destination_location_id._get_putaway_strategy(self.product_id).id
            or self.destination_location_id.id
        )
        qty_done = self._get_available_quantity()
        return {
            "product_id": self.product_id.id,
            "lot_id": self.lot_id.id,
            "package_id": self.package_id.id,
            "result_package_id": self.package_id.id,
            "owner_id": self.owner_id.id,
            "location_id": self.origin_location_id.id,
            "location_dest_id": location_dest_id,
            "quantity": qty_done,
            "uom_id": self.product_uom_id.id,
            "picking_id": picking.id,
            "move_id": move.id,
        }

    def _get_available_quantity(self):
        """We check here if the actual amount changed in the stock.

        We don't care about the reservations but we do care about not moving
        more than exists."""
        self.ensure_one()
        if not self.product_id:
            return 0
        if self.env.context.get("planned"):
            # for planned transfer we don't care about the amounts at all
            return 0.0

        # Check if we should exclude reserved quantities
        exclude_reserved = self.move_location_wizard_id.exclude_reserved_qty

        if exclude_reserved:
            # Use the built-in stock.quant method to get available quantity
            available_qty = self.env["stock.quant"]._get_available_quantity(
                product_id=self.product_id,
                location_id=self.origin_location_id,
                lot_id=self.lot_id,
                package_id=self.package_id,
                owner_id=self.owner_id,
                strict=False,
            )
        else:
            # Include reserved quantities - use total quantity from quant
            quant = self.env["stock.quant"].search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("location_id", "=", self.origin_location_id.id),
                    ("lot_id", "=", self.lot_id.id or False),
                    ("package_id", "=", self.package_id.id or False),
                    ("owner_id", "=", self.owner_id.id or False),
                ],
                limit=1,
            )
            available_qty = quant.quantity if quant else 0

        if not available_qty:
            # if it is immediate transfer and product doesn't exist in that
            # location -> make the transfer of 0.
            return 0
        available_qty_lt_move_qty = (
            self.product_uom_id.compare(available_qty, self.move_quantity) == -1
        )
        return available_qty if available_qty_lt_move_qty else self.move_quantity
