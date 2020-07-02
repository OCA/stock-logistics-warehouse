# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock_vertical_lift.tests.common import VerticalLiftCase


class TrayTypeCommonCase(VerticalLiftCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.TrayType = cls.env["stock.location.tray.type"]
        cls.location_2b = cls.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_2b"
        )
        cls.location_2d = cls.env.ref(
            "stock_vertical_lift." "stock_location_vertical_lift_demo_tray_2d"
        )
        LocStorageType = cls.env["stock.location.storage.type"]
        cls.location_storage_type_buffer = LocStorageType.create(
            {"name": "VLift Buffer"}
        )
        cls.location_storage_type_small_8x = LocStorageType.create(
            {"name": "Small 8x", "only_empty": True}
        )
        cls.storage_types = (
            cls.location_storage_type_small_8x | cls.location_storage_type_buffer
        )
