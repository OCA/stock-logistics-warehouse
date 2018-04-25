# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class WizardStockRequestOrderKanbanAbstract(models.TransientModel):
    _name = "wizard.stock.request.kanban"
    _inherit = "wizard.stock.request.kanban.abstract"

    def barcode_ending(self):
        self.stock_request_id.action_confirm()
        return
