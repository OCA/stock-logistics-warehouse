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
        products_info = []

        if qty >= 0:
            return False

        for product_id in self.product_id.product_interchangeable_ids:
            available_qty = product_id.immediately_usable_qty

            if available_qty > 0 > qty:
                product_qty = abs(qty) if available_qty + qty >= 0 else available_qty

                products_info.append((product_id, product_qty))
                qty += product_qty

        if mode == "any" or (mode == "all" and qty == 0):
            return products_info

        return False

    def _create_stock_move_interchangeable_products(self, products_info):
        """
        Creates stock.move records for replacement product
        :param products_info: struct list of tuple [(product_obj, count), ...]
        :return: Stock Move object
        """
        if not products_info:
            return self.env["stock.move"]

        return self.env["stock.move"].create(
            [
                {
                    "picking_id": self.picking_id.id,
                    "name": product_id.display_name,
                    "product_id": product_id.id,
                    "product_uom_qty": qty,
                    "location_id": self.location_id.id,
                    "location_dest_id": self.location_dest_id.id,
                    "company_id": self.company_id.id,
                }
                for product_id, qty in products_info
            ]
        )

    def _interchangeable_stock_move_filter(self):
        """
        Filter for applying interchangeable behavior for stock.move
        :return: True/False
        """
        picking_type_id = self.picking_type_id

        return not (
            not (
                picking_type_id.substitute_products_mode
                and picking_type_id.code == "outgoing"
            )
            or self.picking_id.pass_interchangeable
        )

    def _add_note_interchangeable_picking_note(
        self,
        products_info,
        qty,
    ):
        """Add interchangeable products note to picking."""
        self.ensure_one()

        lines = "".join(
            f"<li><b>{product.display_name}</b> <i>{qty}</i></li>"
            for product, qty in products_info
        )

        self.picking_id.note = (
            f'{self.picking_id.note or ""}'
            rf'<b>{self.product_id.display_name}</b> missing qty '
            rf'<i>{abs(qty)}</i> was replaced with:<br\>'
            f'<ul>{lines}</ul><br/>'
        )

    def _action_confirm(self, merge=True, merge_into=False):
        move_ids = super()._action_confirm(
            merge=merge,
            merge_into=merge_into,
        )

        inter_move_ids = move_ids.filtered(
            lambda m_id: m_id._interchangeable_stock_move_filter()
        )

        if not inter_move_ids:
            return move_ids

        new_move_ids = self.env["stock.move"]

        for move_id in inter_move_ids.filtered(
            lambda m_id: m_id.product_id.product_interchangeable_ids
        ):
            qty = move_id.product_id.immediately_usable_qty

            if products_info := move_id._prepare_interchangeable_products(
                move_id.picking_type_id.substitute_products_mode,
                qty,
            ):
                new_move_ids = move_id._create_stock_move_interchangeable_products(
                    products_info
                )
                new_move_ids |= new_move_ids._action_confirm(
                    merge,
                    merge_into,
                )
                move_id.product_uom_qty -= sum(map(lambda item: item[1], products_info))
                move_id._add_note_interchangeable_picking_note(
                    products_info,
                    qty,
                )

        return inter_move_ids | new_move_ids | move_ids - inter_move_ids
