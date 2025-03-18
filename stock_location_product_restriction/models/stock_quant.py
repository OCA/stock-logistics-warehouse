# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockQuant(models.Model):

    _inherit = "stock.quant"

    @api.constrains("location_id", "product_id")
    def _check_location_product_restriction(self):
        """
        Check if the quant can be put into the location according to restriction
        defined on the stock_location
        """
        StockLocation = self.env["stock.location"]
        ProductProduct = self.env["product.product"]
        # We only check quants with a location_id that can
        # only contain the same product
        quants_to_check = self.filtered(
            lambda q: q.location_id.product_restriction == "same"
        )
        if not quants_to_check:
            return
        product_ids_location_id = defaultdict(set)
        error_msgs = []
        for quant in quants_to_check:
            product_ids_location_id[quant.location_id.id].add(quant.product_id.id)
        for location_id, product_ids in product_ids_location_id.items():
            if len(product_ids) > 1:
                location = StockLocation.browse(location_id)
                products = ProductProduct.browse(list(product_ids))
                error_msgs.append(
                    _(
                        "The location %(location)s can only contain items of the same "
                        "product. You plan to put different products into "
                        "this location. (%(products)s)",
                        location=location.name,
                        products=", ".join(products.mapped("name")),
                    )
                )
        # Get existing product already in the locations
        precision_digits = max(
            6, self.sudo().env.ref("product.decimal_product_uom").digits * 2
        )
        self.flush_model(
            [
                "product_id",
                "location_id",
                "quantity",
                "reserved_quantity",
                "available_quantity",
                "inventory_quantity",
            ]
        )
        SQL = """
            SELECT
                location_id,
                array_agg(distinct(product_id))
            FROM
                stock_quant
            WHERE
                location_id in %s
            /* Mimic the _unlink_zero_quant() query in Odoo */
            AND (NOT (round(quantity::numeric, %s) = 0 OR quantity IS NULL)
            OR NOT round(reserved_quantity::numeric, %s) = 0
            OR NOT (round(inventory_quantity::numeric, %s) = 0
                    OR inventory_quantity IS NULL))
            GROUP BY
                location_id
        """
        self.env.cr.execute(
            SQL,
            (
                tuple(quants_to_check.mapped("location_id").ids),
                precision_digits,
                precision_digits,
                precision_digits,
            ),
        )
        existing_product_ids_by_location_id = dict(self.env.cr.fetchall())

        for (
            location_id,
            existing_product_ids,
        ) in existing_product_ids_by_location_id.items():
            product_ids_to_add = product_ids_location_id[location_id]
            if set(existing_product_ids).symmetric_difference(product_ids_to_add):
                location = StockLocation.browse(location_id)
                existing_products = ProductProduct.browse(existing_product_ids)
                to_move_products = ProductProduct.browse(list(product_ids_to_add))
                error_msgs.append(
                    _(
                        "You plan to add the product %(product)s into the location"
                        " %(location)s "
                        "but the location must only contain items of same "
                        "product and already contains items of other "
                        "product(s) "
                        "(%(existing_products)s).",
                        product=" | ".join(to_move_products.mapped("name")),
                        location=location.name,
                        existing_products=" | ".join(existing_products.mapped("name")),
                    )
                )

        if error_msgs:
            raise ValidationError("\n".join(error_msgs))
