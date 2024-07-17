# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.tools.misc import OrderedSet


class StockMoveClass(models.Model):
    _inherit = "stock.move"

    product_id = fields.Many2one(required=False)
    product_template_id = fields.Many2one(
        comodel_name="product.template",
        string="Product template",
        required=False,
    )

    def _prepare_procurement_values(self):
        return {
            **super()._prepare_procurement_values(),
            "product_template_id": self.product_template_id,
        }

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        return [
            *super()._prepare_merge_moves_distinct_fields(),
            "product_template_id",
        ]

    @api.constrains("product_uom")
    def _check_uom(self):
        super(StockMoveClass, self.filtered(lambda move: move.product_id))._check_uom()
        moves_error = self.filtered(
            lambda move: not move.product_id
            and move.product_template_id.uom_id.category_id
            != move.product_uom.category_id
        )
        if moves_error:
            user_warning = _(
                "You cannot perform the move because the unit of measure has a different category as the product unit of measure."
            )
            for move in moves_error:
                user_warning += _(
                    "\n\n%s --> Product UoM is %s (%s) - Move UoM is %s (%s)"
                ) % (
                    move.product_template_id.display_name,
                    move.product_template_id.uom_id.name,
                    move.product_template_id.uom_id.category_id.name,
                    move.product_uom.name,
                    move.product_uom.category_id.name,
                )
            user_warning += _("\n\nBlocking: %s") % " ,".join(
                moves_error.mapped("name")
            )
            raise UserError(user_warning)

    def _prepare_procurement_values(self):
        """Prepare specific key for moves or other componenets that will be created from a stock rule
        comming from a stock move. This method could be override in order to add other custom key that could
        be used in move/po creation.
        """
        if not isinstance(self.product_id, self.env["product.product"].__class__):
            return super()._prepare_procurement_values()
        self.ensure_one()
        group_id = self.group_id or False
        if self.rule_id:
            if (
                self.rule_id.group_propagation_option == "fixed"
                and self.rule_id.group_id
            ):
                group_id = self.rule_id.group_id
            elif self.rule_id.group_propagation_option == "none":
                group_id = False
        product_template_id = self.product_template_id.with_context(
            lang=self._get_lang()
        )
        return {
            "product_description_variants": self.description_picking
            and self.description_picking.replace(
                product_template_id._get_description(self.picking_type_id), ""
            ),
            "product_template_id": product_template_id.id,
            "date_planned": self.date,
            "date_deadline": self.date_deadline,
            "move_dest_ids": self,
            "group_id": group_id,
            "route_ids": self.route_ids,
            "warehouse_id": self.warehouse_id
            or self.picking_id.picking_type_id.warehouse_id
            or self.picking_type_id.warehouse_id,
            "priority": self.priority,
            "orderpoint_id": self.orderpoint_id,
        }

    def _should_bypass_reservation(self):
        self.ensure_one()
        if self.product_id:
            return super()._should_bypass_reservation()
        return (
            self.location_id.should_bypass_reservation()
            or self.product_template_id.type != "product"
        )

    # necessary hook to be able to override move reservation to a restrict lot, owner, pack, location...
    def _get_available_quantity(self, *args, **kwargs):
        self.ensure_one()
        if self.product_id:
            super()._get_available_quantity(*args, **kwargs)
        else:
            return self.env["stock.quant"]._get_available_quantity(
                self.product_template_id, *args, **kwargs
            )

    def _action_assign(self):
        """Reserve stock moves by creating their stock move lines. A stock move is
        considered reserved once the sum of `product_qty` for all its move lines is
        equal to its `product_qty`. If it is less, the stock move is considered
        partially available.
        """
        # first assign moves with product.product as much restrictive
        super(
            StockMoveClass, self.filtered(lambda move: move.product_id)
        )._action_assign()
        self = self.filtered(lambda move: not move.product_id)
        StockMove = self.env["stock.move"]
        assigned_moves_ids = OrderedSet()
        partially_available_moves_ids = OrderedSet()
        # Read the `reserved_availability` field of the moves out of the loop to prevent unwanted
        # cache invalidation when actually reserving the move.
        reserved_availability = {move: move.reserved_availability for move in self}
        roundings = {move: move.product_template_id.uom_id.rounding for move in self}
        move_line_vals_list = []
        for move in self.filtered(
            lambda m: m.state in ["confirmed", "waiting", "partially_available"]
        ):
            rounding = roundings[move]
            missing_reserved_uom_quantity = (
                move.product_uom_qty - reserved_availability[move]
            )
            missing_reserved_quantity = move.product_uom._compute_quantity(
                missing_reserved_uom_quantity,
                move.product_template_id.uom_id,
                rounding_method="HALF-UP",
            )
            if move._should_bypass_reservation():
                raise NotImplementedError()
                # create the move line(s) but do not impact quants
                # if move.product_id.tracking == 'serial' and (move.picking_type_id.use_create_lots or move.picking_type_id.use_existing_lots):
                #     for i in range(0, int(missing_reserved_quantity)):
                #         move_line_vals_list.append(move._prepare_move_line_vals(quantity=1))
                # else:
                #     to_update = move.move_line_ids.filtered(lambda ml: ml.product_uom_id == move.product_uom and
                #                                             ml.location_id == move.location_id and
                #                                             ml.location_dest_id == move.location_dest_id and
                #                                             ml.picking_id == move.picking_id and
                #                                             not ml.lot_id and
                #                                             not ml.package_id and
                #                                             not ml.owner_id)
                #     if to_update:
                #         to_update[0].product_uom_qty += missing_reserved_uom_quantity
                #     else:
                #         move_line_vals_list.append(move._prepare_move_line_vals(quantity=missing_reserved_quantity))
                # assigned_moves_ids.add(move.id)
            else:
                if float_is_zero(
                    move.product_uom_qty, precision_rounding=move.product_uom.rounding
                ):
                    assigned_moves_ids.add(move.id)
                elif not move.move_orig_ids:
                    if move.procure_method == "make_to_order":
                        continue
                    # If we don't need any quantity, consider the move assigned.
                    need = missing_reserved_quantity
                    if float_is_zero(need, precision_rounding=rounding):
                        assigned_moves_ids.add(move.id)
                        continue
                    # Reserve new quants and create move lines accordingly.
                    forced_package_id = move.package_level_id.package_id or None
                    available_quantity = move._get_available_quantity(
                        move.location_id, package_id=forced_package_id
                    )
                    if available_quantity <= 0:
                        continue
                    taken_quantity = move._update_reserved_quantity(
                        need,
                        available_quantity,
                        move.location_id,
                        package_id=forced_package_id,
                        strict=False,
                    )
                    if float_is_zero(taken_quantity, precision_rounding=rounding):
                        continue
                    if (
                        float_compare(need, taken_quantity, precision_rounding=rounding)
                        == 0
                    ):
                        assigned_moves_ids.add(move.id)
                    else:
                        partially_available_moves_ids.add(move.id)
                else:
                    # Check what our parents brought and what our siblings took in order to
                    # determine what we can distribute.
                    # `qty_done` is in `ml.product_uom_id` and, as we will later increase
                    # the reserved quantity on the quants, convert it here in
                    # `product_id.uom_id` (the UOM of the quants is the UOM of the product).
                    move_lines_in = move.move_orig_ids.filtered(
                        lambda m: m.state == "done"
                    ).mapped("move_line_ids")
                    keys_in_groupby = [
                        "location_dest_id",
                        "lot_id",
                        "result_package_id",
                        "owner_id",
                    ]

                    def _keys_in_sorted(ml):
                        return (
                            ml.location_dest_id.id,
                            ml.lot_id.id,
                            ml.result_package_id.id,
                            ml.owner_id.id,
                        )

                    grouped_move_lines_in = {}
                    for k, g in groupby(
                        sorted(move_lines_in, key=_keys_in_sorted),
                        key=itemgetter(*keys_in_groupby),
                    ):
                        qty_done = 0
                        for ml in g:
                            qty_done += ml.product_uom_id._compute_quantity(
                                ml.qty_done, ml.product_id.uom_id
                            )
                        grouped_move_lines_in[k] = qty_done
                    move_lines_out_done = (
                        (move.move_orig_ids.mapped("move_dest_ids") - move)
                        .filtered(lambda m: m.state in ["done"])
                        .mapped("move_line_ids")
                    )
                    # As we defer the write on the stock.move's state at the end of the loop, there
                    # could be moves to consider in what our siblings already took.
                    moves_out_siblings = (
                        move.move_orig_ids.mapped("move_dest_ids") - move
                    )
                    moves_out_siblings_to_consider = moves_out_siblings & (
                        StockMove.browse(assigned_moves_ids)
                        + StockMove.browse(partially_available_moves_ids)
                    )
                    reserved_moves_out_siblings = moves_out_siblings.filtered(
                        lambda m: m.state in ["partially_available", "assigned"]
                    )
                    move_lines_out_reserved = (
                        reserved_moves_out_siblings | moves_out_siblings_to_consider
                    ).mapped("move_line_ids")
                    keys_out_groupby = [
                        "location_id",
                        "lot_id",
                        "package_id",
                        "owner_id",
                    ]

                    def _keys_out_sorted(ml):
                        return (
                            ml.location_id.id,
                            ml.lot_id.id,
                            ml.package_id.id,
                            ml.owner_id.id,
                        )

                    grouped_move_lines_out = {}
                    for k, g in groupby(
                        sorted(move_lines_out_done, key=_keys_out_sorted),
                        key=itemgetter(*keys_out_groupby),
                    ):
                        qty_done = 0
                        for ml in g:
                            qty_done += ml.product_uom_id._compute_quantity(
                                ml.qty_done, ml.product_id.uom_id
                            )
                        grouped_move_lines_out[k] = qty_done
                    for k, g in groupby(
                        sorted(move_lines_out_reserved, key=_keys_out_sorted),
                        key=itemgetter(*keys_out_groupby),
                    ):
                        grouped_move_lines_out[k] = sum(
                            self.env["stock.move.line"]
                            .concat(*list(g))
                            .mapped("product_qty")
                        )
                    available_move_lines = {
                        key: grouped_move_lines_in[key]
                        - grouped_move_lines_out.get(key, 0)
                        for key in grouped_move_lines_in.keys()
                    }
                    # pop key if the quantity available amount to 0
                    rounding = move.product_id.uom_id.rounding
                    available_move_lines = {
                        k: v
                        for k, v in available_move_lines.items()
                        if float_compare(v, 0, precision_rounding=rounding) > 0
                    }

                    if not available_move_lines:
                        continue
                    for move_line in move.move_line_ids.filtered(
                        lambda m: m.product_qty
                    ):
                        if available_move_lines.get(
                            (
                                move_line.location_id,
                                move_line.lot_id,
                                move_line.result_package_id,
                                move_line.owner_id,
                            )
                        ):
                            available_move_lines[
                                (
                                    move_line.location_id,
                                    move_line.lot_id,
                                    move_line.result_package_id,
                                    move_line.owner_id,
                                )
                            ] -= move_line.product_qty
                    for (
                        location_id,
                        lot_id,
                        package_id,
                        owner_id,
                    ), quantity in available_move_lines.items():
                        need = move.product_qty - sum(
                            move.move_line_ids.mapped("product_qty")
                        )
                        # `quantity` is what is brought by chained done move lines. We double check
                        # here this quantity is available on the quants themselves. If not, this
                        # could be the result of an inventory adjustment that removed totally of
                        # partially `quantity`. When this happens, we chose to reserve the maximum
                        # still available. This situation could not happen on MTS move, because in
                        # this case `quantity` is directly the quantity on the quants themselves.
                        available_quantity = move._get_available_quantity(
                            location_id,
                            lot_id=lot_id,
                            package_id=package_id,
                            owner_id=owner_id,
                            strict=True,
                        )
                        if float_is_zero(
                            available_quantity, precision_rounding=rounding
                        ):
                            continue
                        taken_quantity = move._update_reserved_quantity(
                            need,
                            min(quantity, available_quantity),
                            location_id,
                            lot_id,
                            package_id,
                            owner_id,
                        )
                        if float_is_zero(taken_quantity, precision_rounding=rounding):
                            continue
                        if float_is_zero(
                            need - taken_quantity, precision_rounding=rounding
                        ):
                            assigned_moves_ids.add(move.id)
                            break
                        partially_available_moves_ids.add(move.id)
            if move.product_id.tracking == "serial":
                move.next_serial_count = move.product_uom_qty

        self.env["stock.move.line"].create(move_line_vals_list)
        StockMove.browse(partially_available_moves_ids).write(
            {"state": "partially_available"}
        )
        StockMove.browse(assigned_moves_ids).write({"state": "assigned"})
        self.mapped("picking_id")._check_entire_pack()
