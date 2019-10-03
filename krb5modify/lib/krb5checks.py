import os
import sys
import time
import getpass
import socket
import subprocess
import logging
import signal

class Krb5ReadyChecks:
    """ The methods check to see if we should execute or back off """
    """ or support pid files etc..                                """

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
        myhostip      = socket.gethostbyname(socket.gethostname())
        masterip      = socket.gethostbyname('krbadmin.your.com')
        masteripqa    = socket.gethostbyname('krbadminqa.your.com')
        masteripdev   = socket.gethostbyname('krbadmindev.your.com')
        masters       = { masterip : 1 , masteripqa : 1 , masteripdev : 1 }
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
                if count > 1:
                    msg=f"Backup not running after {count} tries - {user}  to be processed next"
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
                return Krb5ReadyChecks.check_if_backup_running(secs,count,user)
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
