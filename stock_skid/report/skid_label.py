# -*- encoding: utf-8 -*-

############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from collections import namedtuple

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.report import report_sxw


class SkidLabel(namedtuple("Label", "wizard label_data")):
    @property
    def production_lot_id(self):
        return self.wizard.prodlot_id.name or ''

    @property
    def product(self):
        return self.wizard.prodlot_id and self.wizard.prodlot_id.product_id

    @property
    def product_name(self):
        return self.product and self.product.name

    @property
    def product_code(self):
        return self.product and self.product.code

    @property
    def production_name(self):
        return ''

    @property
    def bom_name(self):
        return ''

    @property
    def machine(self):
        return ''

    @property
    def shift(self):
        return ''

    @property
    def quantity(self):
        return self.label_data["product_qty"]

    @property
    def uom(self):
        uom = self.product.uom_id
        return uom and uom.name

    @property
    def supervisor(self):
        return self.label_data["supervisor"]

    @property
    def packer_name(self):
        return self.wizard.packer_name

    @property
    def date(self):
        return time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @property
    def company_name(self):
        return self.label_data.get("company_name", "")


class SkidLabelParser(report_sxw.rml_parse):
    label_data = ()

    def __init__(self, cr, uid, name, context):
        super(SkidLabelParser, self).__init__(cr, uid, name, context=context)
        if context and context.get("label_data"):
            self.label_data = context["label_data"]

        self.localcontext.update({
            'labels': self.label_data,
            'time': time,
            'get_all_labels': self.get_all_labels,
        })

    def get_all_labels(self, objects):
        return [
            SkidLabel(o, l)
            for o, l in zip(objects, self.label_data)
        ]


report_sxw.report_sxw('report.stock_skid.report.skid_label',
                      'stock.skid.reprint.wizard',
                      'addons/stock_skid/report/skid_label.rml',
                      parser=SkidLabelParser,
                      header=False)
