# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models

from odoo.addons.queue_job.job import identity_exact


class RecomputeStockGroupReservationRate(models.TransientModel):
    _name = "recompute.stock.group.reservation.rate"
    _description = "Recompute the Reservation Rate for picking groups"

    group_id = fields.Many2one(
        comodel_name="stock.picking.type.group",
        required=True,
    )

    def recompute(self):
        for wizard in self:
            wizard.group_id.with_delay(
                description=_(
                    "Reservation Rate recomputation for %(group_name)s group",
                    group_name=wizard.group_id.display_name,
                ),
                identity_key=identity_exact,
            )._recompute_type_group_reservation_rate()
