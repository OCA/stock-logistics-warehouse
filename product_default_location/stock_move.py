# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm


class stock_move(orm.Model):
    _inherit = 'stock.move'

    def _get_product_default_loc_for_type(self, cr, uid,
                                          prod_id=False, type=False,
                                          context=None):
        # helper function to change the source and destination
        #  location to product default location depending on the shipment type
        update_dict = {}
        if prod_id:
            product = self.pool.get('product.product').browse(cr, uid, prod_id)
            if product.default_location_id:
                if type == "in":
                    update_dict['location_dest_id'] = \
                        product.default_location_id.id

                elif type == "out":
                    update_dict['location_id'] = product.default_location_id.id

                else:
                    update_dict['location_id'] = product.default_location_id.id
                    update_dict['location_dest_id'] = \
                        product.default_location_id.id
            return update_dict

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
                            loc_dest_id=False, partner_id=False, type=False):

        result = super(stock_move, self).\
            onchange_product_id(cr, uid, ids, prod_id=prod_id, loc_id=loc_id,
                                loc_dest_id=loc_dest_id, partner_id=partner_id)
        update_dict = self.\
            _get_product_default_loc_for_type(cr, uid, prod_id, type)
        result['value'].update(update_dict)
        return result

    def onchange_move_type(self, cr, uid, ids, type, prod_id, context=None):
        res = super(stock_move, self).\
            onchange_move_type(cr, uid, ids, type, context=None)
        update_dict = self.\
            _get_product_default_loc_for_type(cr, uid, prod_id, type, context)
        if update_dict is not None:
            res['value'].update(update_dict)
        return res
