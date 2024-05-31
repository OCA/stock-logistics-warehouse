# Copyright 2023 Raumschmiede (http://www.raumschmiede.de)
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

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
