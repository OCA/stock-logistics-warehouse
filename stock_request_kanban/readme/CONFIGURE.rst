If the barcode does not contain a CRC check digit on the kanban card, you should:

* Access on Development mode
* Access 'Settings / Technical / Parameters / System Parameters'
* Create a parameter with name 'stock_request_kanban.crc' and set it to value to 0

If the barcode contains a CRC check digit and you want to ignore it:

* Create a paramenter with name 'stock_request_kanban.ignore_crc' and set it to value to 1

If you want to change the format of the QR, you should:

* Access on Development mode
* Access 'Settings / Technical / Parameters / System Parameters'
* Create a parameter with name 'stock_request_kanban.barcode_format' and set
  the format of the barcode
