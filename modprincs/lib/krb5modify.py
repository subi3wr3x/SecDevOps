import re
import sys
import subprocess
import logging


class Krb5Modify:
    """ Class for manipulating principals """
    
    kdb_disfwd_flag   = "DISALLOW_FORWARDABLE"
    kdb_disalltx_flag = "DISALLOW_ALL_TIX"

    def __init__(self,kadminl,kadmin,svc_prn,spn,princfile,blklfile,errfile,logfile):
        self.kadminl   = kadminl
        self.kadmin    = kadmin
        self.svc_prn   = svc_prn 
        self.spn     = spn 
        self.princfile = princfile 
        self.blklfile  = blklfile
        self.errfile   = errfile
        self.logfile   = logfile

    def query_spn_attrs(self,spn):
        """ Query the princ,logging any errors      """
        """ Will return None on Success or an error """
        try:
            self.spn = spn 
            command = self.kadminl + " -q \"getprinc \"" + self.spn
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
                msg="QUERY: " + spn + " attributes are currently: \n" + output
                logging.info(msg)
                return None
        except Exception as e:
            logging.error("Princ Query Error:",e)

    def rm_last_newline(self,string):
        """ Remove newline if it's the last character of a string """
        if string[-1] == "\n":
            return string[:-1]

    def mod_spn_encs(self,user,action):
        """ Modify the princ or log an Error  """
        """ Always local with kadmin.local    """
        """ return OK, NOTOK, or sys.exit     """

        try:
            self.user   = user
            self.action = action 

            if action == "strengthen":
                cmd = f"{self.kadminl} -q \"cpw -randkey -e aes256-cts-hmac-sha1-96:normal,"\
                      f"aes128-cts-hmac-sha1-96:normal,des3-cbc-sha1:normal,arcfour-hmac:normal"\
                      f" {self.user}\""
            elif action == "restore":
                cmd = f"{self.kadminl} -q \"cpw -randkey -e aes128-cts-hmac-sha1-96:normal,"\
                      f"des3-cbc-sha1:normal,arcfour-hmac:normal,des-cbc-crc:normal"\
                      f" {self.user}\""

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
                    status = "OK"
                    msg    = f"ACTION: {self.user} modified {status} - action: {self.action}"
                    logging.info(msg)
                    return status
                else:
                    status  = "NOTOK"
                    msg     = f"ACTION: {self.user} modified {status} - action: {self.action}"
                    logging.error(msg)
                    return status
        except Exception as e:
            print("Modify Proid Error:",e)

    def query_user_fwd_flag(self,user):
        """ Query the princ or log an Error """
        try:
            self.user = user
            command = self.kadminl + " -q \"getprinc \"" + self.user
            proch = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output, error = proch.communicate()
            if error:
                logging.error("KADMIN_ERROR:" + str(error))
                return "KADMIN_ERROR"
            else:
                output = output.decode("utf-8")
                msg="QUERY: " + user + " " + Krb5Modify.kdb_disfwd_flag + " attribute is currently "
                if Krb5Modify.kdb_disfwd_flag in output:
                    state="set"
                    logging.info(msg + state)
                else:
                    state="not set"
                    logging.info(msg + state)
        except Exception as e:
            logging.error("Query Setup Error:",e)

    def mod_forward_flag(self,user,action,mode):
        """ Modify the princ or log an Error """
        """ return OK, NOTOK                 """
        try:

            self.user        = user 
            self.disfwd_mode = mode
            self.action      = action 

            if "disable" in self.action:
                flag="-"; what = 'set'
            elif "restore" in self.action:
                flag="+"; what = 'unset'

            if self.disfwd_mode == "local": 
                cmd = f"{self.kadminl} -q \"modprinc {flag}allow_forwardable {self.user}\""
            elif self.disfwd_mode == "remote": 
                cmd = f"{self.kadmin}  -p {self.svc_prn} -kt /var/spool/keytabs/{self.spn} -q \
                        modprinc {flag}allow_forwardable {self.user}"

            proch = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output, error = proch.communicate()
            if error:
                logging.error("KADMIN_ERROR:" + str(error))
            else:
                output = output.decode("utf-8")
                if "Principal \"" + self.user + "\" modified" in output:
                    msg=f"ACTION: {Krb5Modify.kdb_disfwd_flag} was {what} OK for {self.user}"
                    logging.info(msg)
                    return "OK"
                else:
                    msg=f"ACTION: {Krb5Modify.kdb_disfwd_flag} was NOT {what} OK for {self.user}"
                    logging.error(msg)
                    return "NOTOK"
        except Exception as e:
            print("Modify User FWD Flag Error:",e)

    def check_if_enabled(self,user):
        """ Trust, but Verify.                                 """
        """ What if the user was disabled/re-enabled recently? """
        try:
            self.user = user
            command = self.kadminl + " -q \"getprinc \"" + self.user
            proch = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output, error = proch.communicate()
            if error:
                logging.error("KADMIN_ERROR:" + str(error))
                return "KADMIN_ERROR"
            else:
                output = output.decode("utf-8")
                msg="PRE-EXEC-CHECK: " + user + " " +  Krb5Modify.kdb_disalltx_flag + " attribute is currently "
                if Krb5Modify.kdb_disalltx_flag in output:
                    state="set"
                    status="Yes"
                    logging.info(msg + state)
                    return status 
                else:
                    state="not set"
                    status="No"
                    logging.info(msg + state)
                    return status 
        except Exception as e:
            logging.error("Enabled Query Error:",e)

    def OpenUserList(self):
        """ Open the Principal list and return it's members """
        candidates = []
        try:
            with open(self.princfile,'r') as fh:
                for user in fh:
                    candidates.append(user.rstrip())
            return candidates
        except Exception as e:
            print("Principal List file problem:",e)
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
