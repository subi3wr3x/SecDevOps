#!/usr/bin/python3

""" Given a list of is1.users, modify the allow_forwardable flag on or off; default    """
"""     action is 'off'.                                                                   """
""" Uses kadmin.local and proc module from pythn to do so                              """
""" Input from CSV/text file (principal_name@yourrealm)                               """
""" Allows blacklist input from CSV/text file (principal_name@yourrealm)              """
""" Script will continue on user error for a principal and log it                      """
""" Output(log) contains date and REQ, principal per line, status of execution, error  """
"""     summary of the execution                                                       """
""" Checks if root user and if on a master kdc                                         """

import os
import re
import sys
import time
import fcntl
import getpass
import socket
import argparse
import datetime
import subprocess
import logging


class TicketUser:


    def __init__(self,logfile,kadmin,errfile,userfile,blklfile):
        self.logfile   = logfile
        self.errfile   = errfile
        self.logfile   = logfile
        self.userfile  = userfile
        self.blklfile  = blklfile
        self.kadmin    = kadmin

    def query_user(self,user):
        try:
            self.user = user
            command = self.kadmin + " -q \"getprinc \"" + self.user
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

            #TODO: Make prettier. 
            cmd = self.kadmin + " " + "-q" + " " + "\"" + "modprinc" + " " + \
                flag + "allow_forwardable" + " " + self.user + "\""
            proch = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output, error = proch.communicate()
            if error:
                logging.error("KADMIN_ERROR:" + str(error))
            else:
                output = output.decode("utf-8")
                if "Principal \"" + self.user + "\" modified" in output:
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

class ReadyChecks:


    def check_if_root():
        whoami=getpass.getuser()
        if whoami != 'root':
            print("This script must be run as root")
            sys.exit(1)
        else:
            return "OK"

    def check_if_on_a_master():
        masterip     = socket.gethostbyname('master')
        masteripdev  = socket.gethostbyname('master-dev')
        myhostip     = socket.gethostbyname(socket.gethostname())
        masters      = { masterip : 1 , masteripdev : 1 }
        if myhostip not in masters:
            print("This script must be run on the master kdc (resolve to 'krb-master')")
            sys.exit(1)
        else:
            return "OK"

    def check_kadmin_is_ready(kadmin_path):
        if os.path.exists(kadmin_path):
            pass
        else:
            print(kadmin_path + " does not exist - exiting")
            sys.exit(1)

        if os.access(kadmin_path,os.X_OK):
            pass
            return "OK"
        else:
            print(kadmin_path + " is not-executable - exiting")
            sys.exit(1)

    def am_i_running(pid_file):
        if os.path.exists(pid_file):
            print(pid_file + " exits - exiting")
            sys.exit(0)
        else:
            try:
                with open(pid_file,'w') as fh:
                    fh.write(str(os.getpid()))
                    return "OK"
            except Exception as ex:
                print("Pid Error: " + str(ex))

    def check_if_backup_running(secs):
        command      = "backup_script.sh"
        ps_command   = "ps -ef |" + "grep -iw " + command + " | grep -iv grep"
        proch = subprocess.Popen(ps_command, shell=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        try:
            output, error = proch.communicate()
            #If we can't determine if backups are running or not, exit
            if error:
                logging.critical("Command error:" +  str(error) + "exiting")
                print("Command error:" +  str(error) + "exiting")
                sys.exit(1)
            if len(output) < 1:
                #logging.info(command + " not running")
                return True
            else:
                print(command + " running - sleeping for " + str(secs) + " seconds")
                logging.warning(command + " running - sleeping for " + str(secs) + " seconds")
                time.sleep(secs)
                ReadyChecks.check_if_backup_running(int(secs))
        except Exception as e:
            print("OS Error running " + ps_command + ":" +  str(e))
            sys.exit(1)


if __name__ == '__main__':

    try:
        realm    = "yourrealm"
        appname  = os.path.basename(__file__).split('.')[0]
        pid_file = '/tmp/' + appname + '.pid'
        kadmin   = "/usr/sbin/kadmin.local"
        date     = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        statusR0 = ReadyChecks.am_i_running(pid_file)
        statusR1 = ReadyChecks.check_if_root()
        statusR2 = ReadyChecks.check_if_on_a_master()
        statusR3 = ReadyChecks.check_kadmin_is_ready(kadmin)
        #print (statusR0, statusR1, statusR2,  statusR3)

        parser = argparse.ArgumentParser(description='Disable Ticket Forwarding',\
            usage="%(prog)s [-h] --REQ 600XXXXXX [--ulist /tmp/users.txt] [--blist /tmp/blacklist.txt]")
        parser.add_argument(   '--REQ',metavar='\b' ,required = True,  help =  '600XXXXXX')
        parser.add_argument( '--ulist',metavar='\b', required = False, help = '/tmp/users.txt')
        parser.add_argument( '--blist',metavar='\b', required = False, help = '/tmp/blacklist.txt')
        parser.add_argument('--action',metavar='\b', required = False, help = '[on|off]')
        args = parser.parse_args()

        action   = "off"
        if args.action is not None:
            action   = args.action
            if action not in ['off','on']:
                print("Must specify --action off or  --action on")
                sys.exit(1)

        REQ     = args.REQ
        if len(REQ) < 8 or not REQ.startswith('6'):
            print("REQ should be at least 8 numbers and start with a 6")
            sys.exit(1)

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

        ticket  = TicketUser(logfile,kadmin,errfile,userfile,blklfile)
        myuserlist  = ticket.OpenUserList()
        myblacklist = ticket.OpenBlacklist()

        exec_msg = "Execution Starting for REQ:" + REQ + " - Turning allow_forwardable flag " + action
        print(exec_msg)
        logging.info(exec_msg)

        for user in myuserlist:
            if ReadyChecks.check_if_backup_running(240):
                print(user)
                if user not in myblacklist:
                    ruser = re.match(r'[\w+\.?]+@' + re.escape(realm) +r'$',user)
                    if ruser.group(0):
                        print("Processing user:" + user)
                        qresult = ticket.query_user(user)
                        if qresult is None:
                            ticket.forwarding(action)
                            ticket.query_user(user)
                            time.sleep(1)
                        else:
                            pass #Logging handled in the class
                    else:
                        msg=user + " does not conform - skipping"
                        logging.error("PRE_EXEC:CHARSET_ERROR:" + msg)
                        pass
                else:
                    msg=user + " in blacklist - skipping"
                    logging.error("PRE_EXEC:BLACKLIST:" + msg)
                    pass
        logging.info("Execution Completed for REQ:" + REQ)
    except Exception as ex:
        print("Main Setup Error:" + str(ex))
    finally:
        try:
            os.remove(pid_file)
        except Exception as ex:
            print("Cannot remove " + pid_file + ":" +  str(ex))
