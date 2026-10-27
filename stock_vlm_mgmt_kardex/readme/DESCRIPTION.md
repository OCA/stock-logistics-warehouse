This module extends `stock_vlm_mgmt` to communicate with Kardex Vertical
Lift Modules (VLMs) over a TCP socket connection. It supports put, get,
count and tray release operations from Odoo.

Each Kardex location provides a format expression to build the outgoing
message. The expression is evaluated with Odoo's `safe_eval` and can use
Python f-strings to insert values from the request's `data` dictionary,
including the task identifier, machine address, carrier, coordinates,
quantity and additional information fields. Operation types are converted
to Kardex codes and quantities to integers before evaluating the expression.

The expression must return the complete message, including its terminator.
The connector currently expects the standard eleven-field, semicolon-separated
layout when extracting the outgoing task identifier and parsing responses.
Customizing the outgoing expression does not change the response parser.

When a response is expected, the connector matches it to the task identifier
and reports the machine result and confirmed quantity to Odoo. Tray calls
send the command without waiting for operator confirmation at the machine.
