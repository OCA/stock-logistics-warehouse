# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base_tier_validation.tests.common import CommonTierValidation


class TestStockInventoryTierValidation(CommonTierValidation):
    def test_01_tier_definition_models(self):
        res = self.tier_def_obj._get_tier_validation_model_names()
        self.assertIn("stock.inventory", res)
