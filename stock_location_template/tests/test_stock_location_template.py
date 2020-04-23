# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockLocationTemplate(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestStockLocationTemplate, self).setUp(*args, **kwargs)

        self.stock_location_obj = self.env["stock.location"]
        self.stock_location_template_obj = self.env["stock.location.template"]

        self.location_template_id = self.stock_location_template_obj.create({
            "name": "Wagon - 10 Cells",
            "cells_nbr": 10,
            "digits": 2,
            "starting_nbr": 1,
            "cells_nomenclature": "CELL-%c",
            "auto_generate_locations": True,
        })

        self.location_template_2_id = self.stock_location_template_obj.create({
            "name": "Wagon - 20 Cells",
            "cells_nbr": 20,
            "digits": 2,
            "starting_nbr": 1,
            "cells_nomenclature": "SHELF-%c",
            "auto_generate_locations": True,
        })

        self.location_id = self.stock_location_obj.create({
            "name": "location_test",
            "usage": "internal",
            "location_template_id": self.location_template_id.id,
        })

    def test_01_assign_template_to_location(self):
        """
            We perform basic computation checks and we also check that all
            sub-locations have been created with the correct nomenclature
        """
        self.location_template_id._compute_location_count()
        self.assertEqual(self.location_template_id.location_count, 1)
        self.location_template_id._compute_cell_name_example()
        self.assertEqual(
            self.location_template_id.cell_name_example, "CELL-01")
        self.assertEqual(
            len(self.location_id.child_ids),
            self.location_template_id.cells_nbr
        )
        self.assertTrue(
            self.location_id.child_ids[0].filtered(
                lambda x: x.name == "CELL-01"
            )
        )

    def test_02_assign_template_to_location_with_template(self):
        """
            We try to assign a template to a location that already has a
            template and we assert that a ValidationError is launched
        """
        with self.assertRaises(ValidationError):
            self.location_id.write({
                "location_template_id": self.location_template_2_id.id
            })
