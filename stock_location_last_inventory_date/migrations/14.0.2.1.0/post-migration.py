# Copyright 2026 Raumschmiede GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock_location_last_inventory_date.hooks import (
    set_inventory_date_on_child_location,
)


def migrate(cr, version):
    set_inventory_date_on_child_location(cr)
