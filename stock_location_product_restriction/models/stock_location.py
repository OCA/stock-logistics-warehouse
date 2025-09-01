# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.osv.expression import NEGATIVE_TERM_OPERATORS


class StockLocation(models.Model):

    _inherit = "stock.location"

    product_restriction = fields.Selection(
        selection=lambda self: self._selection_product_restriction(),
        help="If 'Same product' is selected the system will prevent to put "
        "items of different products into the same location.",
        index=True,
        required=True,
        compute="_compute_product_restriction",
        store=True,
        default="any",
        recursive=True,
    )

    specific_product_restriction = fields.Selection(
        selection=lambda self: self._selection_product_restriction(),
        help="If specified the restriction specified will apply to "
        "the current location and all its children",
        default=False,
    )

    parent_product_restriction = fields.Selection(
        string="Parent Location Product Restriction",
        store=True,
        readonly=True,
        related="location_id.product_restriction",
        recursive=True,
    )

    has_restriction_violation = fields.Boolean(
        compute="_compute_restriction_violation",
        search="_search_has_restriction_violation",
        recursive=True,
    )

    restriction_violation_message = fields.Char(
        compute="_compute_restriction_violation",
        recursive=True,
    )

    @api.model
    def _get_product_restriction_query(self):
        SQL = """
           SELECT
               stock_quant.location_id,
               array_agg(distinct(product_id))
           FROM
               stock_quant,
               stock_location
           WHERE
               stock_quant.location_id in %s
               and stock_location.id = stock_quant.location_id
               and stock_location.product_restriction = 'same'
               and stock_location.fill_state NOT IN ('being_filled', 'being_emptied')
               /* Mimic the _unlink_zero_quant() query in Odoo */
                AND (NOT (round(quantity::numeric, %s) = 0 OR quantity IS NULL)
                OR NOT round(reserved_quantity::numeric, %s) = 0
                OR NOT (round(inventory_quantity::numeric, %s) = 0
                        OR inventory_quantity IS NULL))
           GROUP BY
               stock_quant.location_id
        """
        return SQL

    @api.model
    def _get_product_restriction_query_having(self):
        return """
            HAVING count(distinct(product_id)) > 1
        """

    @api.model
    def _selection_product_restriction(self):
        return [
            ("any", "Items of any products are allowed into the location"),
            (
                "same",
                "Only items of the same product allowed into the location",
            ),
        ]

    @api.depends("specific_product_restriction", "parent_product_restriction")
    def _compute_product_restriction(self):
        default_value = "any"
        for rec in self:
            rec.product_restriction = (
                rec.specific_product_restriction
                or rec.parent_product_restriction
                or default_value
            )

    def _check_has_location_product_restriction(self, product):
        """
        Call this if you want to check if product can
        enter a location.
        """
        product_ids_by_location_id = self._get_product_ids_by_locations()
        for location in self:
            product_ids = product_ids_by_location_id.get(location.id)
            if product_ids and product.id not in product_ids:
                return True
        return False

    def _get_product_ids_by_locations(self):
        self.env["stock.quant"].flush_model(
            [
                "product_id",
                "location_id",
                "quantity",
                "reserved_quantity",
                "available_quantity",
                "inventory_quantity",
            ]
        )
        self.flush_model(["product_restriction", "fill_state"])

        precision_digits = max(
            6, self.sudo().env.ref("product.decimal_product_uom").digits * 2
        )
        SQL = SQL = self._get_product_restriction_query()
        # Browse only real record ids
        ids = tuple(
            [record.id for record in self if not isinstance(record.id, fields.NewId)]
        )
        if not ids:
            product_ids_by_location_id = dict()
        else:
            self.env.cr.execute(
                SQL, (ids, precision_digits, precision_digits, precision_digits)
            )
            product_ids_by_location_id = dict(self.env.cr.fetchall())
        return product_ids_by_location_id

    @api.depends("product_restriction")
    def _compute_restriction_violation(self):
        records = self
        self.env["stock.quant"].flush_model(
            [
                "product_id",
                "location_id",
                "quantity",
                "reserved_quantity",
                "available_quantity",
                "inventory_quantity",
            ]
        )
        self.flush_model(["product_restriction", "fill_state"])
        ProductProduct = self.env["product.product"]
        precision_digits = max(
            6, self.sudo().env.ref("product.decimal_product_uom").digits * 2
        )

        SQL = self._get_product_restriction_query()
        SQL += self._get_product_restriction_query_having()
        # Browse only real record ids
        ids = tuple(
            [record.id for record in records if not isinstance(record.id, fields.NewId)]
        )
        if not ids:
            product_ids_by_location_id = dict()
        else:
            self.env.cr.execute(
                SQL, (ids, precision_digits, precision_digits, precision_digits)
            )
            product_ids_by_location_id = dict(self.env.cr.fetchall())
        for record in self:
            record_id = record.id
            has_restriction_violation = False
            restriction_violation_message = ""
            product_ids = product_ids_by_location_id.get(record_id)
            if product_ids:
                products = ProductProduct.browse(product_ids)
                has_restriction_violation = True
                restriction_violation_message = _(
                    "This location should only contain items of the same "
                    "product but it contains items of products %(products)s",
                    products=" | ".join(products.mapped("name")),
                )
            record.has_restriction_violation = has_restriction_violation
            record.restriction_violation_message = restriction_violation_message

    def _search_has_restriction_violation(self, operator, value):
        precision_digits = max(
            6, self.sudo().env.ref("product.decimal_product_uom").digits * 2
        )
        search_has_violation = (
            # has_restriction_violation != False
            (operator in NEGATIVE_TERM_OPERATORS and not value)
            # has_restriction_violation = True
            or (operator not in NEGATIVE_TERM_OPERATORS and value)
        )
        self.env["stock.quant"].flush_model(
            [
                "product_id",
                "location_id",
                "quantity",
                "reserved_quantity",
                "available_quantity",
                "inventory_quantity",
            ]
        )
        self.flush_model(["product_restriction", "fill_state"])
        SQL = """
            SELECT
                stock_quant.location_id
            FROM
               stock_quant,
               stock_location
            WHERE
               stock_location.id = stock_quant.location_id
               and stock_location.product_restriction = 'same'
               and stock_location.fill_state NOT IN ('being_filled', 'being_emptied')
               /* Mimic the _unlink_zero_quant() query in Odoo */
                AND (NOT (round(quantity::numeric, %s) = 0 OR quantity IS NULL)
                OR NOT round(reserved_quantity::numeric, %s) = 0
                OR NOT (round(inventory_quantity::numeric, %s) = 0
                        OR inventory_quantity IS NULL))
            GROUP BY
               stock_quant.location_id
            HAVING count(distinct(product_id)) > 1
        """
        self.env.cr.execute(
            SQL,
            (
                precision_digits,
                precision_digits,
                precision_digits,
            ),
        )
        violation_ids = [r[0] for r in self.env.cr.fetchall()]
        if search_has_violation:
            op = "in"
        else:
            op = "not in"
        return [("id", op, violation_ids)]
