# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher (Camptocamp)
#    Copyright 2012 Camptocamp SA
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

""" Wizard defining stock.warehouse.orderpoint configurations for selected
products. Those configs are generated using templates """

from openerp.osv.orm import browse_record, TransientModel, fields

_template_register = ['orderpoint_template_id']

class OrderpointCreator(TransientModel):
    _name = 'stock.warehouse.orderpoint.creator'
    _description = 'Orderpoint Creator'

    _columns = {'orderpoint_template_id': fields.many2many(
                        'stock.warehouse.orderpoint.template',
                        rel='order_point_creator_rel',
                        string='Stock rule template')
    }


    def _get_template_register(self):
        """return a list of the field names which defines a template
        This is a hook to allow expending the list of template"""
        return _template_register


    def action_configure(self, cursor, uid, wiz_id, context=None):
        """ action to retrieve wizard data and launch creation of items """

        product_ids = context['active_ids']
        if isinstance(wiz_id, list):
            wiz_id = wiz_id[0]
        current = self.browse(cursor, uid, wiz_id, context=context)
        for template_field in  self._get_template_register():
            template_br_list = current[template_field]
            if template_br_list:
                if isinstance(template_br_list, browse_record):
                    template_br_list = [template_br_list]
                template_model = template_br_list[0]._model._name
                template_obj = self.pool.get(template_model)
                template_obj._disable_old_instances(cursor, uid, template_br_list,
                                                    product_ids, context=context)
                for template_br in template_br_list:
                    template_obj.create_instances(cursor, uid, template_br,
                                              product_ids, context=context)

        return {}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
