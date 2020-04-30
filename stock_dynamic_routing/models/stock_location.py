# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models, tools


class StockLocation(models.Model):
    _inherit = "stock.location"

    @tools.ormcache("self.id")
    def _location_parent_tree(self):
        self.ensure_one()
        tree = self.search(
            [("id", "parent_of", self.id)],
            # the recordset will be ordered bottom location to top location
            order="parent_path desc",
        )
        return tree

    @api.model_create_multi
    def create(self, vals_list):
        locations = super().create(vals_list)
        self._location_parent_tree.clear_cache(self)
        return locations

    def write(self, values):
        res = super().write(values)
        self._location_parent_tree.clear_cache(self)
        return res

    def unlink(self):
        res = super().unlink()
        self._location_parent_tree.clear_cache(self)
        return res
