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
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
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
