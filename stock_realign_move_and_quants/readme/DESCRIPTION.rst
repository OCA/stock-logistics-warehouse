A bug in Odoo 12 leads to the desynchronisation of the stock
quants and the stock move lines. The root cause has yet to be found.
This modules fixes the symptoms and not the cause. It aims to
1. Realign the stock quants and the stock move lines
2. Correct on the fly future desynchronisation

To do that, we assume the source of truth are the move lines rather than
the quants.

More information on this issue: https://github.com/odoo/odoo/issues/62139
