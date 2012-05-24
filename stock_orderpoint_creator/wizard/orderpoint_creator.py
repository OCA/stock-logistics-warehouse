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

from osv import osv, fields

_template_register = ['orderpoint_template_id']

class OrderpointCreator(osv.osv_memory):
    _name = 'stock.warehouse.orderpoint.creator'
    _description = 'Orderpoint Creator'

    _columns = {
            'orderpoint_template_id': fields.many2one(
                'stock.warehouse.orderpoint.template',
                "Stock rule template")
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
            template_br = current[template_field]
            if template_br:
                template_model = template_br._model._name
                template_obj = self.pool.get(template_model)
                template_obj.create_instances(cursor, uid, template_br,
                                              product_ids, context=context)

        return {}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
