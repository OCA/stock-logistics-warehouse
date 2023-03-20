# Copyright 2021 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)


def make_pkg_values(record, **kw):
    """Helper to generate test values for packaging."""
    name = record.name
    if record._name == "uom.uom":
        is_unit = True
        barcode = None
        qty = record.factor
    elif record._name == "product.packaging":
        qty = record.qty
        is_unit = False
        barcode = record.barcode
        if record.product_id:
            name = record.product_id._packaging_name_getter(record)
    values = {
        "id": record.id,
        "name": name,
        "qty": qty,
        "barcode": barcode,
        "is_unit": is_unit,
    }
    values.update(kw)
    return values
