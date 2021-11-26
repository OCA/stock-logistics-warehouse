# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import contextlib
from collections import namedtuple

from odoo.tools import float_compare

from odoo import api, fields, models
from .. import context

Packaging = namedtuple("Packaging", "id name qty is_unit")

_packaging_filter_ctx = context.ContextVar("packaging_filter", None)
_packaging_name_getter_ctx = context.ContextVar("packaging_name_getter", None)
_packaging_values_handler_ctx = context.ContextVar(
    "packaging_values_handler", None
)

_UNDEFINED = object()


class ProductProduct(models.Model):

    _inherit = "product.product"

    packaging_contained_mapping = fields.Serialized(
        compute="_compute_packaging_contained_mapping",
        help="Technical field to store contained packaging. ",
    )

    @api.depends("packaging_ids.qty")
    def _compute_packaging_contained_mapping(self):
        for rec in self:
            rec.packaging_contained_mapping = (
                rec._packaging_contained_mapping()
            )

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
            res[str(pkg.id)] = self._product_qty_by_packaging(
                packaging[i + 1 :], pkg.qty
            )
        return res

    @contextlib.contextmanager
    @api.model
    def product_qty_by_packaging_arg_ctx(
        self,
        packaging_filter=_UNDEFINED,
        packaging_name_getter=_UNDEFINED,
        packaging_values_handler=_UNDEFINED,
    ):
        """
        Use `packaging_filter` to pass a function to filter packaging
        to be considered.

        Use `packaging_name_getter` to pass a function to change
        the display name of the packaging.
        """
        try:
            token_packaging_filter = None
            token_packaging_name_getter = None
            token_packaging_values_handler = None
            if packaging_filter != _UNDEFINED:
                token_packaging_filter = _packaging_filter_ctx.set(
                    packaging_filter
                )
            if packaging_name_getter != _UNDEFINED:
                token_packaging_name_getter = _packaging_name_getter_ctx.set(
                    packaging_name_getter
                )
            if packaging_values_handler != _UNDEFINED:
                token_packaging_values_handler = _packaging_values_handler_ctx.set(
                    packaging_values_handler
                )
            yield
        finally:
            if token_packaging_values_handler:
                _packaging_values_handler_ctx.reset(
                    token_packaging_values_handler
                )
            if token_packaging_name_getter:
                _packaging_name_getter_ctx.reset(token_packaging_name_getter)
            if token_packaging_filter:
                _packaging_filter_ctx.reset(token_packaging_filter)

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
            self._ordered_packaging(), prod_qty, with_contained=with_contained,
        )

    def _ordered_packaging(self):
        """Prepare packaging ordered by qty and exclude empty ones.

        Use product_qty_by_packaging_arg_ctx context manager to
        provide custom_getter and name_getter for collected packaging
        """
        custom_filter = _packaging_filter_ctx.get(lambda x: x)
        name_getter = _packaging_name_getter_ctx.get(lambda x: x.name)
        packagings = sorted(
            [
                Packaging(x.id, name_getter(x), x.qty, False)
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
            Packaging(
                self.uom_id.id, self.uom_id.name, self.uom_id.factor, True
            )
        )
        return packagings

    def _product_qty_by_packaging(self, pkg_by_qty, qty, with_contained=False):
        """Produce a list of dictionaries of packaging info."""
        res = []
        prepare_values = _packaging_values_handler_ctx.get(
            self._prepare_qty_by_packaging_values
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
                if 0 < qty < 1:
                    unit_pkg = prepare_values(pkg_by_qty[-1], 1)
                    res.append(unit_pkg)
            if not qty:
                break
        return res

    def _qty_by_pkg(self, pkg_qty, qty):
        """Calculate qty needed for given package qty."""
        qty_per_pkg = 0
        while (
            float_compare(
                qty - pkg_qty, 0.0, precision_digits=self.uom_id.rounding
            )
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
        }
