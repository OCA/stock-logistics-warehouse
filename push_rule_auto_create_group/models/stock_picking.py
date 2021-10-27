from odoo import models, api, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    push_group_id = fields.Many2one('procurement.group')

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        for picking in self.with_context(manual_push=True):
            picking.move_lines[0].first_backorder_move = True
            picking.move_lines._push_apply()
            break
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    first_backorder_move = fields.Boolean(default=False)
