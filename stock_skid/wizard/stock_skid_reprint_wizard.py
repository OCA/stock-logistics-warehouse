# -*- encoding: utf-8 -*-

############################################################################
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

from openerp.osv import orm, fields


class SkidReprintWizard(orm.TransientModel):
    _name = "stock.skid.reprint.wizard"
    _description = "Skid Reprint Wizard"
    _columns = {
        "prodlot_id": fields.many2one("stock.production.lot", "Production Lot"),
        "location_id": fields.many2one("stock.location", "Location"),
    }

    def do_print(self, cr, uid, ids, context=None):
        print cr, uid, ids, context
