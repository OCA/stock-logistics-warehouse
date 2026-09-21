# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = "stock.quant"

    being_filled_before_done_location_ids = fields.One2many(
        comodel_name="stock.location",
        compute="_compute_being_filled_before_done_location_ids",
        help="Technical field to compute locations with their fill state"
        "at 'Being Filled' before they'll be filled with an incoming move.",
    )

    @api.depends_context("being_filled_locations_before_update")
    @api.depends("location_id")
    def _compute_being_filled_before_done_location_ids(self):
        self.being_filled_before_done_location_ids = self.env["stock.location"].browse(
            self.env.context.get("being_filled_locations_before_update", [])
        )

    @api.model
    def _update_available_quantity(
        self,
        product_id,
        location_id,
        quantity,
        lot_id=None,
        package_id=None,
        owner_id=None,
        in_date=None,
    ):
        new_self = self.with_context(
            being_filled_locations_before_update=location_id.filtered(
                lambda location: location.fill_state == "being_filled"
            ).ids
        )
        return super(StockQuant, new_self)._update_available_quantity(
            product_id=product_id,
            location_id=location_id,
            quantity=quantity,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            in_date=in_date,
        )

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
            if location_id in self.being_filled_before_done_location_ids.ids:
                continue
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
        self.env["stock.location"].flush_model(
            [
                "fill_state",
            ]
        )
        SQL = """
            SELECT
                stock_quant.location_id,
                array_agg(distinct(product_id))
            FROM
                stock_quant,
                stock_location
            WHERE
                stock_quant.location_id in %s
                and stock_quant.location_id = stock_location.id
                and stock_location.fill_state NOT IN ('being_filled', 'being_emptied')
            /* Mimic the _unlink_zero_quant() query in Odoo */
            AND (NOT (round(quantity::numeric, %s) = 0 OR quantity IS NULL)
            OR NOT round(reserved_quantity::numeric, %s) = 0
            OR NOT (round(inventory_quantity::numeric, %s) = 0
                    OR inventory_quantity IS NULL))
            GROUP BY
                stock_quant.location_id
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
            if location_id in self.being_filled_before_done_location_ids.ids:
                continue
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
