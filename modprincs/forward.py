#!/usr/bin/python3

import os
import sys
import re
import argparse
import datetime
import subprocess
import logging


class TicketUser:

        def __init__(self,logfile,kadmin,errfile,userfile,blklfile,realm):
            self.logfile   = logfile 
            self.errfile   = errfile 
            self.logfile   = logfile
            self.userfile  = userfile
            self.blklfile  = blklfile
            self.realm     = realm 
            self.kadmin    = kadmin

        def query_user(self,user):
            try:
                self.user = user  
                command = self.kadmin + " -q \"getprinc " + self.user + "@" + self.realm
                proch = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                output, error = proch.communicate()
                if error:
                    logging.error("KADMIN_ERROR:" + str(error))
                    return "KADMIN_ERROR"
                else:
                    output = output.decode("utf-8")
                    msg="QUERY: " + user + " allow_forwardable attribute is currently "
                    if "DISALLOW_FORWARDABLE" in output:
                        state="disabled"
                        logging.info(msg + state)
                    else:
                        state="enabled"
                        logging.info(msg + state)
            except Exception as e:
                logging.error("Query Setup Error:",e)

        def forwarding(self,state):
            try:

                if "on" in state:
                    flag="+"
                elif "off" in state:
                    flag="-"
                cmd = self.kadmin + " -q \"modprinc " + flag + \
                    "allow_forwardable " + self.user + "@" + self.realm 
                proch = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                output, error = proch.communicate()
                if error:
                    logging.error("KADMIN_ERROR:" + str(error))
                else:
                    output = output.decode("utf-8")
                    if "Principal \"" + self.user + "@" + self.realm + "\" modified" in output:
                        msg="ACTION: allow_forwardable flag turned " + state + " OK for " + self.user
                        logging.info(msg)
                    else:
                        msg="ACTION: allow_forwardable flag NOT turned " + state + " OK for " + self.user
                        logging.error(msg)
            except Exception as e:
                print("Modify Setup Error:",e)


        def OpenUserList(self):
            candidates = []
            try:
                with open(self.userfile,'r') as fh:
                    for user in fh:
                        candidates.append(user.rstrip())
                return candidates
            except Exception as e:
                print("UserList file problem:",e)
                sys.exit(1)
        
        def OpenBlacklist(self):
            blmembers = {}
            try:
                with open(self.blklfile,'r') as fh:
                    for user in fh:
                        blmembers[user.rstrip()] = 1
                return blmembers
            except Exception as e:
                print("BlackList file problem:",e)
                sys.exit(1)
    

if __name__ == '__main__':

    kadmin   = "/usr/sbin/kadmin.local"
    if os.path.exists(kadmin):
        pass
    else:
        print(kadmin + " does not exist - exiting")
        sys.exit(1)

    if os.access(kadmin,os.X_OK):
        pass
    else:
        print(kadmin + " is not-executable - exiting")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Disable Ticket Forwarding',usage="%(prog)s [-h] [--ulist /tmp/users.txt] [--blist /tmp/blacklist.txt]") 
    parser.add_argument('--ulist',metavar='\b', required = False, help = '/tmp/users.txt')
    parser.add_argument('--blist',metavar='\b', required = False, help = '/tmp/blacklist.txt')
    args = parser.parse_args()

    try:
        appname  = os.path.basename(__file__).split('.')[0]
        date     = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        realm    = "my.realm"
        blklfile = args.blist 
        if args.blist is None:
            blklfile = "/tmp/black_list.txt"
        userfile = args.ulist
        if args.ulist is None:
            userfile = "/tmp/users.txt"
        logfile  = "/tmp/" + appname + "_log_"     + str(date) + ".log"
        errfile  = "/tmp/" + appname + "_errfile_" + str(date) + ".txt"
        loglevel = "INFO"
        logging.basicConfig(filename=logfile, level=loglevel,format = \
            '%(levelname)s %(asctime)s %(module)s %(process)d %(message)s')
        ticket  = TicketUser(logfile,kadmin,errfile,userfile,blklfile,realm)
        myuserlist  = ticket.OpenUserList()
        myblacklist = ticket.OpenBlacklist()

        logging.info("Execution Starting for TASK:")
        for user in myuserlist:
            print("Processing user::" + user)
            if user not in myblacklist:
                ruser = re.match(r'[\w+\.?]+$',user)
                if ruser:
                    qresult = ticket.query_user(user)
                    if qresult is None:
                        ticket.forwarding("off")
                        ticket.query_user(user)
                else:
                    msg=user + " does not conform - skipping"
                    logging.error("PRE_EXEC:CHARSET_ERROR:" + msg)
                    pass
            else:
                msg=user + " in blacklist - skipping"
                logging.error("PRE_EXEC:BLACKLIST:" + msg)
                pass
    except Exception as ex:
        print("Main Setup Error:" + str(ex))
    logging.info("Execution Completed for TASK:")
