# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = "stock.location"

    @api.constrains("location_id")
    def _check_inventory_location_id(self):
        vals = set(self.ids) | set(self.mapped("location_id").ids)
        location_inventory_open_ids = self.env[
            "stock.inventory"
        ]._get_locations_open_inventories(vals)
        if location_inventory_open_ids:
            raise ValidationError(_("An inventory is being conducted at this location"))

    def unlink(self):
        location_inventory_open_ids = (
            self.env["stock.inventory"].sudo()._get_locations_open_inventories(self.ids)
        )
        if location_inventory_open_ids:
            raise ValidationError(_("An inventory is being conducted at this location"))
        return super(StockLocation, self).unlink()
