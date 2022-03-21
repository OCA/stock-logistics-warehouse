# Copyright 2018 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_request_allow_virtual_loc = fields.Boolean(
        string="Allow Virtual locations on Stock Requests"
    )

    stock_request_send_confirm_message = fields.Boolean(string='Send Confirm Done messages on Stock Requests',
                                                        default=True)
