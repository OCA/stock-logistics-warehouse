# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockLocation(models.Model):
    _inherit = "stock.location"

    def _location_parent_tree(self):
        self.ensure_one()
        # Build the tree of parent locations, we don't need SQL
        # at all since the parent ids are all in the parent path.
        tree_ids = [int(tree_id) for tree_id in self.parent_path.rstrip("/").split("/")]
        # the recordset will be ordered bottom location to top location
        tree_ids.reverse()
        return self.browse(tree_ids)
