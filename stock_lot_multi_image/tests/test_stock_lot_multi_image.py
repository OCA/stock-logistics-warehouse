# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestStockLotMultiImage(BaseCommon):
    @classmethod
    def _get_image_vals(cls, name, image_data):
        """Helper to get image values based on available fields"""
        comodel = cls.env["stock.lot"]._fields["image_ids"].comodel_name
        fields_list = cls.env[comodel]._fields
        vals = {"name": name}
        if "storage" in fields_list:
            vals["storage"] = "filestore"
        if "attachment_image" in fields_list:
            vals["attachment_image"] = image_data
        elif "image_1920" in fields_list:
            vals["image_1920"] = image_data
        if "owner_model" in fields_list:
            vals["owner_model"] = "stock.lot"
        return vals

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        field = cls.env["stock.lot"]._fields["image_ids"]
        comodel_fields = cls.env[field.comodel_name]._fields
        if "owner_model" not in comodel_fields:
            field.domain = []

        # Create test images
        cls.transparent_image = (  # 1x1 Transparent GIF
            b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
        )
        cls.black_image = (  # 1x1 Black GIF
            b"R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs="
        )
        cls.grey_image = (  # 1x1 Grey GIF
            b"R0lGODlhAQABAIAAAMLCwgAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw =="
        )

        # Create test product for lot
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
            }
        )

        # Create test lot with images
        cls.test_lot = cls.env["stock.lot"].create(
            {
                "name": "TEST/01/001",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
                "image_ids": [
                    Command.create(
                        cls._get_image_vals("Image 1", cls.transparent_image)
                    ),
                    Command.create(cls._get_image_vals("Image 2", cls.black_image)),
                ],
            }
        )
        cls.test_lot.invalidate_recordset()

    def test_compute_image_1920(self):
        """Test the computation of the main image"""
        self.assertTrue(self.test_lot.image_1920, "Main image should be computed")
        self.assertEqual(
            self.test_lot.image_1920,
            self.test_lot.image_ids[0].image_1920,
            "Main image should match the first image in image_ids",
        )

    def test_all_images(self):
        """Test multiple images are correctly attached"""
        self.assertEqual(len(self.test_lot.image_ids), 2)

    def test_add_image(self):
        """Test adding a new image"""
        initial_count = len(self.test_lot.image_ids)
        self.test_lot.write(
            {
                "image_ids": [
                    Command.create(self._get_image_vals("Image 3", self.grey_image))
                ]
            }
        )
        self.test_lot.invalidate_recordset()
        self.assertEqual(len(self.test_lot.image_ids), initial_count + 1)

    def test_remove_image(self):
        """Test removing an image"""
        initial_images = self.test_lot.image_ids
        self.assertTrue(len(initial_images) >= 2, "Test requires at least 2 images")

        # Store the second image for comparison
        second_image = initial_images[1].with_context(bin_size=False).image_1920

        # Remove the first image
        self.test_lot.write({"image_ids": [Command.delete(initial_images[0].id)]})
        self.test_lot.invalidate_recordset()

        # Check the count and the new first image
        self.assertEqual(len(self.test_lot.image_ids), len(initial_images) - 1)
        self.assertEqual(
            self.test_lot.with_context(bin_size=False).image_ids[0].image_1920,
            second_image,
        )

    def test_remove_all_images(self):
        """Test removing all images"""
        # Remove all images using unlink
        self.test_lot.write({"image_ids": [Command.clear()]})
        self.test_lot.invalidate_recordset()
        self.assertEqual(len(self.test_lot.image_ids), 0)
        self.assertFalse(self.test_lot.image_1920)

    def test_edit_image(self):
        """Test editing image metadata"""
        new_name = "Test name changed"
        self.test_lot.image_ids[0].name = new_name
        self.assertEqual(self.test_lot.image_ids[0].name, new_name)
