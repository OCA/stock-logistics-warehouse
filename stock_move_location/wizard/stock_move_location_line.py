# Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class StockMoveLocationWizardLine(models.TransientModel):
    _name = "wiz.stock.move.location.line"

    move_location_wizard_id = fields.Many2one(
        string="Move location Wizard",
        comodel_name="wiz.stock.move.location",
        ondelete="cascade",
        required=True,
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        required=True,
    )
    origin_location_id = fields.Many2one(
        string='Origin Location',
        comodel_name='stock.location',
    )
    destination_location_id = fields.Many2one(
        string='Destination Location',
        comodel_name='stock.location',
    )
    product_uom_id = fields.Many2one(
        string='Product Unit of Measure',
        comodel_name='product.uom',
    )
    lot_id = fields.Many2one(
        string='Lot/Serial Number',
        comodel_name='stock.production.lot',
        domain="[('product_id','=',product_id)]"
    )
    move_quantity = fields.Float(
        string="Quantity to move",
        digits=dp.get_precision('Product Unit of Measure'),
    )
    max_quantity = fields.Float(
        string="Maximum available quantity",
        digits=dp.get_precision('Product Unit of Measure'),
    )
    custom = fields.Boolean(
        string="Custom line",
        default=True,
    )

    @api.model
    def get_rounding(self):
        return self.env.ref("product.decimal_product_uom").digits or 3

    @api.constrains("max_quantity", "move_quantity")
    def _constraint_max_move_quantity(self):
        for record in self:
            if (float_compare(
                    record.move_quantity,
                    record.max_quantity, self.get_rounding()) == 1 or
                    float_compare(record.move_quantity, 0.0,
                                  self.get_rounding()) == -1):
                raise ValidationError(_(
                    "Move quantity can not exceed max quantity or be negative"
                ))

    def create_move_lines(self, picking, move):
        for line in self:
            values = line._get_move_line_values(picking, move)
            if values.get("qty_done") <= 0:
                continue
            self.env["stock.move.line"].create(
                values
            )
        return True

    @api.multi
    def _get_move_line_values(self, picking, move):
        self.ensure_one()
        return {
            "product_id": self.product_id.id,
            "lot_id": self.lot_id.id,
            "location_id": self.origin_location_id.id,
            "location_dest_id": self.destination_location_id.id,
            "qty_done": self._get_available_quantity(),
            "product_uom_id": self.product_uom_id.id,
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
            return self.move_quantity
        # switched to sql here to improve performance and lower db queries
        self.env.cr.execute(self._get_specific_quants_sql())
        available_qty = self.env.cr.fetchone()
        if not available_qty:
            # if it is immediate transfer and product doesn't exist in that
            # location -> make the transfer of 0.
            return 0
        available_qty = available_qty[0]
        if float_compare(
                available_qty,
                self.move_quantity, self.get_rounding()) == -1:
            return available_qty
        return self.move_quantity

    def _get_specific_quants_sql(self):
        self.ensure_one()
        lot = "AND lot_id = {}".format(self.lot_id.id)
        if not self.lot_id:
            lot = "AND lot_id is null"
        return """
        SELECT sum(quantity)
        FROM stock_quant
        WHERE location_id = {location}
        {lot}
        AND product_id = {product}
        GROUP BY location_id, product_id, lot_id
        """.format(
            location=self.origin_location_id.id,
            product=self.product_id.id,
            lot=lot,
        )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        # update of wizard lines is extremely buggy
        # so i have to handle this additionally in create
        if not all([res.origin_location_id, res.destination_location_id]):
            or_loc_id = res.move_location_wizard_id.origin_location_id.id
            des_loc_id = res.move_location_wizard_id.destination_location_id.id
            res.write({
                "origin_location_id": or_loc_id,
                "destination_location_id": des_loc_id,
            })
        return res
