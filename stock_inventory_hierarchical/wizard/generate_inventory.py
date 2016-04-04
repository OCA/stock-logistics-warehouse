# -*- coding: utf-8 -*-
# © 2014 Acsone SA/NV (http://www.acsone.eu)
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, api, models
from openerp.tools.translate import _


class GenerateInventoryWizard(models.TransientModel):
    """Generate an inventory and all related sub-inventories

    Example: location = Stock / level = 1 => 1 inventory on Stock
                                             (similar to create)
             location = Stock / level = 2 => 1 inventory on Stock,
                                             1 sub-inventory on Shelf1,
                                             1 sub-inventory on Shelf2
    """

    _name = "stock.generate.inventory"
    _description = "Generate Inventory"

    prefix_inv_name = fields.Char(string='Inventory prefix',
                                  help="Optional prefix for all created "
                                       "inventory")
    location_id = fields.Many2one(comodel_name='stock.location',
                                  default=lambda x: x._default_location(),
                                  string='Location', required=True)
    level = fields.Integer(string="Level", default=3,
                           help="Maximum number of intermediate "
                                "sub-inventories between the main inventory "
                                "and the smallest sub-inventory.")
    only_view = fields.Boolean(string='Only view', default=True,
                               help="If set, only inventory "
                                    "on view location can be created")

    @api.model
    def _default_location(self):
        """Default stock location

        @return: id of the stock location of the first warehouse of the
        default company"""
        company_id = self.env['res.company']._company_default_get(
            'stock.warehouse')
        warehouse_ids = self.env['stock.warehouse'].search(
            [('company_id', '=', company_id)], limit=1)
        return warehouse_ids.lot_stock_id.id

    _sql_constraints = [
        ('level', 'check (level>0)', 'Level must be positive!'),
    ]

    @api.model
    def _create_subinventory(self, inventories, prefix_inv_name, only_view):
        new_inventories = []
        for inventory in inventories:
            if only_view:
                usage = ('view',)
            else:
                usage = ('internal', 'transit', 'view')
            # We search for the children corresponding to our criteria, but we
            # can't search with "child_of" because we'd not know the depth; and
            # we can't neither search for immediate children, because we want
            # to bypass the locations which don't meet our criteria. In other
            # words, if we want a view and the 1st one is under an internal
            # location, we still want to find it.
            self.env.cr.execute("""
            SELECT
                child.id
            FROM
                stock_location AS inventory_loc
                -- find all the view children
                INNER JOIN stock_location AS child ON
                    child.usage IN %s AND
                    child.active AND
                    child.parent_left >= inventory_loc.parent_left AND
                    child.parent_right <= inventory_loc.parent_right
                -- find all the ancestors to count the levels
                INNER JOIN stock_location AS ancestor ON
                    ancestor.active AND
                    ancestor.usage IN %s AND
                    ancestor.parent_left <= child.parent_left AND
                    ancestor.parent_right >= child.parent_right AND
                    -- we only want the locations under the main location
                    ancestor.parent_left > inventory_loc.parent_left AND
                    ancestor.parent_right < inventory_loc.parent_right
            WHERE
                inventory_loc.id=%s
            GROUP BY child.id , child.complete_name
            -- we only want the first level of depth
            HAVING COUNT(*)=1""", (usage, usage, inventory.location_id.id))
            sublocation_ids = [i[0] for i in self.env.cr.fetchall()]
            for location in self.env['stock.location'].browse(sublocation_ids):
                new_inventories.append(
                    self.env['stock.inventory'].create(
                        {'name': prefix_inv_name + location.name,
                         'location_id': location.id,
                         'parent_id': inventory.id}))
        return new_inventories

    @api.multi
    def generate_inventory(self):
        """Generate inventory and sub-inventories for specified location/level
        """
        self.ensure_one()
        # We're going to compute all the parent_left/right at the end
        fast_self = self.with_context(
            defer_parent_store_computation=True)
        # create first level inventory
        prefix_inv_name = self.prefix_inv_name or ''
        parent_inventory = fast_self.env['stock.inventory'].create(
            {'name': prefix_inv_name + self.location_id.name,
             'location_id': self.location_id.id})
        inventories = [parent_inventory]
        # Create the sub-inventories
        for _dummy in range(1, self.level):
            inventories = fast_self._create_subinventory(
                inventories, prefix_inv_name, self.only_view)
        # Compute the parent_left/right
        fast_self.env['stock.inventory']._parent_store_compute()

        result = self.env['ir.model.data'].get_object_reference(
            'stock', 'view_inventory_form')
        view_id = result[1] if result else False
        return {'name': _('Inventory generated'),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'stock.inventory',
                'type': 'ir.actions.act_window',
                'view_id': view_id,
                'res_id': int(parent_inventory.id)}
