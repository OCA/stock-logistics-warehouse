# -*- coding: utf-8 -*-
###############################################################################
#
#    Module for OpenERP
#    Copyright (C) 2015 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Florian DA COSTA <florian.dacosta@akretion.com>
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
###############################################################################
from openerp import models, api, fields
from openerp.tools.translate import _


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    mts_rule_id = fields.Many2one('procurement.rule',
                                  string="MTS Rule")
    mto_rule_id = fields.Many2one('procurement.rule',
                                  string="MTO Rule")

    @api.model
    def _get_action(self):
        return [('split_procurement', _('Choose between MTS and MTO'))] + \
            super(ProcurementRule, self)._get_action()
