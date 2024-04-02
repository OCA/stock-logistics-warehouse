# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestOrderpointGeneratorCommon


class TestOrderpointGeneratorEnabledDomain(TestOrderpointGeneratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        config = cls.config_obj.create({"use_product_domain": True})
        config.execute()

    def test_use_product_domain(self):
        """Check the state of the use product domain configuration parameter."""
        self.assertTrue(
            self.orderpoint_template_model.get_use_product_domain_state(),
            msg="Must be enabled",
        )

    def test_cron_create_auto_orderpoints(self):
        """Create auto orderpoints from cron"""
        self.orderpoint_template_model._cron_create_auto_orderpoints()
        orderpoints = self.orderpoint_model.search(
            [("product_id", "in", [self.p4.id, self.p5.id])]
        )
        self.assertTrue(orderpoints, msg="Must be created orderpoints")
