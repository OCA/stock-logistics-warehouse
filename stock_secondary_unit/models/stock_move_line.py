from odoo.tools import float_is_zero

from odoo.addons.stock.models.stock_move_line import StockMoveLine


def _new_get_aggregated_product_quantities(self, **kwargs):
    """Returns a dictionary of products (key = id+name+description+uom)
    and corresponding values of interest.
    Allows aggregation of data across separate move lines for the same product.
    This is expected to be useful in things such as delivery reports.
    Dict key is made as a combination of values we expect to want to group
    the products by (i.e. so data is not lost).
    This function purposely ignores lots/SNs because these are
    expected to already be properly grouped by line.
    returns: dictionary {product_id+name+description+uom:
    {product, name, description, qty_done, product_uom}, ...}
    """
    aggregated_move_lines = {}

    # Loops to get backorders, backorders' backorders, and so and so...
    backorders = self.env["stock.picking"]
    pickings = self.picking_id
    while pickings.backorder_ids:
        backorders |= pickings.backorder_ids
        pickings = pickings.backorder_ids

    for move_line in self:

        if kwargs.get("except_package") and move_line.result_package_id:
            continue
        aggregated_properties = self._get_aggregated_properties(move_line=move_line)
        line_key = f"{aggregated_properties['line_key']}_{move_line.id}"
        uom = aggregated_properties["product_uom"]
        qty_done = move_line.product_uom_id._compute_quantity(move_line.qty_done, uom)
        if line_key not in aggregated_move_lines:
            qty_ordered = None
            if backorders and not kwargs.get("strict"):
                qty_ordered = move_line.move_id.product_uom_qty
                # Filters on the aggregation key (product, description and uom) to add the
                # quantities delayed to backorders to retrieve the original ordered qty.
                following_move_lines = backorders.move_line_ids.filtered(
                    lambda ml: self._get_aggregated_properties(move=ml.move_id)[
                        "line_key"
                    ]
                    == line_key
                )
                qty_ordered += sum(
                    following_move_lines.move_id.mapped("product_uom_qty")
                )
                # Remove the done quantities of the other move lines of the stock move
                previous_move_lines = move_line.move_id.move_line_ids.filtered(
                    lambda ml: self._get_aggregated_properties(move=ml.move_id)[
                        "line_key"
                    ]
                    == line_key
                    and ml.id != move_line.id
                )
                qty_ordered -= sum(
                    map(
                        lambda m: m.product_uom_id._compute_quantity(
                            m.qty_done, aggregated_properties["product_uom"]
                        ),
                        previous_move_lines,
                    )
                )
            aggregated_move_lines[line_key] = {
                **aggregated_properties,
                "qty_done": qty_done,
                "qty_ordered": qty_ordered or qty_done,
                "product": move_line.product_id,
                "secondary_uom_qty": move_line.secondary_uom_qty,
                "secondary_uom_id": move_line.secondary_uom_id.name,
            }
        else:
            aggregated_move_lines[line_key]["qty_ordered"] += qty_done
            aggregated_move_lines[line_key]["qty_done"] += qty_done

    # Does the same for empty move line to retrieve the ordered qty. for partially done moves
    # (as they are splitted when the transfer is done and empty moves don't have move lines).
    if kwargs.get("strict"):
        return aggregated_move_lines
    pickings = self.picking_id | backorders
    for empty_move in pickings.move_ids:
        to_bypass = False
        if not (
            empty_move.product_uom_qty
            and float_is_zero(
                empty_move.quantity_done,
                precision_rounding=empty_move.product_uom.rounding,
            )
        ):
            continue
        if empty_move.state != "cancel":
            if empty_move.state != "confirmed" or empty_move.move_line_ids:
                continue
            else:
                to_bypass = True
        aggregated_properties = self._get_aggregated_properties(move=empty_move)
        line_key = aggregated_properties["line_key"]

        if line_key not in aggregated_move_lines and not to_bypass:
            qty_ordered = empty_move.product_uom_qty
            aggregated_move_lines[line_key] = {
                **aggregated_properties,
                "qty_done": False,
                "qty_ordered": qty_ordered,
                "product": empty_move.product_id,
            }
        elif line_key in aggregated_move_lines:
            aggregated_move_lines[line_key]["qty_ordered"] += empty_move.product_uom_qty
    return aggregated_move_lines


StockMoveLine._get_aggregated_product_quantities = (
    _new_get_aggregated_product_quantities
)
