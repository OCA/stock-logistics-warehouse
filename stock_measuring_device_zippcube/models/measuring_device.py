# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class MeasuringDevice(models.Model):
    _inherit = "measuring.device"

    device_type = fields.Selection(selection_add=[("zippcube", "Zippcube")])
