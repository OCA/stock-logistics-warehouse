# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class SlotVerificationRequest(models.Model):
    _name = 'stock.slot.verification.request'
    _inherit = 'mail.thread'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'stock.slot.verification.request') or ''
        return super(SlotVerificationRequest, self).create(vals)

    @api.one
    def _count_involved_moves(self):
        self.involved_move_count = len(self.involved_move_ids)

    @api.one
    def _count_involved_inv_lines(self):
        self.involved_inv_line_count = len(self.involved_inv_line_ids)

    name = fields.Char(string='Name', readonly=True)
    inventory_id = fields.Many2one(comodel_name='stock.inventory',
                                   string='Inventory Adjustment',
                                   readonly=True)
    inventory_line_id = fields.Many2one(comodel_name='stock.inventory.line',
                                        string='Inventory Line',
                                        readonly=True)
    location_id = fields.Many2one(comodel_name='stock.location',
                                  string='Location',
                                  required=True)
    state = fields.Selection(selection=[
        ('wait', 'Waiting Actions'),
        ('open', 'In Progress'),
        ('cancelled', 'Cancelled'),
        ('done', 'Solved')
    ], string='Status', default='wait')
    responsible_id = fields.Many2one(comodel_name='res.users',
                                     string='Assigned to')
    product_id = fields.Many2one(comodel_name='product.product',
                                 string='Product', required=True)
    notes = fields.Text('Notes')
    involved_move_ids = fields.Many2many(
        comodel_name='stock.move',
        relation='slot_verification_move_involved_rel',
        column1='slot_verification_request_id',
        column2='move_id',
        string='Involved Stock Moves')
    involved_move_count = fields.Integer(compute=_count_involved_moves)
    involved_inv_line_ids = fields.Many2many(
        comodel_name='stock.inventory.line',
        relation='slot_verification_inv_line_involved_rel',
        column1='slot_verification_request_id',
        column2='inventory_line_id',
        string='Involved Inventory Lines')
    involved_inv_line_count = fields.Integer(compute=_count_involved_inv_lines)

    @api.model
    def _get_involved_moves_domain(self):
        domain = [('product_id', '=', self.product_id.id), '|',
                  ('location_id', '=', self.location_id.id),
                  ('location_dest_id', '=', self.location_id.id)]
        return domain

    @api.model
    def _get_involved_lines_domain(self):
        domain = [('product_id', '=', self.product_id.id),
                  ('location_id', '=', self.location_id.id)]
        return domain

    @api.model
    def _get_involved_lines_and_locations(self):
        involved_moves = self.env['stock.move'].search(
            self._get_involved_moves_domain())
        involved_lines = self.env['stock.inventory.line'].search(
            self._get_involved_lines_domain())
        return involved_moves, involved_lines

    @api.one
    def action_confirm(self):
        self.state = 'open'
        involved_moves, involved_lines = \
            self._get_involved_lines_and_locations()
        self.involved_move_ids = involved_moves
        self.involved_inv_line_ids = involved_lines
        return True

    @api.one
    def action_cancel(self):
        self.state = 'cancelled'
        return True

    @api.one
    def action_solved(self):
        self.state = 'done'
        return True

    @api.multi
    def action_view_moves(self):
        action = self.env.ref('stock.action_move_form2')
        result = action.read()[0]
        result['context'] = {}
        moves_ids = sum([svr.involved_move_ids.ids for svr in self], [])
        if len(moves_ids) > 1:
            result['domain'] = \
                "[('id','in',[" + ','.join(map(str, moves_ids)) + "])]"
        elif len(moves_ids) == 1:
            res = self.env.ref('stock.view_move_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = moves_ids and moves_ids[0] or False
        return result

    @api.multi
    def action_view_inv_lines(self):
        action = self.env.ref(
            'stock_inventory_verification_request.action_inv_adj_line_tree')
        result = action.read()[0]
        result['context'] = {}
        line_ids = sum([svr.involved_inv_line_ids.ids for svr in self], [])
        if len(line_ids) > 1:
            result['domain'] = \
                "[('id','in',[" + ','.join(map(str, line_ids)) + "])]"
        elif len(line_ids) == 1:
            res = self.env.ref('stock_inventory_verification_request.'
                               'view_inventory_line_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = line_ids and line_ids[0] or False
        return result
