# © 2021 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import csv
import io

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPartialPickingImportWizard(models.TransientModel):
    _name = "stock.partial.picking"
    _description = _("Stock Partial Picking")

    order_id = fields.Many2one("sale.order", required=True)
    file_upload = fields.Binary()

    def _read_csv(self):
        self.ensure_one()

        if not self.file_upload:
            return []

        data = base64.b64decode(self.file_upload).decode("utf-8-sig")
        buf = io.StringIO(data)
        reader = csv.DictReader(buf)
        return list(map(dict, reader))

    @api.model
    def find_country(self, value):
        # Try english first
        model = self.env["res.country"].with_context(lang="en_US")
        rec = model.search(["|", ("name", "=", value), ("code", "=", value)])
        if rec:
            return rec

        # Try german
        return model.with_context(lang="de_DE").search([("name", "=", value)])

    def action_import(self):
        self.ensure_one()

        line = self.order_id.order_line.filtered(
            lambda l: l.product_id.type == "product"
        )
        if len(line) != 1:
            raise UserError(_("Can't use an order with more than 1 storable product"))

        product = line.product_id
        parent = self.order_id.partner_id
        picking_type = self.env["stock.picking.type"].search(
            [("barcode", "=", "NK-DELIVERY")]
        )

        src_loc = picking_type.default_location_src_id
        dest_loc = picking_type.default_location_dest_id or self.env.ref(
            "stock.stock_location_customers"
        )

        for row in self._read_csv():
            country_name = row.get("Country")
            country = self.find_country(country_name)
            if not country:
                raise UserError(
                    _(
                        "Invalid country %s. Please check the Odoo"
                        "names or use the ISO country code"
                    )
                    % country_name
                )

            # Build the delivery address
            address = {
                "name": row["Name"],
                "street": row["Street"],
                "street2": row["Street 2"],
                "city": row["City"],
                "zip": row["ZIP"],
                "country_id": country.id,
                "type": "delivery",
                "parent_id": parent.id,
            }
            # Search if the address already exists otherwise create it
            domain = [(k, "=", v) for k, v in address.items()]
            partner = self.env["res.partner"].search(domain, limit=1)
            if not partner:
                partner = self.env["res.partner"].create(address)

            # Create the new picking
            picking = self.env["stock.picking"].create(
                {
                    "partner_id": partner.id,
                    "origin": self.order_id.name,
                    "picking_type_id": picking_type.id,
                    "location_id": src_loc.id,
                    "location_dest_id": dest_loc.id,
                }
            )

            self.env["stock.move"].create(
                {
                    "name": product.name,
                    "sale_line_id": line.id,
                    "picking_id": picking.id,
                    "group_id": self.order_id.procurement_group_id.id,
                    "product_uom": product.uom_id.id,
                    "product_id": product.id,
                    "product_uom_qty": row["Liefermenge"],
                    "location_id": src_loc.id,
                    "location_dest_id": dest_loc.id,
                }
            )
