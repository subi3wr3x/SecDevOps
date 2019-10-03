#!/usr/bin/python3

""" krb5_modify                                                                        """
""" Given a list of users, remove DES                                                  """
""" Given a list of users, flip the DISALLOW_FORWARDABLE flag on or off                """
""" Uses kadmin.local and proc module from python to do so                             """
""" Input from CSV/text file (principal_name@realm)                                    """
""" Allows blacklist input from CSV/text file (principal_name@realm)                   """
""" Script will continue on user error for a principal and log it                      """
""" Output(log) contains date and TKT#, principal per line, status of execution,       """
""" error, summary of the execution                                                    """
""" Checks if root user and if on a master kdc                                         """

import os
import re
import sys
import time
import fcntl
import signal
import socket
import logging
import getpass
import argparse
import datetime
import subprocess
from functools import partial
from lib.krb5modify import Krb5Modify 
from lib.krb5checks import Krb5ReadyChecks

def print_status(stack,frame):
    """ Format summary statement """
    msg=f"Summary ==> Success: {success}, Errors: {errors}, Skipped-in-Error: "\
        f"{skipped}, Skipped-Non-conform: {nonconform}, Skipped-Blacklist:    "\
        f"{blacklist}, Is-Enabled: {enabled}, Total: {total}"
    print(msg)

#When we catch SIGUSR1, print a current status
signal.signal(signal.SIGUSR1, print_status)


if __name__ == '__main__':

    try:
        #Local app Name/Pid file defined first because we may use in finally
        appname  = os.path.basename(__file__).split('.')[0]

        #Local date
        date     = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        #Simple pid file
        pid_file = '/tmp/' + appname + '.pid'

        #Init counters
        errors=0; skipped=0; nonconform=0; success=0; blacklist=0; total=0; enabled=0

        #How often to retry checking if backup is running in seconds
        bucheck  = 240 

        #What to start counting backup tries from 
        scount   = 1 

        #Your  Kerberos Realm
        realm    = "JOHNO.COM"

        #Path to kadmin.local
        kadminl   = "/usr/local/sbin/kadmin.local"

        #Path to kadmin
        kadmin = "/usr/local/bin/kadmin"

        #Proid running remote kadmin commands (needs /var/spool/keytabs/$spn)
        spn = "kdcmaster"

        #Service Princ to run kadmin as (-p)
        svc_prn = spn + "/blah.your.com@" + realm 

        #How long to wait before each modification of each principal
        sleeptime = 1 

        #Ready Check Statuses are caught but not printed
        statusR0 = Krb5ReadyChecks.am_i_running(pid_file)
        statusR1 = Krb5ReadyChecks.check_if_root()
        statusR2 = Krb5ReadyChecks.check_if_on_a_master()
        statusR3 = Krb5ReadyChecks.check_kadmin_is_ready(kadmin)

        parser = argparse.ArgumentParser(description='Disable Ticket Forwarding',\
            usage="%(prog)s [-h] --tkt XXXXXX [--ulist /tmp/users.txt] [--blist /tmp/blacklist.txt]")
        parser.add_argument('--tkt'     ,metavar='\b' ,required = True,  help = 'XXXXXX')
        parser.add_argument('--project' ,metavar='\b' ,required = True,  help = '[desdeco|disfwd]')
        parser.add_argument('--blist'   ,metavar='\b' ,required = False, help = '/tmp/blacklist.txt')
        parser.add_argument('--ulist'   ,metavar='\b' ,required = False, help = '/tmp/users.txt')
        parser.add_argument('--disfwd_action'  ,metavar='\b' ,required = False, \
            help = '[disable|restore]')
        parser.add_argument('--disfwd_mode'    ,metavar='\b' ,required = False, \
            help = '[remote|local]')
        parser.add_argument('--desdeco_action' ,metavar='\b' ,required = False, \
            help = '[strengthen|restore]')

        args = parser.parse_args()

        tkt     = args.tkt
        #Modify as your Change Tracking system allows
        if len(tkt) < 8 or not tkt.startswith('X'):
            print("TKT should be at least 8 numbers and start with an X")
            sys.exit(1)

        project = args.project
        if project is None or project not in ['desdeco','disfwd']:
            print("Must specify --project desdeco or  --project disfwd")
            sys.exit(1)

        if project == "desdeco":
            action = args.desdeco_action
            disfwd_mode = None
            if action is None or action not in ['strengthen','restore']:
                print("Must specify --desdeco_action strengthen or --desdeco_action restore")
                sys.exit(1)
        elif project == "disfwd":
            action      = args.disfwd_action 
            disfwd_mode = args.disfwd_mode
            if action is None or action not in ['disable','restore']:
                print("Must specify --disfwd_action disable or  --disfwd_action restore")
                sys.exit(1)
            if disfwd_mode is None or disfwd_mode not in ['remote','local']:
                print("Must specify --disfwd_mode local or --disfwd_mode remote")
                sys.exit(1)

        blklfile = args.blist
        if args.blist is None:
            blklfile = "/tmp/black_list.txt"

        princfile = args.ulist
        if args.ulist is None:
            userfile = "/tmp/users.txt"

        logfile  = "/tmp/" + appname + "_log_"     + str(date) + ".log"
        errfile  = "/tmp/" + appname + "_errfile_" + str(date) + ".txt"
        loglevel = "INFO"
        logging.basicConfig(filename=logfile, level=loglevel,format = \
            '%(levelname)s %(asctime)s %(module)s %(process)d %(message)s')

        ticket  = Krb5Modify(kadminl,kadmin,svc_prn,spn,princfile,blklfile,errfile,logfile)
        myuserlist  = ticket.OpenUserList()
        myblacklist = ticket.OpenBlacklist()

        exec_msg = f"Execution Starting for TKT:{tkt} - {project}:{action} {disfwd_mode}"
        print(exec_msg)
        logging.info(exec_msg)

        for user in myuserlist:
            print("Processing user:" + user)
            if Krb5ReadyChecks.check_if_backup_running(bucheck,scount,user):
                if user not in myblacklist:
                    ruser = re.match(r'[\w+\.?\/?\-?]+@' + re.escape(realm) +r'$',user)
                    if ruser:
                        is_disabled = ticket.check_if_enabled(user)
                        if is_disabled == "No":
                            enabled+=1
                        if project == "disfwd":
                            query_method  = 'query_user_fwd_flag'
                            query_cmd     = f"ticket.{query_method}(user)"
                            modify_method = 'mod_forward_flag'
                            modify_cmd    = f"ticket.{modify_method}(user,action,disfwd_mode)"
                        elif project == "desdeco":
                            query_method  = 'query_spn_attrs'
                            query_cmd     = f"ticket.{query_method}(user)"
                            modify_method = 'mod_spn_encs'
                            modify_cmd    = f"ticket.{modify_method}(user,action)"

                        qresult = eval(query_cmd)
                        if qresult is None:
                            mod_status = eval(modify_cmd)
                            if mod_status == "OK":
                                success+=1
                            else:
                                #Modify failed, likely variable issue
                                #because query already succeeded
                                errors+=1
                            #Check your work after modd'ing
                            eval(query_cmd)
                            time.sleep(sleeptime)
                        else:
                            #Query Failed, probably does not exist
                            errors+=1
                            pass #Logging handled in the class
                    else:
                        msg=user + " does not conform - skipping"
                        nonconform+=1
                        logging.error("PRE_EXEC:CHARSET_ERROR:" + msg)
                        pass
                else:
                    msg=user + " in blacklist - skipping"
                    blacklist +=1
                    logging.error("PRE_EXEC:BLACKLIST:" + msg)
                    pass
            else:
                #You should never get here but log it just in case
                skipped+=1
                logging.error("Skipping " + str(user))
            total+=1
        msg=f"Execution Completed for TKT: {tkt}"
        print(msg)
        logging.info(msg)
        msg=f"Summary ==> Success: {success}, Errors: {errors}, Skipped-in-Error: " \
            f"{skipped}, Skipped-Non-conform: {nonconform}, Skipped-Blacklist:    " \
            f"{blacklist}, Is-Enabled: {enabled}, Total: {total}"
        print(msg)
        logging.info(msg)
    except Exception as ex:
        print("Main Setup Error:" + str(ex))
    finally:
        try:
            if os.path.exists(pid_file):
                os.remove(pid_file)
        except Exception as ex:
            print("Cannot remove " + pid_file + ":" +  str(ex))
