# Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


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
        readonly=True,
    )
    destination_location_id = fields.Many2one(
        string='Destination Location',
        comodel_name='stock.location',
        readonly=True,
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
        readonly=True,
    )

    @api.constrains("max_quantity", "move_quantity")
    def _contraints_max_move_quantity(self):
        for record in self:
            if (record.move_quantity > record.max_quantity or
                    record.move_quantity < 0):
                raise ValidationError(_(
                    "Move quantity can not exceed max quantity or be negative"
                ))

    def create_move_lines(self, picking):
        for line in self:
            self.env["stock.move.line"].create(
                self._get_move_line_values(line, picking)
            )
        return True

    def _get_move_line_values(self, line, picking):
        return {
            "product_id": line.product_id.id,
            "lot_id": line.lot_id.id,
            "location_id": line.origin_location_id.id,
            "location_dest_id": line.destination_location_id.id,
            "qty_done": line._get_available_quantity(),
            "product_uom_id": line.product_uom_id.id,
            "picking_id": picking.id,
        }

    def _get_available_quantity(self):
        """We check here if the actual amount changed in the stock.

        We don't care about the reservations but we do care about not moving
        more than exists."""
        self.ensure_one()
        if not self.product_id:
            return 0
        # switched to sql here to improve performance and lower db queries
        self.env.cr.execute(self._get_specific_quants_sql())
        available_qty = self.env.cr.fetchone()[0]
        if available_qty < self.move_quantity:
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
