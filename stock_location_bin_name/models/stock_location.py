# Copyright 2017 Syvain Van Hoof (Okia sprl) <sylvainvh@okia.be>
# Copyright 2016-2019 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import string

from odoo import api, fields, models


class PartialFormatter(string.Formatter):
    def __init__(self, missing="~", bad_fmt="!"):
        self.missing = missing
        self.bad_fmt = bad_fmt

    def get_field(self, field_name, args, kwargs):
        # Handle a key not found
        try:
            val = super().get_field(field_name, args, kwargs)
        except (KeyError, AttributeError):
            val = None, field_name
        return val

    def format_field(self, value, spec):
        # handle an invalid format
        if value is None:
            return self.missing
        try:
            return super().format_field(value, spec)
        except ValueError:
            if self.bad_fmt is not None:
                return self.bad_fmt
            else:
                raise


class StockLocation(models.Model):
    _inherit = "stock.location"

    location_name_format = fields.Char(
        "Location Name Format",
        help="Format string that will compute the name of the location. "
        "Use location fields. Example: "
        "'{area}-{corridor:0>2}.{rack:0>3}"
        ".{level:0>2}'\n"
        "Missing fields are replaced by '~' and formatting errors by '!'.",
    )

    @api.onchange("corridor", "row", "rack", "level", "posx", "posy", "posz")
    def _onchange_attribute_compute_name(self):
        for location in self:
            if not location.location_kind == "bin":
                continue
            area = location
            while area and not area.location_name_format:
                area = area.location_id
            if not area:
                continue
            template = area.location_name_format
            # We don't want to use the full browse record as it would
            # give too much access to internals for the users.
            # We cannot use location.read() as we may have a NewId.
            # We should have the record's values in the cache at this
            # point. We must be cautious not to leak an environment through
            # relational fields.
            values = dict(location._cache)
            values["area"] = area.name
            location.name = PartialFormatter().format(template, **values)
