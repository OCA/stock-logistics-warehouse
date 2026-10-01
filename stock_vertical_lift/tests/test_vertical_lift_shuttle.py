from odoo.exceptions import ValidationError

from .common import VerticalLiftCase


class TestVerticalLiftShuttleShared(VerticalLiftCase):
    def test_shared_location_lifecycle(self):
        self.assertFalse(self.shuttle.use_shared_storage_location)
        # When ``use_shared_storage_location`` is False, always matches location_id
        self.shuttle.location_id = self.location_1b
        self.assertEqual(self.shuttle.shared_storage_location_id, self.location_1b)

        # Use shared storage location
        self.shuttle.use_shared_storage_location = True
        self.shuttle.shared_storage_location_id = self.location_2a
        self.assertEqual(self.shuttle.shared_storage_location_id, self.location_2a)

        # Stop using shared storage location
        self.shuttle.use_shared_storage_location = False
        self.assertEqual(self.shuttle.shared_storage_location_id, self.location_1b)

        # _check_shared_storage_location_id() constraints
        with self.assertRaises(ValidationError):
            self.shuttle.write(
                {
                    "use_shared_storage_location": True,
                    "shared_storage_location_id": False,
                }
            )
