This module extends `stock_vlm_mgmt` to communicate with Kardex Vertical
Lift Modules (VLMs) over a TCP socket connection. It supports put, get,
count and tray release operations from Odoo.

Request templates, field separators and response layouts are configurable
per Kardex location. The connector exchanges UTF-8 messages terminated by
CRLF and processes intermediate device events until a final response is
received. Response task identifiers are not required or checked.

Tray calls send the command without waiting for a device response.
