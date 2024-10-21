In common big warehouses, many users do operations at the same time.

During the picking process, one operator can do product collect and another
will do scrap processes. The first one can have collected the products but
not having validated the picking yet (just filled in the done quantities).

If the scrap operator scrapped one quantity done by the picking operator,
quantities will be incoherent in the picking has products have been physically
collected.

We want to ensure no scrap could be done if an operation is in progress.
