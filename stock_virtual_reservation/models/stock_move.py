# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.osv import expression


class StockMove(models.Model):
    _inherit = "stock.move"

    def _virtual_quantity_domain(
        self,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        domain = [
            ("state", "in", ("draft", "confirmed", "partially_available")),
            ("product_id", "=", self.product_id.id),
            ("date", "<=", self.date),
        ]

        def augment(domain, field_name, value, operator="="):
            domain = domain[:]
            if value:
                fragment = (field_name, operator, value.id)
                domain = expression.AND([[fragment], domain])
            return domain

        def augment_s(domain, field_name, value):
            domain = domain[:]
            fragment = (field_name, "=", value.id if value else False)
            domain = expression.AND([[fragment], domain])
            return domain

        if not strict:
            domain = augment(domain, "lot_id", lot_id)
            domain = augment(domain, "package_id", package_id)
            domain = augment(domain, "owner_id", owner_id)
            domain = augment(
                domain, "location_id", owner_id, operator="child_of"
            )
        else:
            domain = augment_s(domain, "lot_id", lot_id)
            domain = augment_s(domain, "package_id", package_id)
            domain = augment_s(domain, "owner_id", owner_id)
            domain = augment_s(domain, "location_id", location_id)
        return domain

    def _update_reserved_quantity(
        self,
        need,
        available_quantity,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        previous_moves = self.search(
            expression.AND(
                [
                    self._virtual_quantity_domain(
                        location_id,
                        lot_id=lot_id,
                        package_id=package_id,
                        owner_id=owner_id,
                        strict=strict,
                    ),
                    [("id", "!=", self.id)],
                ]
            )
        )
        virtual_reserved = sum(
            previous_moves.mapped(
                lambda move: max(
                    move.product_qty - move.reserved_availability, 0.
                )
            )
        )
        available_quantity = max(available_quantity - virtual_reserved, 0.)
        return super()._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
