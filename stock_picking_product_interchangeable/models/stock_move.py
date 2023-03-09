from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_interchangeable_products(self, mode, for_qty):
        """
        Preparing products for current product replacement
        :param mode: stock.picking.type substitute_products_mode value
        :param for_qty: product qty for replacement
        :return: list of tuple [(product_obj, count), ...]
        """
        qty = for_qty
        if qty >= 0:
            return False
        products_info = []
        for product in self.product_id.product_interchangeable_ids:
            available_qty = product.immediately_usable_qty
            if available_qty > 0 > qty:
                product_qty = abs(qty) if available_qty + qty >= 0 else available_qty
                products_info.append((product, product_qty))
                qty += product_qty
        if (mode == "all" and qty == 0) or mode == "any":
            return products_info
        return False

    def _create_stock_move_interchangeable_products(self, products_info):
        """
        Creates stock.move records for replacement product
        :param products_info: struct list of tuple [(product_obj, count), ...]
        :return: Stock Move object
        """
        stock_move_obj = self.env["stock.move"]
        if not products_info:
            return stock_move_obj
        return stock_move_obj.create(
            [
                {
                    "picking_id": self.picking_id.id,
                    "name": product.display_name,
                    "product_id": product.id,
                    "product_uom_qty": qty,
                    "location_id": self.location_id.id,
                    "location_dest_id": self.location_dest_id.id,
                    "company_id": self.company_id.id,
                }
                for product, qty in products_info
            ]
        )

    def _interchangeable_stock_move_filter(self):
        """
        Filter for applying interchangeable behavior for stock.move
        :return: True/False
        """
        type_ = self.picking_type_id
        mode = type_.substitute_products_mode
        skip_behavior = not (mode and type_.code == "outgoing")
        return not (skip_behavior or self.picking_id.pass_interchangeable)

    def _add_note_interchangeable_picking_note(self, products_info, qty):
        """
        Add note for product with interchangeable products
        :param list products_info: struct list of tuple [(product_obj, count), ...]
        """
        self.ensure_one()
        product = self.product_id
        qty = abs(qty)
        note = rf"<b>{product.display_name}</b> missing qty <i>{qty}</i> was replaced with:<br\>"  # noqa
        lines = [
            f"<li><b>{product.display_name}</b> <i>{qty}</i></li>"
            for product, qty in products_info
        ]
        note += f"<ul>{''.join(lines)}</ul><br/>"
        picking = self.picking_id
        if not picking.note:
            picking.note = note
        else:
            picking.note += note

    def _action_confirm(self, merge=True, merge_into=False):
        moves = super(StockMove, self)._action_confirm(
            merge=merge, merge_into=merge_into
        )
        inter_moves = moves.filtered(
            lambda move: move._interchangeable_stock_move_filter()
        )
        if not inter_moves:
            return moves
        other_moves = moves - inter_moves
        move_ids = inter_moves.filtered(
            lambda m: m.product_id.product_interchangeable_ids
        )
        new_moves = self.env["stock.move"]
        for move in move_ids:
            mode = move.picking_type_id.substitute_products_mode
            qty = move.product_id.immediately_usable_qty
            products_info = move._prepare_interchangeable_products(mode, qty)
            if products_info:
                products_qty = sum(map(lambda item: item[1], products_info))
                new_moves = move._create_stock_move_interchangeable_products(
                    products_info
                )
                new_moves |= new_moves._action_confirm(merge, merge_into)
                move.product_uom_qty -= products_qty
                move._add_note_interchangeable_picking_note(products_info, qty)
        return inter_moves | new_moves | other_moves
