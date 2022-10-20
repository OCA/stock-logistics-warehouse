# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):

    _inherit = "stock.move"

    def _check_location_product_restriction(self):
        """
        Check if the move can be executed according to potential restriction
        defined on the stock_location
        """
        StockLocation = self.env["stock.location"]
        ProductProduct = self.env["product.product"]
        # We only check moves with a location_dest that can
        # only contain the same product
        moves_to_ckeck = self.filtered(
            lambda m: m.location_dest_id.product_restriction == "same"
        )
        if not moves_to_ckeck:
            return
        product_ids_location_dest_id = defaultdict(set)
        error_msgs = []
        # check dest locations into the stock moves
        for move in moves_to_ckeck:
            product_ids_location_dest_id[move.location_dest_id.id].add(
                move.product_id.id
            )
        for location_id, product_ids in product_ids_location_dest_id.items():
            if len(product_ids) > 1:
                location = StockLocation.browse(location_id)
                products = ProductProduct.browse(list(product_ids))
                error_msgs.append(
                    _(
                        "The location {location} can only contain items of the same "
                        "product. You plan to move different products to "
                        "this location. ({products})"
                    ).format(
                        location=location.name,
                        products=", ".join(products.mapped("name")),
                    )
                )

        # check dest locations by taking into account product already into the
        # locations
        # here we use a plain SQL to avoid performance issue
        SQL = """
            SELECT
                location_id,
                array_agg(distinct(product_id))
            FROM
                stock_quant
            WHERE
                location_id in %s
            GROUP BY
                location_id
        """
        self.env.cr.execute(
            SQL, (tuple(moves_to_ckeck.mapped("location_dest_id").ids),)
        )
        existing_product_ids_by_location_id = dict(self.env.cr.fetchall())
        for (
            location_dest_id,
            existing_product_ids,
        ) in existing_product_ids_by_location_id.items():
            product_ids_to_move = product_ids_location_dest_id[location_dest_id]
            if set(existing_product_ids).symmetric_difference(product_ids_to_move):
                location = StockLocation.browse(location_dest_id)
                existing_products = ProductProduct.browse(existing_product_ids)
                to_move_products = ProductProduct.browse(list(product_ids_to_move))
                error_msgs.append(
                    _(
                        "You plan to move the product {product} to the location {location} "
                        "but the location must only contain items of same "
                        "product and already contains items of other "
                        "product(s) "
                        "({existing_products})."
                    ).format(
                        product=" | ".join(to_move_products.mapped("name")),
                        location=location.name,
                        existing_products=" | ".join(existing_products.mapped("name")),
                    )
                )
        if error_msgs:
            raise ValidationError("\n".join(error_msgs))

    def _action_done(self, cancel_backorder=False):
        self._check_location_product_restriction()
        return super()._action_done(cancel_backorder=cancel_backorder)
