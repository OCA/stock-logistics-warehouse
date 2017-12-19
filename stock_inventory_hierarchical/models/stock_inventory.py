# -*- coding: utf-8 -*-
# © 2013-2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import models, api, fields
from openerp.tools.translate import _

from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# What states are allowed for children depending on the parent's state
CONSISTANT_STATES = {
    'draft': ['draft'],
    # When confirming inventories, may contain draft children for a short time
    'confirm': ['draft', 'confirm', 'done'],
    'done': ['done'],
    # The state "cancel" is not reachable in the standard anymore
    'cancel': ['cancel']}


class HierarchicalInventory(models.Model):
    _inherit = 'stock.inventory'

    _parent_store = True
    _parent_order = 'date, name'
    _order = 'parent_left'

    # name_get() only changes the default name of the record, not the
    # content of the field "name" so we add another field for that
    complete_name = fields.Char(
        compute='_complete_name',
        string='Complete reference')
    parent_id = fields.Many2one(
        comodel_name='stock.inventory', string='Parent Inventory',
        ondelete='cascade', readonly=True,
        states={'draft': [('readonly', False)]})
    inventory_ids = fields.One2many(
        comodel_name='stock.inventory', inverse_name='parent_id',
        string='List of Sub-inventories', readonly=True,
        states={'draft': [('readonly', False)]})
    parent_left = fields.Integer('Parent Left', index=True)
    parent_right = fields.Integer('Parent Right', index=True)
    progress_rate = fields.Float(
        compute='_progress_rate', string='Progress')

    @api.multi
    def name_get(self):
        """Show the parent inventory's name in the name of the children

        :param dict context: the ``inventory_display`` key can be
                             used to select the short version of the
                             inventory name (without the direct parent),
                             when set to ``'short'``. The default is
                             the long version."""
        if (self._context is None or
                self._context.get('inventory_display') == 'short'):
            # Short name context: just do the usual stuff
            return super(HierarchicalInventory, self).name_get()
        return [(i.id, i.complete_name) for i in self]

    @api.multi
    def _complete_name(self):
        """Function-field wrapper to get the complete name from name_get"""
        for inventory in self:
            inventory.complete_name = (inventory.parent_id and
                                       inventory.parent_id.name + ' / ' or
                                       '') + inventory.name

    @api.multi
    def _progress_rate(self):
        """Rate of (sub)inventories done/total"""
        for inventory in self:
            nb = self.search([('parent_id', 'child_of', inventory.id)],
                             count=True)
            if not nb:
                # the record is not in the database yet: consider it's 0% done
                inventory.progress_rate = 0
                continue
            nb_done = self.search([('parent_id', 'child_of', inventory.id),
                                   ('state', '=', 'done')], count=True)
            inventory.progress_rate = 100 * nb_done / nb

    @api.one
    @api.constrains('inventory_ids', 'parent_id')
    def _check_inventory_recursion(self):
        if not self._check_recursion():
            raise ValidationError(
                _('Error: You can not create recursive inventories.'))

    @api.one
    @api.constrains('state', 'inventory_ids', 'parent_id')
    def _check_state_consitency(self):
        # Check we're consistent with our children
        if self.inventory_ids:
            inconsistent_children = self.search(
                [('parent_left', '>=', self.parent_left),
                 ('parent_right', '<=', self.parent_right),
                 ('state', 'not in', CONSISTANT_STATES[self.state])])
            if inconsistent_children:
                raise ValidationError(
                    (_("The state of the inventory %s (%s) is not consistent "
                       "with the state of the following sub-inventories:\n"
                       ) % ((self.name, self.state)) +
                     "\n".join(['- %s (%s)' % (i.name, i.state)
                                for i in inconsistent_children])))
        # Check we're consistent with our parents
        if self.parent_id:
            parents = self.search(
                [('parent_left', '<', self.parent_left),
                 ('parent_right', '>', self.parent_right)])
            inconsistent_parents = []
            for parent in parents:
                if self.state not in CONSISTANT_STATES[parent.state]:
                    inconsistent_parents.append(parent)
            if inconsistent_parents:
                raise ValidationError(
                    (_("The state of the inventory %s (%s) is not consistent "
                       "with the state of the following parent inventories:\n"
                       ) % ((self.name, self.state)) +
                     "\n".join(['- %s (%s)' % (i.name, i.state)
                                for i in inconsistent_parents])))

    @api.one
    @api.constrains('location_id', 'parent_id')
    def _check_location_id(self):
        """Check if location is a child of parent inventory location"""
        if self.parent_id:
            loc = self.location_id
            parent_loc = self.parent_id.location_id
            if (loc.parent_left < parent_loc.parent_left or
                    loc.parent_right > parent_loc.parent_right):
                raise ValidationError("This location is not declared on "
                                      "the parent inventory\n"
                                      "It cannot be added.")

    @api.multi
    def action_cancel_inventory(self):
        """Cancel all children inventories"""
        for inventory in self:
            if inventory.inventory_ids:
                inventory.inventory_ids.action_cancel_inventory()
        super(HierarchicalInventory, self).action_cancel_inventory()

    @api.multi
    def prepare_inventory(self):
        """Prepare inventory and all the children

        The standard method for this is not modular, and directly records all
        the inventory lines. We cannot afford to waste the computation time
        needed to insert these lines (it can take tens of minutes on very
        large warehouses), just to ignore or delete them for the mere reason
        that they should be in sub-inventories. So instead, we'll prepare all
        the sub-inventories at the same time."""
        _logger.info("Generating the inventory lines")
        result = super(HierarchicalInventory, self).prepare_inventory()
        if not self.mapped("line_ids"):
            _logger.info("No lines have been generated")
            return result

        inv_with_children = self.filtered("inventory_ids")
        if inv_with_children:
            _logger.info("Dispatching the lines to the sub-inventories")
            self.env.cr.execute(
                """
                -- Find all sub-inventories where the line could be dispatched
                WITH possible_sub_inv (
                    line_id, inventory_id,
                    parent_left,
                    best_parent_left)
                AS (
                    SELECT
                        line.id,
                        sub_inv.id,
                        sub_inv.parent_left,
                        -- "deepest" of all possible sub-inventories
                        MAX(sub_inv.parent_left) OVER(PARTITION BY line.id)
                        FROM
                            stock_inventory_line AS line
                            INNER JOIN stock_location AS line_loc ON
                                line_loc.id = line.location_id
                            INNER JOIN stock_inventory AS main_inv ON
                                main_inv.id = line.inventory_id
                            INNER JOIN stock_inventory AS sub_inv ON
                                -- strictly more or less than main inventory
                                -- we're only interested in better matches
                                sub_inv.parent_left > main_inv.parent_left AND
                                sub_inv.parent_right < main_inv.parent_right
                            INNER JOIN stock_location AS sub_inv_loc ON
                                -- the location of the sub-inventory...
                                sub_inv_loc.id = sub_inv.location_id AND
                                -- ...must contain the location of the line
                                line_loc.parent_left >=
                                    sub_inv_loc.parent_left AND
                                line_loc.parent_right <=
                                    sub_inv_loc.parent_right)
                UPDATE stock_inventory_line
                SET inventory_id = (
                    SELECT inventory_id
                    FROM possible_sub_inv
                    WHERE line_id = stock_inventory_line.id AND
                    -- we only want the deepest sub-inventory
                    parent_left = best_parent_left)
                WHERE id IN %s""",
                (tuple(inv_with_children.mapped("line_ids").ids),))

            # Mark the sub-inventories prepared
            for inventory in inv_with_children:
                children = self.search(
                    [('parent_left', '>', inventory.parent_left),
                     ('parent_right', '<', inventory.parent_right),
                     ('state', '!=', 'confirm')])
                # We made a SQL UPDATE, the cache is not up-to-date
                children.invalidate_cache()
                children.write({'state': 'confirm', 'date': inventory.date})
        _logger.debug("Inventory prepared")
        return result
