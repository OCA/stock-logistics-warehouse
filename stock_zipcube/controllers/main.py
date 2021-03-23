# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import os

from odoo import _, http
from odoo.exceptions import MissingError
from odoo.http import request

_logger = logging.getLogger(__name__)


class ZipcubeController(http.Controller):
    weight_keys = ("weight",)
    measures_keys = ("length", "width", "height")
    expected_keys = ("secret", "barcode") + weight_keys + measures_keys

    @http.route("/stock/zipcube/<int:id_>/measurement", type="json", auth="none")
    def measurement(self, id_):
        env = request.env(su=True)
        cubiscan = env["cubiscan.device"].browse(id_)
        if not cubiscan:
            raise MissingError(_("No such cubiscan"))
        data = request.jsonrequest
        if set(data) != set(self.expected_keys):
            _logger.error("wrong data format: %s", data)
            raise ValueError("the data format is incorrect")
        _logger.info("received %s", data)
        self._check_secret(data["secret"])
        # convert the float values passed as strings to floats
        data = self._convert_floats(data)
        cubiscan._update_packaging_measures(data)
        return True

    def _convert_floats(self, data):
        for key in self.weight_keys + self.measures_keys:
            value = data[key]
            if isinstance(value, str):
                value = float(value.replace(",", "."))
                if key in self.measures_keys:
                    # lengths are in cm -> convert to mm
                    value *= 10
                data[key] = value
        return data

    def _check_secret(self, secret):
        if secret and secret == os.environ.get("ZIPCUBE_SECRET"):
            return True
        else:
            _logger.error(
                "Zipcube secret mismatch: %r != %r",
                secret,
                os.environ.get("ZIPCUBE_SECRET", ""),
            )
            raise http.AuthenticationError()
