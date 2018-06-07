# © 2015 Savoir-faire Linux
# © 2018 brain-tec AG (Kumar Aberer <kumar.aberer@braintec-group.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    locations_count = fields.Integer(
        compute='_compute_locations_count', store=False)

    location_ids = fields.One2many(
        'stock.location', 'partner_id', string='Locations')

    @api.multi
    @api.depends('location_ids')
    def _compute_locations_count(self):
        for partner in self:
            partner.locations_count = len(partner.location_ids)

    @api.multi
    def button_locations(self):
        self.ensure_one()

        res = {
            'name': _('Locations'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.location',
            'view_type': 'form',
        }

        if len(self.location_ids) == 1:
            res['res_id'] = self.location_ids.id
            res['view_mode'] = 'form'
        else:
            res['domain'] = [('partner_id', '=', self.id)]
            res['view_mode'] = 'tree,form'

        return res

    @api.multi
    def get_main_location(self, usage):
        self.ensure_one()
        return self.location_ids.filtered(
            lambda l: l.usage == usage and l.main_partner_location)

    @api.multi
    def _create_main_partner_location(self):
        for partner in self:
            if partner.customer and partner.property_stock_customer.\
                    partner_id != partner:
                location_customer = (
                    partner.get_main_location('customer') or
                    partner._create_main_location('customer'))

                partner.property_stock_customer = location_customer

            if partner.supplier and partner.property_stock_supplier.\
                    partner_id != partner:
                location_supplier = (
                    partner.get_main_location('supplier') or
                    partner._create_main_location('supplier'))

                partner.property_stock_supplier = location_supplier

    @api.multi
    def _create_main_location(self, usage):
        self.ensure_one()

        parent = (
            self.get_main_location(usage) or
            self.company_id.get_default_location(usage)
        )

        return self.env['stock.location'].create({
            'name': self.name,
            'usage': usage,
            'partner_id': self.id,
            'company_id': self.company_id.id,
            'location_id': parent.id,
            'main_partner_location': True,
        })

    @api.multi
    def _remove_locations(self):
        """
        Unlink all locations related to the partner
        where no stock have been moved.

        This is required to prevent unrequired locations to
        be created when a new partner is tagged as a company
        by mistake.
        """
        move_obj = self.env['stock.move']
        for partner in self:
            for location in partner.location_ids:
                moves = move_obj.search([
                    '|',
                    ('location_id', 'child_of', location.id),
                    ('location_dest_id', 'child_of', location.id),
                ])
                if not moves:
                    location.unlink()

    @api.model
    def create(self, vals):
        """ The first time a partner is created, a main customer
        and / or supplier location is created for this partner """
        partner = super(ResPartner, self).create(vals)

        if vals.get('is_company', False):
            partner._create_main_partner_location()

        return partner

    @api.multi
    def write(self, vals):
        if vals.get('name'):
            for partner in self:
                locations = partner.location_ids.filtered(
                    lambda l: l.name == partner.name)
                locations.write({'name': vals.get('name')})

        res = super(ResPartner, self).write(vals)

        if (
                vals.get('is_company') or
                vals.get('customer') or
                vals.get('supplier')
        ):
            for partner in self.filtered('is_company'):
                partner._create_main_partner_location()

        if 'is_company' in vals and not vals['is_company']:
            # When False is written to field 'is_company'
            self._remove_locations()

        if 'active' in vals:
            self.location_ids.write({'active': vals['active']})

        return res
