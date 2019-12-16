import logging
import os

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class VerticalLiftController(http.Controller):
    @http.route(["/vertical-lift"], type="http", auth="public", csrf=False)
    def vertical_lift(self, answer, secret):
        if secret == os.environ.get("VERTICAL_LIFT_SECRET", ""):
            rec = request.env["vertical.lift.command"].sudo().record_answer(answer)
            return str(rec.id)
        else:
            _logger.error(
                "secret mismatch: %r != %r",
                secret,
                os.environ.get("VERTICAL_LIFT_SECRET", ""),
            )
            raise http.AuthenticationError()
