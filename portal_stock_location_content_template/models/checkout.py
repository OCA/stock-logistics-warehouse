from odoo import models


class Checkouts(models.Model):
    _name = "stock.location.content.check"
    _inherit = [
        "stock.location.content.check",
        "portal.mixin",
        "mail.thread",
        "mail.activity.mixin",
    ]

    def _compute_access_url(self):
        super(Checkouts, self)._compute_access_url()
        for checkout in self:
            checkout.access_url = "/my/checkouts/%s" % (checkout.id)
