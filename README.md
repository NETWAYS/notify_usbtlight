notify_usbtlight.py is a script which controls a little 
[USB-Ampel](http://shop.netways.de/alarmierung/nagios-ampel.html) to turn red
when an icinga installation reports critical services, yellow when there are
only warnings and green if everything is good and well. 


#####Requirements

[Python 2.7](https://www.python.org/downloads/) and 
[clewarecontrol 2.5](http://www.vanheusden.com/clewarecontrol/) are required 
to run the script, you will also need to have a 
[classic ui](https://wiki.icinga.org/display/howtos/Setting+up+Icinga+Classic+UI+Standalone) 
running. Cron is recommended in order to automate the scripts execution.


#####Installation  
The script does not require any steps more steps to be taken once its 
requirements are are met, but in order for the traffic light to be updated the 
scripts needs to be called continuously.


#####Usage
`./notify_usbtlight.py --url url > [--user <user>] [--passwd < passwd >] [--hostgroup < hostgroup >] [--servicegroup < servicegroup >] [--debug]`

    --url           url to icinga
    --user          user for the webinterface
    --passwd        password of user
    --hostgroup     hostgroup filter
    --servicegroup  servicegroup filter
    --debug         verbose output for debugging


#####Run in crontab  
One way to do this is in a crontab:  
To do this run: `crontab -e`  (prepend sudo if your clewarecontrol needs it)  
And add `*/1 * * * * /path/to/script.py` to your cronfile.  
This way the script will be run every minute


#####License
Copyright (C) 2015 NETWAYS GmbH <support@netways.de>  
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
or see <http://www.gnu.org/licenses/>.

CONTRIBUTION SUBMISSION POLICY:

(The following paragraph is not intended to limit the rights granted
to you to modify and distribute this software under the terms of
the GNU General Public License and is only of importance to you if
you choose to contribute your changes and enhancements to the
community by submitting them to NETWAYS GmbH.)

By intentionally submitting any modifications, corrections or
derivatives to this work, or any other work intended for use with
this Software, to NETWAYS GmbH, you confirm that
you are the copyright holder for those contributions and you grant
NETWAYS GmbH a nonexclusive, worldwide, irrevocable,
royalty-free, perpetual, license to use, copy, create derivative
works based on those contributions, and sublicense and distribute
those contributions and any derivatives thereof.

Nagios and the Nagios logo are registered trademarks of Ethan Galstad.
