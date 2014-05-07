meetlogindex
============

Project meetlogindex serves for the purpose of adding new meeting log entries
to the wiki page (index of meeting logs).

Say you have a regular meeting and store the zogbot meeting logs on one wiki
page (index), so it is easily accessible. Then you need to update the wiki page
after every meeting, which is too much manual work.

The meetlogindex can help, because it goes through the last zogbot meeting logs
and updates the wiki page for you.

The configuration is also stored on the wiki and the example below defines:

 * id of the entry -- just pick a name matching [a-z-]+
 * regexp for meeting rooms (fedora-meeting(-[1-5])? is usually used)
 * regexp for meeting name (yeah, meetlogindex need to distinguish your meeting
   between the others)
 * wikipage is where the index is placed (and where the link to the last log
   entry will be added). 

Example of the configuration available at
https://fedoraproject.org/wiki/User:Hhorak/Draft/meetlog-config:

{|
! Entry ID      !! regexp for meeting rooms !! regexp for meeting name                  !! wikipage where store the result (log index)
|-
| env-and-stack || fedora-meeting(-[1-5])?  || env(ironment)?([-_])?and([-_])?stack(s)? || Env_and_Stacks/Meeting_Logs
|}

