#!/bin/bash

curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"secret": "abcdefg", "barcode":"xyz", "weight": "12,3", "length": "123,1", "width": "456,5", "height": "789,2"}' \
  http://localhost:8069/stock/zippcube/${DEVICE_NAME}/measurement
