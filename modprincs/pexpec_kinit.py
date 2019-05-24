#!/usr/bin/python3

"Quick Helper Script to flow through potentially bad auth attempts"
"Verify what works and what shows up in splunk logs               "
"Not need to modprinc.py by helpful post implemenation-wise       "


import os
import sys
import time
import pexpect
import pexpect.exceptions
import pexpect.expect
import pexpect.utils


passw = "password"
kinit = "/usr/bin/kinit"

kinit_args= [
    "user@ -f",
    "-f       user",
    "-f -5    user",
    "-F -5    user",
    "-f -F -5 user",
    "-f           testuser",
    "-f -5        testuser",
    "-F -5        testuser",
    "-f -F -5     testuser",
    "-5 testuser@MYREALM",
    "-5 host/realm",
    "-5 -f testuser@MYREALM",
    "-5 -f host/realm"
    "-f user@",
    "test user -f",
    '\<script\>',
]

for each_arg in kinit_args:
    command=str(kinit) + " " +  str(each_arg)
    print (command)
    child = pexpect.spawn(command)
    try:
        i = child.expect(['Password for', 'Only one of', 'Extra arguments', 'Client not found','invalid option'])
        if i == 0:
            print("OK, Got Password prompt")
            child.sendline(str(passw))
        elif i == 1:
            print("OK: Only one of error")
        elif i == 2:
            print("OK: Extra arguments error")
        elif i == 3:
            print("OK: Client not found error")
        elif i == 4:
            print("OK: Invalid option error")
        else:
            print("Other")
        time.sleep(2)
    except Exception as err:
        print(str(err))
