Configure the VLM connection on the stock location and select **Kardex**
as the vendor. Set the following fields to match the JMIF configuration:

- **Socket Message Format**: a Python format string with named placeholders,
  not a Python expression. For example:

  ```text
  {task_type},{task_id},{address},{carrier},{pos_x},{pos_y},{qty},{info1},{info2},{info3},{info4}
  ```

  All placeholders must exist in the request data. Numeric formatting such
  as `{qty:.0f}` is supported. The template does not automatically convert
  operation names to device codes or quantities to integers.
- **Separator**: separator used in requests and responses, for example `;`.
  After formatting the request, every comma is replaced with this separator,
  including commas inside field values.
- **Socket Format**: ordered response field names, separated by the configured
  separator. For example, with `;`:

  ```text
  task_type;task_id;address;carrier;pos_x;pos_y;qty;info1;info2;info3;info4
  ```

  This layout controls response parsing independently of the request template.
  Missing values become `None`; extra values are ignored.
- **Response Code Key**: name of the response field containing the device code,
  for example `task_type` in the layout above.

A single CRLF (`\r\n`) terminator is appended automatically to each request.
JMIF responses must also use CRLF as the message delimiter.

Configure JMIF to send a final confirmation after arrival: the connector
always treats code `203` as intermediate. A setup that ends the operation
at arrival without sending a final response is not supported by this workflow.
