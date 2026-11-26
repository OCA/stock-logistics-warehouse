Run the put, get, count or tray release operation through the VLM workflow.
When a response is expected, the connector processes one response per socket
read (up to 1024 bytes). Each read is assumed to contain a complete response;
fragmented messages and multiple messages in one read are not reassembled
or separated.

The following device events keep the connector waiting:

- `201`: request accepted and queued.
- `202`: request processing started.
- `203`: carrier arrived; operator confirmation is still expected.

Any other code ends the wait. Code `0` indicates success. Device code `101`
is mapped to `-4`, and `107` to `-5`, in the configured response code field.
Other codes are returned unchanged. A missing or empty response code is
returned as `-999`.

Connection refusal returns `code = -1`, connection closure before a final
response returns `code = -2`, and a receive timeout returns `code = -3`.
These connection status dictionaries also include the submitted `task_id`.
Device response identifiers are not compared with the submitted identifier.

A positive connector timeout limits each socket read, not the total operation
time. With a timeout of zero, reads can block indefinitely. Tray calls skip
response reading and return immediately after sending the request.
