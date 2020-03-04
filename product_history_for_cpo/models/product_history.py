#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

from odoo import models, api


class ProductHistory(models.Model):
    _inherit = "product.history"

    # Private section
    @api.multi
    def ignore_line_cpo(self):
        self.mark_line(True)
        context = self.env.context
        model = context.get('active_model', False)
        id = context.get('active_id', False)
        cpol = self.env[model].browse(id)
        cpol.displayed_average_consumption =\
            self.product_id.displayed_average_consumption
        cpol.view_history()

    @api.multi
    def unignore_line_cpo(self):
        self.mark_line(False)
        context = self.env.context
        model = context.get('active_model', False)
        id = context.get('active_id', False)
        cpol = self.env[model].browse(id)
        cpol.displayed_average_consumption =\
            self.product_id.displayed_average_consumption
        cpol.view_history()
