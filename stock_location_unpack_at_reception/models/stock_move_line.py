# Copyright 2026 Camptocamp SA
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        # OVERRIDE: unpack here rather than after the move is done, as
        # stock.move._action_done() reserves the next moves of the chain right
        # after, and they must find the content without its package.
        res = super()._action_done()
        # Lines with no quantity are deleted by super().
        self.exists()._unpack_at_reception()
        return res

    def _unpack_at_reception(self):
        """Unpack what these done lines put in a location to unpack at reception.

        The packages are unpacked along with their containers, and the
        unpacking is logged on the transfers. The lines keep their destination
        package, so the package and its container stay visible in the moves
        history.
        """
        # Inventory moves only correct or relocate what is in the location (and
        # unpack moves have no destination package): nothing arrives there.
        lines = self.filtered(
            lambda ml: (
                ml.result_package_id
                and ml.location_dest_id.unpack_at_reception
                and not ml.move_id.is_inventory
            )
        )
        if not lines:
            return
        packages = self.env["stock.package"].search(
            [
                ("id", "parent_of", lines.result_package_id.ids),
                ("location_id.unpack_at_reception", "=", True),
            ]
        )
        unpacked_by_picking = {}
        for picking, picking_lines in lines.grouped("picking_id").items():
            # The packages of the lines and their containers.
            package_ids = {
                int(package_id)
                for path in picking_lines.result_package_id.mapped("parent_path")
                for package_id in path.split("/")[:-1]
            }
            # Kept from the lines: once empty, the packages have no location.
            unpacked_by_picking[picking] = (
                packages & packages.browse(package_ids),
                picking_lines.location_dest_id,
            )
        # The quants moved out of the packages go through _action_done() again,
        # as inventory moves, so they are not unpacked twice.
        packages.unpack()
        for picking, (packages, locations) in unpacked_by_picking.items():
            if not picking or not packages:
                continue
            picking.message_post(
                body=self.env._(
                    "Packages %(packages)s unpacked on arrival in %(locations)s.",
                    packages=", ".join(sorted(packages.mapped("name"))),
                    locations=", ".join(locations.mapped("display_name")),
                )
            )
