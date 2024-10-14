# Copyright 2017 Sylvain Van Hoof <svh@sylvainvh.be>
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    is_zone = fields.Boolean(
        string="Is a Zone Location?", help="Mark to define this location as a zone"
    )

    zone_location_id = fields.Many2one(
        "stock.location",
        string="Location Zone",
        compute="_compute_zone_location_id",
        store=True,
        index=True,
        recursive=True,
    )
    area_location_id = fields.Many2one(
        "stock.location",
        string="Location Area",
        compute="_compute_zone_location_id",
        store=True,
        recursive=True,
    )

    location_kind = fields.Selection(
        [
            ("zone", "Zone"),
            ("area", "Area"),
            ("bin", "Bin"),
            ("stock", "Main Stock"),
            ("other", "Other"),
        ],
        compute="_compute_location_kind",
        store=True,
        help="Group location according to their kinds: "
        "* Zone: locations that are flagged as being zones "
        "* Area: locations with children that are part of a zone "
        "* Bin: locations without children that are part of a zone "
        "* Stock: internal locations whose parent is a view "
        "* Other: any other location",
    )

    @api.depends(
        "is_zone", "location_id.zone_location_id", "location_id.area_location_id"
    )
    def _compute_zone_location_id(self):
        self_browse = self.browse()
        self.update({"zone_location_id": self_browse, "area_location_id": self_browse})
        for location in self:
            if location.is_zone:
                location.zone_location_id = location
                continue
            parent = location.location_id
            if parent.zone_location_id:
                # If we have more than one level of area in a zone,
                # the grouping is done by the first level
                if parent.area_location_id:
                    area_location_id = parent.area_location_id
                else:
                    area_location_id = location
                location.update(
                    {
                        "zone_location_id": parent.zone_location_id,
                        "area_location_id": area_location_id,
                    }
                )

    @api.depends(
        "usage",
        "location_id.usage",
        "child_ids",
        "area_location_id",
        "zone_location_id",
    )
    def _compute_location_kind(self):
        for location in self:
            if location == location.zone_location_id:
                location.location_kind = "zone"
                continue

            parent = location.location_id
            if (
                # Internal locations whose parent is view are main stocks
                location.usage in ("internal", "view")
                and not location.zone_location_id
                and parent.usage == "view"
            ):
                location.location_kind = "stock"
            elif (
                # Internal locations having a zone and no children are bins
                location.usage == "internal"
                and location.zone_location_id
                and location.area_location_id
                and not location.child_ids
            ):
                location.location_kind = "bin"
            elif (
                # Internal locations having a zone and children are areas
                location.usage in ("internal", "view")
                and location.zone_location_id
                and location.area_location_id
                and location.child_ids
            ):
                location.location_kind = "area"
            else:
                # All the rest are other locations
                location.location_kind = "other"
