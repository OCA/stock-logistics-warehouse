# Copyright 2020-2021 Camptocamp SA (http://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockLocation(models.Model):
    _inherit = "stock.location"

    def is_sublocation_of(self, others, func=any):
        """Return True if self is a sublocation of others (or equal)

        By default, it return True if any other is a parent or equal.
        ``all`` can be passed to ``func`` to require all the other locations
        to be parent or equal to be True.
        """
        self.ensure_one()
        # Efficient way to verify that the current location is
        # below one of the other location without using SQL.
        return func(self.parent_path.startswith(other.parent_path) for other in others)
