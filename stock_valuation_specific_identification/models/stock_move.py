# Copyright 2024 Matt Taylor
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit(self):
        # We only modify the function if this is a return of a delivery for a
        # product with SIV (Specific Identification Valuation) costing
        if (
            not self.product_id.specific_ident_cost
            or self.product_id.tracking == "none"
            or not self.origin_returned_move_id
            or not self.origin_returned_move_id.sudo().stock_valuation_layer_ids
            or self.origin_returned_move_id._is_dropshipped()
            or self.origin_returned_move_id._is_dropshipped_returned()
        ):
            return super(StockMove, self)._get_price_unit()

        lot = self.move_line_ids.mapped("lot_id")
        if lot and len(lot) > 1:
            raise ValidationError(
                _(
                    "We can't do multiple lots/serials on the same return. "
                    "Create separate returns for each lot/serial of this "
                    "product:\n%(product)s\n%(lots)s",
                    product=self.product_id.display_name,
                    lot=", ".join(lot.mapped("name")),
                )
            )

        layers = self.origin_returned_move_id.sudo().stock_valuation_layer_ids.filtered(
            lambda x: x.lot_id == lot
        )
        layers |= layers.stock_valuation_layer_ids
        quantity = sum(layers.mapped("quantity"))
        if not float_is_zero(quantity, precision_rounding=layers.uom_id.rounding):
            price_unit = sum(layers.mapped("value")) / quantity
        else:
            price_unit = 0.0
        return price_unit

    def _get_in_svl_vals(self, forced_quantity):
        specific_ident_moves = self.filtered(
            lambda m: m.product_id.specific_ident_cost
            and m.product_id.tracking != "none"
        )
        normal_moves = self - specific_ident_moves
        vals = super(StockMove, normal_moves)._get_in_svl_vals(
            forced_quantity=forced_quantity
        )
        if not specific_ident_moves:
            return vals

        # create separate SVLs for each lot/serial
        for move in specific_ident_moves:
            move = move.with_company(move.company_id)
            valued_move_lines = move._get_in_move_lines()
            lots = valued_move_lines.mapped("lot_id")
            # TODO: check for this case on all moves before processing any
            if len(lots) > 1 and forced_quantity:
                raise UserError(
                    _(
                        "We can't do the valuation because we don't "
                        "know which lot quantity is changing:\n%(lots)s",
                        lots=", ".join(lots.mapped("name")),
                    )
                )
            for lot in lots:
                # group SMLs into a single SVL for each lot/serial
                # TODO: will there ever be multiple SMLs, for the same lot, on a
                #  given stock move?
                lot_move_lines = valued_move_lines.filtered(lambda ml: ml.lot_id == lot)
                valued_quantity = 0
                for lot_move_line in lot_move_lines:
                    valued_quantity += lot_move_line.product_uom_id._compute_quantity(
                        lot_move_line.qty_done, move.product_id.uom_id
                    )
                # unit_cost may be negative (i.e. decrease an out move)
                unit_cost = abs(move._get_price_unit())
                svl_vals = move.product_id._prepare_in_svl_vals(
                    forced_quantity or valued_quantity, unit_cost
                )
                svl_vals.update(move._prepare_common_svl_vals())
                if forced_quantity:
                    svl_vals[
                        "description"
                    ] = "Correction of %s (modification of past move)" % (
                        move.picking_id.name or move.name
                    )

                svl_vals["lot_id"] = lot.id
                vals.append(svl_vals)
        return vals

    def _create_out_svl(self, forced_quantity=None):
        # We get forced_quantity when doing a correction SVL.
        # Correction SVLs are done when changing the qty_done on an already
        # completed SML.
        # e.g. This appears to happen when changing the quantity produced on a
        # completed manufacturing order. See mrp.production.write().
        # In this case, we won't have enough information to create a specific
        # identification valuation layer.  We would need to know which SML is
        # being changed, or to which lot/serial to apply the change.
        specific_ident_moves = self.filtered(
            lambda m: m.product_id.specific_ident_cost
            and m.product_id.tracking != "none"
        )
        normal_moves = self - specific_ident_moves
        recs = self.env["stock.valuation.layer"]
        recs |= super(StockMove, normal_moves)._create_out_svl(
            forced_quantity=forced_quantity
        )
        if not specific_ident_moves:
            return recs

        # create separate SVLs for each lot/serial
        svl_vals_list = []
        for move in specific_ident_moves:
            valued_move_lines = move._get_out_move_lines()
            lots = valued_move_lines.mapped("lot_id")
            # TODO: check for this case on all moves before processing any
            if len(lots) > 1 and forced_quantity:
                raise UserError(
                    _(
                        "We can't do the valuation because we don't "
                        "know which lot quantity is changing:\n%s"
                        % ", ".join(lots.mapped("name"))
                    )
                )
            for lot in lots:
                # group SMLs into a single SVL for each lot/serial
                # TODO: will there ever be multiple SMLs, for the same lot, on a
                #  given stock move?
                lot_move_lines = valued_move_lines.filtered(lambda ml: ml.lot_id == lot)
                valued_quantity = 0
                for lot_move_line in lot_move_lines:
                    valued_quantity += lot_move_line.product_uom_id._compute_quantity(
                        lot_move_line.qty_done, move.product_id.uom_id
                    )
                if float_is_zero(
                    forced_quantity or valued_quantity,
                    precision_rounding=move.product_id.uom_id.rounding,
                ):
                    continue
                svl_vals = lot._prepare_out_svl_vals(
                    forced_quantity or valued_quantity, move.company_id
                )
                svl_vals.update(move._prepare_common_svl_vals())
                if forced_quantity:
                    svl_vals[
                        "description"
                    ] = "Correction of %s (modification of past move)" % (
                        move.picking_id.name or move.name
                    )
                svl_vals["description"] += svl_vals.pop("rounding_adjustment", "")
                svl_vals_list.append(svl_vals)

        # Disallow negative stock quantities for products with specific
        # identification valuation
        lot_ids = [x["lot_id"] for x in svl_vals_list if x.get("remaining_qty")]
        if lot_ids:
            unavailable_lots = self.env["stock.lot"].browse(lot_ids)
            raise ValidationError(
                _(
                    "We can't process the move because the following lots/serials "
                    "are not available: %s" % ", ".join(unavailable_lots.mapped("name"))
                )
            )

        recs |= self.env["stock.valuation.layer"].sudo().create(svl_vals_list)
        return recs
