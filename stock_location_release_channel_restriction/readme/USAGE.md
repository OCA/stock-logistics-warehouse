- When transferring stock movements with assigned release channel to a
  location where the restriction feature is enabled, the next moves should have
  the same release channel in order to be allowed to be transferred.
- When the last movement that restrict the location to a particular release channel
  has left the location, the release channel is removed on the location and all
  locations that belong to the same family and restriction:

                                 Output (No restriction)
            OUTPUT CASE 1 (Restriction)                                      OUTPUT CASE 2 (Restriction)
    CASE A (Restriction)  CASE B (Restriction)  CASE C (R)                        CASE D (Restriction)


    So, when an outgoing move is leaving the CASE A, the release channel restriction
    is removed from CASE B and CASE C too if no outgoing move is waiting in those locations
- To remove the restriction on some locations, select them in the list view and
  click on 'Remove Release Channel' action. It will force the restriction removal.
  If you select the 'Reset Family' option, the behaviour described here above is applied
  too.
