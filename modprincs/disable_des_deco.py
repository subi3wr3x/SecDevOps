#!/usr/bin/python3.6

""" Given a list of proids, modify the enc type lists to rm DES                        """
"""     and allow an action to restore it                                              """
""" Use  kadmin.local and proc module from python to do so                             """
""" Input from CSV/text file (principal_name@is1.morgan)                               """
""" Allows blacklist input from CSV/text file (principal_name@is1.morgan)              """
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
import signal


class TicketUser:
    """ Class for manipulating principals """
    
    def __init__(self,logfile,kadmin,errfile,proidfile,blklfile):
        self.logfile   = logfile
        self.errfile   = errfile
        self.logfile   = logfile
        self.proidfile = proidfile
        self.blklfile  = blklfile
        self.kadmin    = kadmin

    def query_proid(self,proid):
        """ Query the princ,logging any errors      """
        """ Will return None on Success or an error """
        try:
            self.proid = proid 
            command = self.kadmin + " -q \"getprinc \"" + self.proid
            proch = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output, error = proch.communicate()
            if error:
                kadmin_error="KADMIN_QUERY_ERROR"
                logging.error(kadmin_error + str(error))
                return kadmin_error 
            else:
                output = output.decode("utf-8")
                output = self.rm_last_newline(output)
                msg="QUERY: " + proid + " attributes are currently: \n" + output
                logging.info(msg)
                return None
        except Exception as e:
            logging.error("Princ Query Error:",e)

    def rm_last_newline(self,string):
        """ Remove newline if it's the last character of a string """
        if string[-1] == "\n":
            return string[:-1]

    def mod_proid_encs(self,user,action):
        """ Modify the princ or log an Error """
        """ return OK, NOTOK, or sys.exit     """

        try:
            self.user   = user
            self.action = action 

            if action == "strengthen":
                cmd = f"{self.kadmin} -q \"cpw -randkey -e aes256-cts-hmac-sha1-96:normal,"\
                      f"aes128-cts-hmac-sha1-96:normal,des3-cbc-sha1:normal,arcfour-hmac:normal"\
                      f" -keepold {self.user}\""
            elif action == "restore":
                cmd = f"{self.kadmin} -q \"cpw -randkey -e aes128-cts-hmac-sha1-96:normal,"\
                      f"des3-cbc-sha1:normal,arcfour-hmac:normal,des-cbc-crc:normal"\
                      f" -keepold {self.user}\""

            proch = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,\
                stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output, error = proch.communicate()
            if error:
                kadmin_error="KADMIN_MOD_ERROR: "
                logging.error(kadmin_error + str(error))
            else:
                output  = output.decode("utf-8")
                success = f"Key for \"{self.user}\" randomized."
                if success in output:
                    status="OK"
                    msg     = f"ACTION: {self.user} modified {status} - action: {self.action}"
                    logging.info(msg)
                    return status
                else:
                    status="NOTOK"
                    msg     = f"ACTION: {self.user} modified {status} - action: {self.action}"
                    logging.error(msg)
                    return status
        except Exception as e:
            print("Modify Error:",e)

    def OpenUserList(self):
        """ Open the Userlist and return it's members """
        candidates = []
        try:
            with open(self.proidfile,'r') as fh:
                for user in fh:
                    candidates.append(user.rstrip())
            return candidates
        except Exception as e:
            print("UserList file problem:",e)
            sys.exit(1)

    def OpenBlacklist(self): 
        """ Open the Blacklist and return it's members """
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
        """ Return  OK if we are root, else exit  """
        whoami=getpass.getuser()
        if whoami != 'root':
            print("This script must be run as root")
            sys.exit(1)
        else:
            return "OK"

    def check_if_on_a_master():
        """ Return  OK if  we can are running on a master, else exit  """
        masterip     = socket.gethostbyname('krbadmin.ms.com')
        masteripdev  = socket.gethostbyname('itsikdcdev01.devin1.ms.com')
        myhostip     = socket.gethostbyname(socket.gethostname())
        masters      = { masterip : 1 , masteripdev : 1 }
        if myhostip not in masters:
            print("This script must be run on the master kdc (resolve to 'krbadmin')")
            sys.exit(1)
        else:
            return "OK"

    def check_kadmin_is_ready(kadmin_path):
        """ Return  OK if  we can use kadmin, else exit  """
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
        """ Return  OK if  we can write a pid file, else exit  """
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

    def check_if_backup_running(secs,count,user):
        """ Return True if backups are not running, otherwise recurse and try again """
        command      = "backup_kdb5.sh"
        ps_command   = "ps -ef |" + "grep -iw " + command + " | grep -iv grep"
        proch = subprocess.Popen(ps_command, shell=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        try:
            output, error = proch.communicate()
            #If we can't determine if backups are running or not, exit
            if error:
                msg="Command error: " +  str(error) + " exiting"
                logging.critical(msg)
                print(msg)
                sys.exit(1)
            if len(output) < 1:
                #TBD: make this possible debugging prettier
                #msg=user + " - " + command + " not running - count " + str(count)
                #logging.info(msg)
                #print(msg)
                if count > 1:
                    msg="Backup not running after - " + str(count) + " tries " + str(user) + " to be processed next"
                    logging.info(msg)
                    print(msg)
                    return True
                return True
            else:
                msg=user + " - " + command + " running - sleeping for " + str(secs) + " seconds - count " + str(count)
                logging.warning(msg)
                print(msg)
                time.sleep(secs)
                count+=1
                return ReadyChecks.check_if_backup_running(secs,count,user)
        except Exception as e:
            print("OS Error running " + ps_command + ":" +  str(e))
            sys.exit(1)

    def print_status(signum,stack):
        """ Inject a Summary message into the log 'now' """
        msg=f"Summary (In process) ==> Success: {success}, Errors: {errors}, Skipped-in-Error: "\
            f"{skipped}, Skipped-Non-conform: {nonconform}, Skipped-Blacklist: "\
            f"{blacklist}, Total: {total}"
        logging.info(msg)
        print(msg)

if __name__ == '__main__':


    try:
        #Local app Name/Pid file defined first because we may use in finally
        appname  = os.path.basename(__file__).split('.')[0]
        pid_file = '/tmp/' + appname + '.pid'

        #When we catch SIGUSR1, print a current status
        signal.signal(signal.SIGUSR1, ReadyChecks.print_status)

        #How often to retry checking if backup is running
        #bucheck  = 5    #Dev 
        bucheck  = 240   #Prod 

        #What to start counting backup tries from 
        scount   = 1 

        #Your  Kerberos Realm
        realm    = "yourrealm"

        #Path to kadmin
        kadmin   = "/path/to/kadmin.local"

        date     = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        #Ready Check Statuses are caught but not printed
        statusR0 = ReadyChecks.am_i_running(pid_file)
        statusR1 = ReadyChecks.check_if_root()
        statusR2 = ReadyChecks.check_if_on_a_master()
        statusR3 = ReadyChecks.check_kadmin_is_ready(kadmin)

        #Give the user some feedback if they  don't use the right syntax
        parser = argparse.ArgumentParser(description='Disable Ticket Forwarding',\
            usage="%(prog)s [-h] --REQ XXXXXX [--ulist /tmp/users.txt] [--blist /tmp/blacklist.txt]")
        parser.add_argument(   '--REQ',metavar='\b' ,required = True,  help =  '600XXXXXX')
        parser.add_argument( '--ulist',metavar='\b', required = False, help = '/tmp/users.txt')
        parser.add_argument( '--blist',metavar='\b', required = False, help = '/tmp/blacklist.txt')
        parser.add_argument('--action',metavar='\b', required = False, help = '[on|off]')
        args = parser.parse_args()

        #Turn the flag off or on here
        action   = "strengthen"
        if args.action is not None:
            action   = args.action
            if action not in ['strengthen','restore']:
                print("Must specify --action strengthen or  --action restore")
                sys.exit(1)

        #Ensure the REQ number is well formed 
        REQ     = args.REW
        if len(REQ) < 8: 
            print("REQ should be at least 8 numbers and start with a 6")
            sys.exit(1)

        blklfile = args.blist
        if args.blist is None:
            blklfile = "/tmp/black_list.txt"

        proidfile = args.ulist
        if args.ulist is None:
            proidfile = "/tmp/users.txt"

        logfile  = "/tmp/" + appname + "_log_"     + str(date) + ".log"
        errfile  = "/tmp/" + appname + "_errfile_" + str(date) + ".txt"
        loglevel = "INFO"
        logging.basicConfig(filename=logfile, level=loglevel,format = \
            '%(levelname)s %(asctime)s %(module)s %(process)d %(message)s')

        ticket  = TicketUser(logfile,kadmin,errfile,proidfile,blklfile)
        myuserlist  = ticket.OpenUserList()
        myblacklist = ticket.OpenBlacklist()

        exec_msg = "Execution Starting for REQ:" + REQ + " Upgrade Weak Encryption Keys "
        print(exec_msg)
        logging.info(exec_msg)

        errors=0; skipped=0; nonconform=0; success=0; blacklist=0; total=0
        for user in myuserlist:
            print("Processing user:" + user)
            if ReadyChecks.check_if_backup_running(bucheck,scount,user):
                if user not in myblacklist:
                    #principal should be alpha-num[.]@realm
                    ruser = re.match(r'[\w+\.?]+@' + re.escape(realm) +r'$',user)
                    if ruser:
                        qresult = ticket.query_proid(user)
                        if qresult is None:
                            mod_status=ticket.mod_proid_encs(user,action)
                            if mod_status == "OK":
                                success+=1
                            else:
                                #Modify failed, likely variable issue
                                #because query already succeeded
                                errors+=1
                            ticket.query_proid(user)
                            time.sleep(1)
                        else:
                            #Query Failed, probably does not exist
                            print("    Error: " + str(qresult))
                            errors+=1
                            pass #Local logging handled in the class
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
        msg=f"Execution Completed for REQ: {REQ}"
        print(msg)
        logging.info(msg)
        msg=f"Summary ==> Success: {success}, Errors: {errors}, Skipped-in-Error: "\
            f"{skipped}, Skipped-Non-conform: {nonconform}, Skipped-Blacklist: " \
            f"{blacklist},Total: {total}"
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
