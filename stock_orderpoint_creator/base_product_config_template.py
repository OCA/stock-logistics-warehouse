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

""" Base template for product config """
from openerp.osv.orm import browse_record, browse_record_list

class BaseProductConfigTemplate():
    """ Abstract class for product config """


    def _get_model(self):
        """ Get the model for which this template is defined

        return a browse record of the model for which
               is represented by this template
        """
        model = self._inherit
        model_obj = self.pool.get(model)
        return model_obj

    def _get_ids_2_clean(self, cursor, uid, template_br,
                         product_ids, context=None):
        """ hook to select model specific objects to clean
        return must return a list of id"""
        return []

    def _disable_old_instances(self, cursor, uid, template_br_list,
                               product_ids, context=None):
        """ Clean old instance by setting those inactives """
        model_obj = self._get_model()
        for template in template_br_list:
            ids2clean = self._get_ids_2_clean(cursor, uid, template,
                                              product_ids, context=context)
            if self._clean_mode == 'deactivate':
                model_obj.write(cursor, uid, ids2clean,
                                {'active': False}, context=context)
            elif self._clean_mode == 'unlink':
                model_obj.unlink(cursor, uid, ids2clean, context=context)


    def create_instances(self, cursor, uid, template_br,
                         product_ids, context=None):
        """ Create instances of model using template inherited model """
        if not isinstance(product_ids, list):
            product_ids = [product_ids]

        # data = self.copy_data(cursor, uid, template_br.id, context=context)
        # copy data will not work in all case and may retrieve erronus value

        model_obj = self._get_model()

        data = {}
        #May rais error on function fields in future
        for key in model_obj._columns.keys():
            tmp = template_br[key]
            if isinstance(tmp, browse_record):
                tmp = tmp.id
            if isinstance(tmp, browse_record_list):
                tmp = [(6, 0, tmp)]
            data[key] = tmp

        for product_id in product_ids:
            data['product_id'] = product_id
            model_obj.create(cursor, uid, data, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
