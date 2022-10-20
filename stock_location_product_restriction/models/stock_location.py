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

    @api.depends("product_restriction")
    def _compute_restriction_violation(self):
        records = self
        ProductProduct = self.env["product.product"]
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
           GROUP BY
               stock_quant.location_id
            HAVING count(distinct(product_id)) > 1
       """
        self.env.cr.execute(SQL, (tuple(records.ids),))
        product_ids_by_location_id = dict(self.env.cr.fetchall())
        for record in self:
            record_id = record.id
            has_restriction_violation = False
            restriction_violation_message = False
            product_ids = product_ids_by_location_id.get(record_id)
            if product_ids:
                products = ProductProduct.browse(product_ids)
                has_restriction_violation = True
                restriction_violation_message = _(
                    "This location should only contain items of the same "
                    "product but it contains items of products {products}"
                ).format(products=" | ".join(products.mapped("name")))
            record.has_restriction_violation = has_restriction_violation
            record.restriction_violation_message = restriction_violation_message

    def _search_has_restriction_violation(self, operator, value):
        search_has_violation = (
            # has_restriction_violation != False
            (operator in NEGATIVE_TERM_OPERATORS and not value)
            # has_restriction_violation = True
            or (operator not in NEGATIVE_TERM_OPERATORS and value)
        )
        SQL = """
            SELECT
                stock_quant.location_id
            FROM
               stock_quant,
               stock_location
            WHERE
               stock_location.id = stock_quant.location_id
               and stock_location.product_restriction = 'same'
            GROUP BY
               stock_quant.location_id
            HAVING count(distinct(product_id)) > 1
        """
        self.env.cr.execute(SQL)
        violation_ids = [r[0] for r in self.env.cr.fetchall()]
        if search_has_violation:
            op = "in"
        else:
            op = "not in"
        return [("id", op, violation_ids)]
