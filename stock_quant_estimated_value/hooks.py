# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


def pre_init_hook(cr):
    cr.execute(
        """ALTER TABLE stock_quant
    ADD COLUMN estimated_value numeric
    DEFAULT 0"""
    )

    cr.execute(
        """UPDATE stock_quant AS sq
        SET estimated_value = sq.quantity * COALESCE(ip.value_float, 0)
        FROM product_product AS pr
        JOIN product_template pt ON pt.id = pr.product_tmpl_id
        LEFT JOIN ir_property ip ON ip.name = 'standard_price'
            AND substring(ip.res_id FROM '(([0-9]+.*)*[0-9]+)')::integer = pr.id
            AND regexp_replace(ip.res_id, '[^a-zA-Z]', '', 'g') = 'productproduct'
        WHERE pr.active = true AND pt.type = 'product'
        AND sq.location_id IN (SELECT id FROM stock_location WHERE usage = 'internal')
        AND sq.product_id = pr.id;
    """
    )
