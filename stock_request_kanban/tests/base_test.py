# Copyright 2017 Creu Blanca
# Copyright 2017-2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from reportlab.graphics.barcode import getCodes

from odoo.tests.common import TransactionCase


class TestBaseKanban(TransactionCase):
    def pass_code(self, wizard, code):
        bcc = getCodes()[self.env["stock.request.kanban"].get_barcode_format()](
            value=code
        )
        bcc.validate()
        bcc.encode()
        wizard.on_barcode_scanned(bcc.encoded[1:-1])
