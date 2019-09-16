# Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class Tests(TransactionCase):

    # Test Section
    def test_01_che_res_config_settings(self):
        vals = {
            'default_display_range': 30,
            'default_calculation_range': 365,
            'default_consumption_calculation_method': 'moves'
        }
        self.res_config = self.env['res.config.settings'].create(vals)
        self.res_config.write(vals)