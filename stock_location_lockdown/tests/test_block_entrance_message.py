from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestBlockEntranceMessage(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        cls.loc = env["stock.location"].create(
            {
                "name": "Has Stock",
                "usage": "internal",
            }
        )
        product = env["product.product"].create({"name": "P", "type": "product"})
        # create stock in that location (quant)
        env["stock.quant"]._update_available_quantity(product, cls.loc, 1.0)

    def test_message_has_no_double_spaces(self):
        with self.assertRaises(UserError) as err:
            # field name may differ; adjust to the real one (check model fields)
            self.loc.block_stock_entrance = True
        msg = str(err.exception)
        # Expect the exact sentence (or just assert no double spaces)
        self.assertNotRegex(msg, r"\s{2,}")
        self.assertIn("It is impossible to prohibit this location", msg)
