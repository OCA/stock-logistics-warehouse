This module adds an accounting date in both stock pickings and stock moves.
The accounting date from the picking is propagated to its corresponding stock move.
If a picking doesn't specify an accounting date, the stock move's accounting date
will be set to the 'Effective Date'. This value is then passed to the SVL's journal entry
accounting date.
