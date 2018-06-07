# © 2015 Savoir-faire Linux
# © 2018 brain-tec AG (Kumar Aberer <kumar.aberer@braintec-group.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import UserError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    main_partner_location = fields.Boolean(
        'Main Partner Location',
        help="The root location for a partner's location for a specific "
        "type.")

    @api.multi
    @api.constrains('partner_id', 'main_partner_location', 'usage')
    def _check_main_location(self):
        for location in self:
            partner = location.partner_id

            if partner and len(partner.get_main_location(location.usage)) > 1:
                raise UserError(
                    _('The partner %s already has a main location '
                        'of type %s.') % (partner.name, location.usage))

    @api.onchange('partner_id', 'usage')
    def _onchange_parent_location(self):
        if self.partner_id:
            self.location_id = self.partner_id.get_main_location(self.usage).id
