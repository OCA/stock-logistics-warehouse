# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import logging
import os

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

_logger = logging.getLogger(__name__)


class ZippcubeController(http.Controller):
    DEVICE_SECRET_KEY = "ZIPPCUBE_SECRET"

    weight_keys = ("weight",)
    measures_keys = ("length", "width", "height")
    expected_keys = ("secret", "barcode") + weight_keys + measures_keys

    @http.route(
        "/stock/zippcube/<string:zippcube_device_name>/measurement",
        type="json",
        auth="none",
    )
    def measurement(self, zippcube_device_name):
        data = request.jsonrequest
        _logger.info("/measurement, data received: {}".format(data))

        env = request.env(su=True)
        device = env["measuring.device"].search(
            [("name", "=", zippcube_device_name), ("device_type", "=", "zippcube")],
            limit=1,
        )
        if not device:
            raise MissingError(
                _("No such Zippcube with name {}.").format(zippcube_device_name)
            )

        keys_missing = set(self.expected_keys) - set(data)
        keys_spurious = set(data) - set(self.expected_keys)
        if keys_missing or keys_spurious:
            error_msg = _(
                "Wrong data format: {}. Keys missing: {}, Unexpected keys: {}"
            ).format(data, keys_missing, keys_spurious)
            _logger.error(error_msg)
            raise ValueError(error_msg)

        self._check_secret(data["secret"])
        data.pop("secret")
        device._update_packaging_measures(data)
        return True

    def _device_get_secret(self):
        return os.environ.get(self.DEVICE_SECRET_KEY)

    def _check_secret(self, secret):
        if secret and secret == self._device_get_secret():
            return True
        else:
            raise AccessError(_("ZIPPCUBE_SECRET is wrong or missing"))
