# Copyright 2020 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import unicodedata
from collections import namedtuple

from odoo import api, models
from odoo.tools import float_compare

from odoo.addons.base_sparse_field.models.fields import Serialized

# Unify records as we mix up w/ UoM
Packaging = namedtuple("Packaging", "id name qty barcode is_unit")

NO_BREAK_SPACE_CHAR = unicodedata.lookup("NO-BREAK SPACE")


class Product(models.Model):
    _inherit = "product.product"

    packaging_contained_mapping = Serialized(
        compute="_compute_packaging_contained_mapping",
        help="Technical field to store contained packaging. ",
    )

    @api.depends_context("lang")
    @api.depends("packaging_ids.qty")
    def _compute_packaging_contained_mapping(self):
        for rec in self:
            rec.packaging_contained_mapping = rec._packaging_contained_mapping()

    def _packaging_contained_mapping(self):
        """Produce a mapping of packaging and contained packagings.

        Used mainly for `product_qty_by_packaging` but can be used
        to display info as you prefer.

        :returns: a dictionary in the form {pkg.id: [contained packages]}
        """
        res = {}
        packaging = self._ordered_packaging()
        for i, pkg in enumerate(packaging):
            if pkg.is_unit:
                # skip minimal unit
                continue
            res[pkg.id] = self._product_qty_by_packaging(packaging[i + 1 :], pkg.qty)
        return res

    def product_qty_by_packaging(self, prod_qty, with_contained=False):
        """Calculate quantity by packaging.

        The minimal quantity is always represented by the UoM of the product.

        Limitation: fractional quantities are lost.

        :prod_qty: total qty to satisfy.
        :with_contained: include calculation of contained packagings.

            eg: 1 pallet contains 4 big boxes and 6 little boxes.

        :returns: list of dict in the form

            [{id: 1, qty: qty_per_package, name: package_name}]

            If `with_contained` is passed, each element will include
            the quantity of smaller packaging, like:

            {contained: [{id: 1, qty: 4, name: "Big box"}]}
        """
        self.ensure_one()
        return self._product_qty_by_packaging(
            self._ordered_packaging(),
            prod_qty,
            with_contained=with_contained,
        )

    def _ordered_packaging(self):
        """Prepare packaging ordered by qty and exclude empty ones.

        Use ctx key `_packaging_filter` to pass a function to filter packaging
        to be considered.

        Use ctx key `_packaging_name_getter` to pass a function to change
        the display name of the packaging.
        """
        custom_filter = self.env.context.get("_packaging_filter", lambda x: x)
        name_getter = self.env.context.get(
            "_packaging_name_getter", self._packaging_name_getter
        )
        packagings = sorted(
            [
                Packaging(x.id, name_getter(x), x.qty, x.barcode, False)
                for x in self.packaging_ids.filtered(custom_filter)
                # Exclude the ones w/ zero qty as they are useless for the math
                if x.qty
            ],
            reverse=True,
            key=lambda x: x.qty,
        )
        # Add minimal unit
        packagings.append(
            # NOTE: the ID here could clash w/ one of the packaging's.
            # If you create a mapping based on IDs, keep this in mind.
            # You can use `is_unit` to check this.
            Packaging(self.uom_id.id, self.uom_id.name, self.uom_id.factor, None, True)
        )
        return packagings

    def _packaging_name_getter(self, packaging):
        return packaging.name

    def _product_qty_by_packaging(self, pkg_by_qty, qty, with_contained=False):
        """Produce a list of dictionaries of packaging info."""
        # TODO: refactor to handle fractional quantities (eg: 0.5 Kg)
        res = []
        prepare_values = self.env.context.get(
            "_packaging_values_handler", self._prepare_qty_by_packaging_values
        )
        for pkg in pkg_by_qty:
            qty_per_pkg, qty = self._qty_by_pkg(pkg.qty, qty)
            if qty_per_pkg:
                value = prepare_values(pkg, qty_per_pkg)
                if with_contained:
                    contained = None
                    if not pkg.is_unit:
                        mapping = self.packaging_contained_mapping
                        # integer keys are serialized as strings :/
                        contained = mapping.get(str(pkg.id))
                    value["contained"] = contained
                res.append(value)
            if not qty:
                break
        return res

    def _qty_by_pkg(self, pkg_qty, qty):
        """Calculate qty needed for given package qty."""
        qty_per_pkg = 0
        while (
            float_compare(qty - pkg_qty, 0.0, precision_digits=self.uom_id.rounding)
            >= 0.0
        ):
            qty -= pkg_qty
            qty_per_pkg += 1
        return qty_per_pkg, qty

    def _prepare_qty_by_packaging_values(self, packaging, qty_per_pkg):
        return {
            "id": packaging.id,
            "qty": qty_per_pkg,
            "name": packaging.name,
            "is_unit": packaging.is_unit,
            "barcode": packaging.barcode,
        }

    def product_qty_by_packaging_as_str(
        self, prod_qty, include_total_units=False, only_packaging=False
    ):
        """Return a string representing the qty of each packaging.

        :param prod_qty: the qty of current product to translate to pkg qty
        :param include_total_units: includes total qty required initially
        :param only_packaging: exclude units if you have only units.
            IOW: if the qty does not match any packaging and this flag is true
            you'll get an empty string instead of `N units`.
        """
        self.ensure_one()
        if not prod_qty:
            return ""

        qty_by_packaging = self.product_qty_by_packaging(prod_qty)
        if not qty_by_packaging:
            return ""

        # Exclude unit qty and reuse it later
        unit_qty = None
        has_only_units = True
        _qty_by_packaging = []
        for pkg_qty in qty_by_packaging:
            if pkg_qty["is_unit"]:
                unit_qty = pkg_qty["qty"]
                continue
            has_only_units = False
            _qty_by_packaging.append(pkg_qty)
        # Browse them all at once
        records = self.env["product.packaging"].browse(
            [x["id"] for x in _qty_by_packaging]
        )
        _qty_by_packaging_as_str = self.env.context.get(
            "_qty_by_packaging_as_str", self._qty_by_packaging_as_str
        )
        # Collect all strings representations
        as_string = []
        for record, info in zip(records, _qty_by_packaging):
            bit = _qty_by_packaging_as_str(record, info["qty"])
            if bit:
                as_string.append(bit)
        # Restore unit information if any.
        include_units = (has_only_units and not only_packaging) or not has_only_units
        if unit_qty and include_units:
            as_string.append(f"{unit_qty} {self.uom_id.name}")
        # We want to avoid line break here as this string
        # can be used by reports
        res = f",{NO_BREAK_SPACE_CHAR}".join(as_string)
        if include_total_units and not has_only_units:
            res += " " + self._qty_by_packaging_total_units(prod_qty)
        return res

    def _qty_by_packaging_as_str(self, packaging, qty):
        return f"{qty} {packaging.name}"

    def _qty_by_packaging_total_units(self, prod_qty):
        return f"({prod_qty} {self.uom_id.name})"
