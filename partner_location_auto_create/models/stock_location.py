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
from odoo.exceptions import Warning


class StockLocation(models.Model):
    _inherit = "stock.location"

    main_partner_location = fields.Boolean(
        "Main Partner Location",
        help="The root location for a partner's location for a specific " "type.",
    )
    partner_id = fields.Many2one(
        "res.partner", "Owner", help="Owner of the location if not internal"
    )

    # @api.constrains('main_partner_location', 'usage')
    @api.constrains("partner_id", "main_partner_location", "usage")
    def _check_main_location(self):
        """Raise warning if partner already has a main location linked to it."""
        partner = self.partner_id

        if partner and len(partner.get_main_location(self.usage)) > 1:
            raise Warning(
                _("The partner %s already has a main location " "of type %s.")
                % (partner.name, self.usage)
            )

    # @api.onchange('usage')
    @api.onchange("partner_id", "usage")
    def _onchange_parent_location(self):
        if self.partner_id:
            self.location_id = self.partner_id.get_main_location(self.usage).id
