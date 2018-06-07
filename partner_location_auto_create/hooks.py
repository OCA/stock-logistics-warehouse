# © 2018 brain-tec AG (Kumar Aberer <kumar.aberer@braintec-group.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, SUPERUSER_ID
import logging
logger = logging.getLogger(__name__)


def post_init_hook(cr, _):
    """Create custom location for existing partners"""
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        logger.info('Create custom locations for partners')

        locations = env['stock.location'].search([])
        partners = env['res.partner'].search([('is_company', '=', True)])
        counter = 0
        for partner in partners:
            if not locations.filtered(lambda l: l.partner_id == partner):
                logger.info('Create custom location for partner id=%s (%s/%s)'
                            % (partner.id, counter, len(partners)))
                partner._create_main_partner_location()
                counter += 1
