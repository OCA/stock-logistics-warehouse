# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockMoveLocationWizard(models.TransientModel):
    _inherit = "wiz.stock.move.location"

    @api.onchange("picking_type_id")
    def _onchange_picking_type_id(self):
        for line in self.stock_move_location_line_ids:
            product_uom = line.product_id.uom_id
            purchase_uom = line.product_id.uom_po_id
            original_uom = line.product_uom_id

            # If the picking type has the 'use_purchase_uom' enabled,
            # set the uom to the product purchase one
            if self.picking_type_id.use_purchase_uom:
                new_uom = purchase_uom
            # Else, set the uom to the product uom again
            else:
                new_uom = product_uom

            if original_uom != new_uom:
                line.move_quantity = original_uom._compute_quantity(
                    line.move_quantity, new_uom
                )
                line.max_quantity = original_uom._compute_quantity(
                    line.max_quantity, new_uom
                )
                line.reserved_quantity = original_uom._compute_quantity(
                    line.reserved_quantity, new_uom
                )
                line.product_uom_id = new_uom

    def _get_move_values(self, picking, lines):
        res = super()._get_move_values(picking, lines)
        picking_id = res["picking_id"]
        picking = self.env["stock.picking"].search([("id", "=", picking_id)])
        if picking.picking_type_id.use_purchase_uom:
            original_uom_id = res["product_uom"]
            original_uom = self.env["uom.uom"].search([("id", "=", original_uom_id)])
            original_qty = res["product_uom_qty"]
            product_id = res["product_id"]
            product = self.env["product.product"].search([("id", "=", product_id)])

            new_uom = product.uom_po_id
            new_qty = original_uom._compute_quantity(original_qty, new_uom)
            res["product_uom_qty"] = new_qty
            res["product_uom"] = new_uom.id

        return res
