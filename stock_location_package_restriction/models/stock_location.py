# Copyright 2023 Raumschmiede (http://www.raumschmiede.de)
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import NEGATIVE_TERM_OPERATORS

NOPACKAGE = "nopackage"
SINGLEPACKAGE = "singlepackage"
MULTIPACKAGE = "multiplepackage"


class StockLocation(models.Model):
    _inherit = "stock.location"

    package_restriction = fields.Selection(
        selection=lambda self: self._selection_package_restriction(),
        help="""
            Control if the location can contain products not in a package.

            Options:
              * False (not set): No restriction, the location can contain products
                with and without package
              * Forbidden: The location cannot have products part of a package
              * Mandatory and unique: The location cannot have products not
                part of a package and you cannot have more than 1 package on
                the location
              * Mandatory and not unique:  The location cannot have products
                not part of a package and you may store multiple packages
                on the location
        """,
    )

    @api.model
    def _selection_package_restriction(self):
        return [
            (NOPACKAGE, "Forbidden"),
            (MULTIPACKAGE, "Mandatory"),
            (SINGLEPACKAGE, "Mandatory and unique"),
        ]

    has_package_restriction_violation = fields.Boolean(
        compute="_compute_package_restriction_violation",
        search="_search_has_package_restriction_violation",
    )

    package_restriction_violation_message = fields.Char(
        compute="_compute_package_restriction_violation",
    )

    def _has_package_restriction_violation_query(self):
        self.flush()
        query = """
            SELECT stock_quant.location_id,
            (count(distinct(stock_quant.package_id)) > 1)::bool as has_multiple_packages,
            (count(*) FILTER (WHERE stock_quant.package_id IS NULL) > 0)::bool as has_no_package
            FROM stock_quant
            JOIN stock_location ON stock_location.id = stock_quant.location_id
            WHERE
                quantity != 0
                AND stock_location.package_restriction IS NOT NULL
            """
        if self:
            query += "AND stock_quant.location_id in %s"
        query += f"""
            GROUP BY
                stock_quant.location_id, stock_location.package_restriction
            HAVING
                (
                    stock_location.package_restriction = '{NOPACKAGE}'
                    AND count(distinct(stock_quant.package_id)) > 0
                ) OR (
                    stock_location.package_restriction = '{SINGLEPACKAGE}'
                    AND (
                        count(distinct(stock_quant.package_id)) > 1
                        OR count(*) FILTER (WHERE stock_quant.package_id IS NULL) > 0
                    )
                ) OR (
                    stock_location.package_restriction = '{MULTIPACKAGE}'
                    AND count(*) FILTER (WHERE stock_quant.package_id IS NULL) > 0
                )
        """
        return query

    @api.depends("package_restriction")
    def _compute_package_restriction_violation(self):
        errors = {}
        if self.ids:
            self.env.cr.execute(
                self._has_package_restriction_violation_query(), (tuple(self.ids),)
            )
            errors = {r[0]: r[1:] for r in self.env.cr.fetchall()}
        for location in self:
            error = errors.get(location.id)
            if not error:
                location.has_package_restriction_violation = False
                location.package_restriction_violation_message = False
                continue
            location.has_package_restriction_violation = True
            if location.package_restriction == NOPACKAGE:
                location.package_restriction_violation_message = _(
                    "This location should only contain items without package "
                    "but it contains the package(s): {packages}"
                ).format(
                    packages=", ".join(location.quant_ids.package_id.mapped("name"))
                )
            else:
                messages = []
                has_multiple_package, has_no_package = error
                if has_multiple_package:
                    messages.append(
                        _(
                            "This location should only contain a single package "
                            "but it contains the package(s): {packages}"
                        ).format(
                            packages=", ".join(
                                location.quant_ids.package_id.mapped("name")
                            )
                        )
                    )
                if has_no_package:
                    products = location.quant_ids.filtered(
                        lambda q: not q.package_id
                    ).product_id
                    messages.append(
                        _(
                            "This location should only contain items in a package "
                            "but it contains the items of product(s): {products}"
                        ).format(products=", ".join(products.mapped("name")))
                    )
                location.package_restriction_violation_message = "\n".join(messages)

    def _search_has_package_restriction_violation(self, operator, value):
        search_has_violation = (
            # has_restriction_violation != False
            (operator in NEGATIVE_TERM_OPERATORS and not value)
            # has_restriction_violation = True
            or (operator not in NEGATIVE_TERM_OPERATORS and value)
        )
        self.env.cr.execute(self._has_package_restriction_violation_query())
        error_ids = [r[0] for r in self.env.cr.fetchall()]
        if search_has_violation:
            op = "in"
        else:
            op = "not in"
        return [("id", op, error_ids)]

    def _check_package_restriction(self, move_lines=None):
        """Check if the location respect the package restrictions

        :param move_lines: Optional planned move_line to validate its destination location
        :raises ValidationError: if the restriction is not respected
        """
        error_msgs = []
        move_lines = move_lines or self.env["stock.move.line"]
        for location in self:
            if not location.package_restriction:
                continue
            invalid_products = False
            if location.package_restriction == NOPACKAGE:
                if move_lines:
                    move_lines_with_package = move_lines.filtered("result_package_id")
                    if move_lines_with_package:
                        invalid_products = move_lines_with_package.product_id
                else:
                    quants_with_package = location.quant_ids.filtered(
                        lambda q: q.package_id and q.quantity
                    )
                    if quants_with_package:
                        invalid_products = quants_with_package.product_id
                if invalid_products:
                    error_msgs.append(
                        _(
                            "A package is not allowed on the location {location}."
                            "You cannot move the product(s) {product} with a package."
                        ).format(
                            location=location.display_name,
                            product=", ".join(invalid_products.mapped("display_name")),
                        )
                    )
                continue
            # SINGLE or MULTI
            if move_lines:
                move_lines_without_package = move_lines.filtered(
                    lambda ml: not ml.result_package_id
                )
                if move_lines_without_package:
                    invalid_products = move_lines_without_package.product_id
            else:
                quants_without_package = location.quant_ids.filtered(
                    lambda q: not q.package_id and q.quantity
                )
                if quants_without_package:
                    invalid_products = quants_without_package.product_id
            if invalid_products:
                error_msgs.append(
                    _(
                        "A package is mandatory on the location {location}.\n"
                        "You cannot move the product(s) {product} without a package."
                    ).format(
                        location=location.display_name,
                        product=", ".join(invalid_products.mapped("display_name")),
                    )
                )
                continue
            if location.package_restriction == MULTIPACKAGE:
                continue
            # SINGLE
            packages = (
                move_lines.result_package_id
                | location.quant_ids.filtered("quantity").package_id
            )
            if len(packages) > 1:
                error_msgs.append(
                    _("Only one package is allowed on the location {location}.").format(
                        location=location.display_name
                    )
                )
        if error_msgs:
            raise ValidationError("\n".join(error_msgs))
