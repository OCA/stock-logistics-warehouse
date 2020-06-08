# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from collections import namedtuple

from odoo import models
from odoo.tools import float_compare

# Unify records as we mix up w/ UoM
Packaging = namedtuple("Packaging", "id name qty")


class Product(models.Model):
    _inherit = "product.product"

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
        packagings = [Packaging(x.id, x.name, x.qty) for x in self.packaging_ids]
        # Add minimal unit
        packagings.append(
            # NOTE: the ID here could clash w/ one of the packaging's.
            # If you create a mapping based on IDs, keep this in mind.
            Packaging(self.uom_id.id, self.uom_id.name, self.uom_id.factor)
        )
        return self._product_qty_by_packaging(
            sorted(packagings, reverse=True, key=lambda x: x.qty),
            prod_qty,
            with_contained=with_contained,
        )

    def _product_qty_by_packaging(self, pkg_by_qty, qty, with_contained=False):
        """Produce a list of dictionaries of packaging info."""
        # TODO: refactor to handle fractional quantities (eg: 0.5 Kg)
        res = []
        for i, pkg in enumerate(pkg_by_qty):
            qty_per_pkg, qty = self._qty_by_pkg(pkg.qty, qty)
            if qty_per_pkg:
                value = {"id": pkg.id, "qty": qty_per_pkg, "name": pkg.name}
                if with_contained:
                    value["contained"] = self._product_qty_by_packaging(
                        pkg_by_qty[i + 1 :], pkg.qty
                    )
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
