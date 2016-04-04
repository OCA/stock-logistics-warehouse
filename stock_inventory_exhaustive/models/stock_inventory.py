# -*- coding: utf-8 -*-
# © 2013-2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api


class StockInventory(models.Model):
    """Add locations to the inventories"""
    _inherit = 'stock.inventory'

    exhaustive = fields.Boolean(
        string='Exhaustive', readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda x: x._get_default_exhaustive(),
        help="Check the box if you are conducting an exhaustive "
             "Inventory.\n"
             "Leave the box unchecked if you are conducting a standard "
             "Inventory (partial inventory for example).\n"
             "For an exhaustive Inventory:\n"
             " - if some of the Inventory's Locations have not been "
             "entered in the Inventory Lines, Odoo warns you "
             "when you confirm the Inventory\n"
             " - every good that is not in the Inventory Lines is "
             "considered lost, and gets moved out of the stock when you "
             "confirm the Inventory")

    def _get_default_exhaustive(self):
        """Override this method in a sub-module if it changes the default"""
        return False

    @api.multi
    def get_missing_locations(self):
        """Compute the list of location_ids which are missing from the lines

        Here, "missing" means the location is the inventory's location or one
        of it's children, and the inventory does not contain any line with
        this location."""
        # Find the locations of the inventories (including sub-locations)
        inv_locations = self.env['stock.location'].search(
            [('location_id', 'child_of', self.mapped('location_id').ids),
             ('usage', 'in', ['internal', 'transit'])])
        # Find the locations already recorded in inventory lines
        line_locations = self.mapped('line_ids.location_id')
        return inv_locations - line_locations

    @api.multi
    def confirm_missing_locations(self):
        """Open wizard to confirm empty locations on exhaustive inventories"""
        exh_inventories = self.filtered('exhaustive')
        if exh_inventories.get_missing_locations():
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.inventory.uninventoried.locations',
                'target': 'new',
                'context': dict(self._context,
                                active_ids=exh_inventories.ids,
                                active_id=exh_inventories[0].id),
                'nodestroy': True,
            }
        return self.action_done()

    @api.onchange('exhaustive')
    def _onchange_exhaustive(self):
        """A exhaustive inventory is for all products only."""
        if self.exhaustive:
            self.filter = 'none'

    @api.multi
    def _inventory_locations_to_purge(self):
        """Find all the locations inventoried

        Override this method in submodules if you need to make the inventory
        exhaustive on only some of the locations"""
        self.ensure_one()
        return self.env['stock.location'].search(
            [('id', 'child_of', [self.location_id.id])])

    @api.multi
    def action_done(self):
        """Add missing lines with qty=0 for exhaustive inventories"""
        for inventory in self.filtered('exhaustive'):
            sql = '''
                SELECT
                    sq.product_id,
                    SUM(sq.qty) AS product_qty,
                    sq.location_id,
                    sq.lot_id AS prod_lot_id,
                    sq.package_id,
                    sq.owner_id AS partner_id
                FROM stock_quant AS sq
                    LEFT JOIN stock_inventory_line as sil
                        ON sq.location_id = sil.location_id
                        -- not '=' because they can be NULL
                        AND sq.product_id IS NOT DISTINCT FROM  sil.product_id
                        AND sq.lot_id IS NOT DISTINCT FROM sil.prod_lot_id
                        AND sq.owner_id IS NOT DISTINCT FROM sil.partner_id
                        AND sq.package_id IS NOT DISTINCT FROM sil.package_id
                        -- not 'IN' because the list can be empty
                        AND sil.id = ANY (%s)
                WHERE sq.location_id = ANY (%s)
                    AND sil.id IS NULL
                GROUP BY
                    sq.product_id,
                    sq.location_id,
                    sq.lot_id,
                    sq.package_id,
                    sq.owner_id
            '''
            params = (inventory.line_ids.ids,
                      inventory._inventory_locations_to_purge().ids)
            self.env.cr.execute(sql, params)
            for product_line in self.env.cr.dictfetchall():
                # replace the None the dictionary by False,
                # because false values are tested later on
                for key, value in product_line.items():
                    if not value:
                        product_line[key] = False
                product_line.update(
                    {'inventory_id': inventory.id,
                     'product_qty': 0.0,
                     'theoretical_qty': product_line['product_qty']})
                if product_line['product_id']:
                    product = self.env['product.product'].browse(
                        product_line['product_id'])
                    product_line['product_uom_id'] = product.uom_id.id
                self.env['stock.inventory.line'].create(product_line)
        super(StockInventory, self).action_done()
