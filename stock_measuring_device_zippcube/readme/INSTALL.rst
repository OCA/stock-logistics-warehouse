To secure the communication, we use a pre-shared secret. Generate it with a
tool able to generate a random string, such as uuidgen. Run Odoo with an
environment variable called ZIPPCUBE_SECRET set to the value of the secret.

After you have configured the measuring device in Odoo, you need to configure the device itself.

Edit the language file on the computer attached to the device, and set the
following parameters (the secret value must be the one generated earlier)::

  REST_Body={"barcode":"%%VAR_NUMBER%%", "weight":"%%VAR_SCALE_WEIGHT%%",  "length":"%%VAR_LENGTH", "width":"%%VAR_WIDTH%%", "height":"%%VAR_HEIGHT%%", "secret": "<insert secret here>"}
  REST_BaseURL=http://<odoo_host_url>/stock/zippcube/<device_name>/measurement
  REST_ContentType=application/json
  REST_AcceptEncoding=gzip, deflate

For local testing you can use the script in `scripts/measurement.sh`
