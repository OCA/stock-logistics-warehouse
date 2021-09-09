# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class MeasuringDevice(AbstractComponent):
    _name = "measuring.device.base"
    _collection = "measuring.device"

    def test_device(self):
        """Test that the device is properly configured.

        Override to e.g. test the connection parameter or send a test command.

        :return: True on success, False otherwise"""
        return True

    def preprocess_measures(self, measures):
        """perform required parsing, key mapping and possible unit conversion

        :param measures: a dictionary passed to _update_packaging_measures
        :return: a dictionary containing values that will be written on the
        wizard line
        """
        return measures

    def post_update_packaging_measures(self, measures, packaging, wizard_line):
        """hook called after the update of the packaging or wizard line update.

        This method can be called to send notifications for instance.

        :return: None"""

    def get_measure(self):
        """Get a measure from the device

        the implementation must communicate with the device to trigger a
        measure. If this can be done synchronously, call
        _update_packaging_measures() to get the update"""
        raise NotImplementedError()
