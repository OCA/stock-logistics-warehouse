##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    locations_count = fields.Integer(
        compute="_compute_locations_count", store=False, default=0
    )

    location_ids = fields.One2many("stock.location", "partner_id", string="Locations")

    @api.depends("location_ids")
    def _compute_locations_count(self):
        self.locations_count = len(self.location_ids)

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        if "company_id" in fields:
            res["company_id"] = self.env.user.company_id.id

        res["customer_rank"] = 1
        # Update: not all partners must be suppliers by default
        # (only partners created from vendors list view,
        # rfq form views ...)

        return res

    def button_locations(self):
        """Return ir.actions.act_window to show related locations of the customer"""
        self.ensure_one()

        res = {
            "name": _("Locations"),
            "type": "ir.actions.act_window",
            "res_model": "stock.location",
            "view_type": "form",
        }

        if len(self.location_ids) == 1:
            res["res_id"] = self.location_ids.id
            res["view_mode"] = "form"
        else:
            res["domain"] = [("partner_id", "=", self.id)]
            res["view_mode"] = "tree,form"

        return res

    # Returns location which matches usage and has main_partner_location == True
    def get_main_location(self, usage):
        """Return main location of the partner"""
        self.ensure_one()
        return self.location_ids.filtered(
            lambda l: l.usage == usage and l.main_partner_location
        )

    def get_parent_location(self, usage):
        return self.env.ref(f"stock.stock_location_{usage}s")

    def _create_main_partner_location(self):
        """Create the main partner location.

        Create a location for customers with the parent "Partner Location/Customers".
        Create a location for vendors with the parent "Partner Location/Vendors"."""
        # Create location for customers
        if self.customer_rank > 0 and self.property_stock_customer.partner_id != self:
            location_customer = self.get_main_location(
                "customer"
            ) or self._create_main_location("customer")

            self.write({"property_stock_customer": location_customer})

        # Create location for vendors
        if self.supplier_rank > 0 and self.property_stock_supplier.partner_id != self:
            location_supplier = self.get_main_location(
                "supplier"
            ) or self._create_main_location("supplier")

            self.write({"property_stock_supplier": location_supplier})

    def _create_main_location(self, usage):
        """Create stock.location for the partner"""
        self.ensure_one()

        parent = (
            self.get_main_location(usage)
            or self.company_id.get_default_location(usage)
            or self.get_parent_location(usage)
        )

        return (
            self.env["stock.location"]
            .sudo()
            .create(
                {
                    "name": self.name,
                    "usage": usage,
                    "partner_id": self.id,
                    "company_id": self.company_id.id,
                    "location_id": parent.id if parent is not None else None,
                    "main_partner_location": True,
                }
            )
        )

    def _remove_locations(self):
        """
        Unlink all locations related to the partner
        where no stock have been moved.

        This is required to prevent unrequired locations to
        be created when a new partner is tagged as a company
        by mistake.
        """
        move_obj = self.env["stock.move"]
        for location in self.location_ids:
            moves = move_obj.search(
                [
                    "|",
                    ("location_id", "child_of", location.id),
                    ("location_dest_id", "child_of", location.id),
                ]
            )
            if not moves:
                location.unlink()

    @api.model
    def create(self, vals):
        """ The first time a partner is created, a main customer
        and / or supplier location is created for this partner """
        partner = super(ResPartner, self).create(vals)
        if partner.is_company:
            partner._create_main_partner_location()
        return partner

    def write(self, vals):
        if vals.get("name"):
            for partner in self:
                locations = partner.location_ids.filtered(
                    lambda l: l.name == partner.name
                )
                locations.sudo().write({"name": vals.get("name")})

        res = super(ResPartner, self).write(vals)

        # Update: If the partner is changed to be a supplier
        # (adding tag 'Lieferant') then a supplier stock location
        # should be generated (if needed)
        if (
            vals.get("is_company")
            or vals.get("customer")
            or vals.get("supplier")
            or vals.get("category_id")
        ):
            for partner in self.filtered("is_company"):
                partner._create_main_partner_location()

        if "is_company" in vals and not vals["is_company"]:
            # When False is written to field 'is_company'
            self._remove_locations()

        if "active" in vals:
            self.location_ids.write({"active": vals["active"]})

        return res
