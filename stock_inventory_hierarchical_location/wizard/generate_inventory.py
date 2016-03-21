# -*- coding: utf-8 -*-
#
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
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
#

from openerp.osv import fields, orm
from openerp.tools.translate import _


class GenerateInventoryWizard(orm.TransientModel):

    """ This wizard generate an inventory and all related sub-inventories
    for the specified location and level
    Example: location = Stock / level = 1 => 1 inventory on Stock
                                                            (similar to create)
             location = Stock / level = 2 => 1 inventory on Stock,
                                             1 sub-inventory on Shelf1,
                                             1 sub-inventory on Shelf2
    """

    _name = "stock.generate.inventory"
    _description = "Generate Inventory"

    _columns = {
        'prefix_inv_name': fields.char('Inventory prefix',
                                       help="Optional prefix for all "
                                       "created inventory"),
        'location_id': fields.many2one('stock.location', 'Location',
                                       required=True),
        'level': fields.integer("Level",
                                help="Maximum number of intermediate "
                                "sub-inventories between the main inventory "
                                "and the smallest sub-inventory."),
        'only_view': fields.boolean('Only view',
                                    help="If set, only inventory "
                                    "on view location can be created"),
    }

    def _default_location(self, cr, uid, ids, context=None):
        """Default stock location

        @return: id of the stock location of the first warehouse of the
        default company"""
        location_id = False
        company_id = self.pool['res.company']._company_default_get(
            cr, uid, 'stock.warehouse', context=context)
        warehouse_id = self.pool['stock.warehouse'].search(
            cr, uid, [('company_id', '=', company_id)], limit=1)
        if warehouse_id:
            location_id = self.pool['stock.warehouse'].read(
                cr, uid, warehouse_id[0], ['lot_stock_id'])['lot_stock_id'][0]
        return location_id

    _defaults = {
        'location_id': _default_location,
        'level': 1,
        'only_view': True,
    }

    _sql_constraints = [
        ('level', 'CHECK (level>0)', 'Level must be positive!'),
    ]

    def _create_subinventory(self, cr, uid, inventory_ids, prefix_inv_name,
                             only_view, context):
        new_inventory_ids = []
        for inventory_id in inventory_ids:
            location_id = self.pool['stock.inventory'].read(
                cr, uid, inventory_id, ['location_id'],
                context=context)['location_id'][0]
            domain = [('location_id', '=', location_id)]
            if only_view:
                domain.append(('usage', '=', 'view'))
            location_ids = self.pool['stock.location'].search(
                cr, uid, domain, context=context)
            for location_id in location_ids:
                location_name = self.pool['stock.location'].read(
                    cr, uid, location_id, ['name'], context=context)['name']
                new_inventory_ids.append(
                    self.pool['stock.inventory'].
                    create(cr, uid, {'name': prefix_inv_name + location_name,
                                     'exhaustive': True,
                                     'location_id': location_id,
                                     'parent_id': inventory_id},
                           context=context))
        return new_inventory_ids

    def generate_inventory(self, cr, uid, ids, context=None):
        """ Generate inventory and sub-inventories for specified location
        and level

        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        if ids and len(ids):
            ids = ids[0]
        else:
            return {'type': 'ir.actions.act_window_close'}
        generate_inventory = self.browse(cr, uid, ids, context=context)
        # create first level inventory
        prefix_inv_name = generate_inventory.prefix_inv_name or ''
        location_id = generate_inventory.location_id.id
        only_view = generate_inventory.only_view
        parent_inventory_id = self.pool['stock.inventory'].\
            create(cr, uid, {'name': prefix_inv_name +
                             generate_inventory.location_id.name,
                             'exhaustive': True,
                             'location_id': location_id}, context=context)

        inventory_ids = [parent_inventory_id]
        for i in range(1, generate_inventory.level):
            inventory_ids = self._create_subinventory(
                cr, uid, inventory_ids, prefix_inv_name, only_view, context)

        mod_obj = self.pool['ir.model.data']
        result = mod_obj.get_object_reference(
            cr, uid, 'stock', 'view_inventory_form')
        view_id = result and result[1] or False
        return {'name': _('Inventory generated'),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'stock.inventory',
                'type': 'ir.actions.act_window',
                'view_id': view_id,
                'res_id': int(parent_inventory_id),
                }
