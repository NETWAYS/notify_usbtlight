#! /bin/python2
#
# COPYRIGHT:
# 
# This software is Copyright (c) 2015 NETWAYS GmbH, Jean-Marcel Flach
#                                <support@netways.de>
#
# (Except where explicitly superseded by other copyright notices)
#
#
# LICENSE:
#
# Copyright (C) 2015 NETWAYS GmbH <support@netways.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# or see <http://www.gnu.org/licenses/>.
#
# CONTRIBUTION SUBMISSION POLICY:
#
# (The following paragraph is not intended to limit the rights granted
# to you to modify and distribute this software under the terms of
# the GNU General Public License and is only of importance to you if
# you choose to contribute your changes and enhancements to the
# community by submitting them to NETWAYS GmbH.)
#
# By intentionally submitting any modifications, corrections or
# derivatives to this work, or any other work intended for use with
# this Software, to NETWAYS GmbH, you confirm that
# you are the copyright holder for those contributions and you grant
# NETWAYS GmbH a nonexclusive, worldwide, irrevocable,
# royalty-free, perpetual, license to use, copy, create derivative
# works based on those contributions, and sublicense and distribute
# those contributions and any derivatives thereof.
#
# Nagios and the Nagios logo are registered trademarks of Ethan Galstad.

import getopt, sys, json, urllib2, re
import subprocess

#print usage information
def usage(progname):
    print "usage:"
    print progname, """--url <url> [--user <user>] [--passwd <passwd>] [--hostgroup <hostgroup>] [--servicegroup <servicegroup>] [--debug]

    --url           url to icinga
    --user          user for the webinterface
    --passwd        password of user
    --hostgroup     hostgroup filter
    --servicegroup  servicegroup filter
    --debug         verbose output for debugging

Requires clewarecontrol v2.5 from http://www.vanheusden.com/clewarecontrol
DO NOT USE Version 1.0 (it's too slow!)
""", progname, """comes with ABSOLUTELY NO WARRANTY.
This program is licensed under the terms of the
GNU General Public License (see source code for details)
"""

#Check and set Ampel
def blinkenlights(status, debug):

    if debug:
        print 'Checking clewarecontrol for Ampel ("Switch1") serial'

    try:
        proc = subprocess.Popen(["clewarecontrol", "-l"], stdout=subprocess.PIPE)
    except OSError as err:
        print str(err)
        return 3

    out, err = proc.communicate()

    if proc.returncode != 0:
        print "Call to clewarecontrol failed with exitcode ", proc.returncode
        print err
        return 3

    if debug:
        print out

    match = re.search('.*Switch1.*serial number: ([0-9]*)', out)

    if not match.group(0):
        print "Could not find Ampel"
        return 3

    if debug:
        print "Found: ", match.group(1)
        print "Checking whether bulb ", status, " is already on"

    try:
        proc = subprocess.Popen(["clewarecontrol", "-c", "1", \
                "-d", str(match.group(1)), "-rs", str(status)],\
                stdout=subprocess.PIPE)
    except OSError as err:
        print str(err)
        return 3
    out, err = proc.communicate()

    if proc.returncode != 0:
        print "Call to clewarecontrol failed with exitcode ", proc.returncode()
        print err
        return 3

    if debug:
        print out

    matchBulb = re.search('On', out)
    if matchBulb != None:
        if debug:
            print "Bulb ", status, " is already on. Not touching Ampel."
        return status

    if debug:
        print "Bulb", status, " is not on, turning it on \
            (0=red, 1=yellow, 2=green)"

    #go over bulbs 0-2 and turning the right one on and the rest off
    for i in range(3):
        power = 0
        if i == status:
            power = 1
        if debug and power:
            print "Turn on Bulb ", i
        elif debug and not power:
            print "Turn off Blub ", i
        try:
            proc = subprocess.Popen(["clewarecontrol", "-c", "1", "-d", \
                    str(match.group(1)), "-as", str(i), str(power)], \
                    stdout=subprocess.PIPE)
            proc.wait()
        except OSError as err:
            print str(err)
            return 3

        if proc.returncode != 0:
            print "Call to clewarecontrol failed with exitcode ",\
                    proc.returncode()
            print err
            return 3
 
    return status


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", \
                ['url=', 'user=', 'passwd=', 'hostgroup=', 'servicegroup=', \
                'debug'])
    except getopt.error as err:
        print str(err)
        usage(sys.argv[0])
        return 3

    debug = False
    url = None
    user = None
    password = None
    hostgroup = None
    servicegroup = None

    for o, a in opts:
        if o == "--url":
            url = a
        elif o == "--user":
            user = a
        elif o == "--passwd":
            password = a
        elif o == "--hostgroup":
            hostgroup = a
        elif o == "--servicegroup":
            servicegroup = a
        elif o == "--debug":
            debug = True
        else: #getopt should already have thrown an unknow operator error
            print "Unknown operator ", o
            usage(sys.argv[0])
            return 2

    if url == None \
            or (user != None and password == None) \
            or (user == None and password != None):
        print "Missing or unallowed operator, check your url"
        usage(sys.argv[0])
        return 3
    #servicestatustypes=20 lists only critical and warning states
    #serviceprobs=262186 lists only active unacknowleged check which are
    #not in a scheduled downtime and in a hard state
    #see http://docs.icinga.org/latest/en/cgiparams.html#cgiparams-filter
    url += "/cgi-bin/status.cgi?host=all&jsonoutput&serviceprops=262186&servicestatustypes=20"

    if hostgroup != None:
        url += '&hostgroup=' + hostgroup
    if servicegroup != None:
        url += '&servicegroup=' + servicegroup
 
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, user, password)

    if debug:
        print "Building HTTP Auth handler"
    try:
        urllib2.install_opener(urllib2.build_opener(\
                    urllib2.HTTPBasicAuthHandler(passman)))
    except (urllib2.URLError, urllib2.HTTPError) as err:
        print str(err)
        return 3

    if debug:
        print "Sending request to: "
        print url
    req = urllib2.Request(url)
    try:
        reqData = urllib2.urlopen(req, None, 10)
    except urllib2.URLError as err:
        print str(err)
        return 3

    if debug:
        print "Recieved HTTP code ", reqData.getcode(), " from url:"
        print reqData.geturl()
        print "Loading and parsing json data"
    data = json.loads(reqData.read())
 
    #2=green, 1=yellow, 0=red
    status = 1
    
    if not data['status']['service_status']:
        status = 2
    else:
        for stati in data['status']['service_status']:
            if stati['status'] == "CRITICAL":
                status = 0
 
    if blinkenlights(status, debug) == 3:
        return 3
    
    if status == 2:
        print 'OK - Status "green" | green=1 yellow=0 red=0'
    elif status == 1:
        print 'WARNING - Status "yellow" | green=0 yellow=1 red=0'
    elif status == 0:
        print 'CRITICAL - Status "red".|green=0 yellow=0 red=1'

if __name__ == "__main__":
    main()
