import re
import sys
import subprocess
import logging

class TicketUser:
    """ Class for manipulating principals """
    
    def __init__(self,logfile,kadmin,errfile,svcprincfile,blklfile):
        self.logfile   = logfile
        self.errfile   = errfile
        self.logfile   = logfile
        self.svcprincfile = proidfile
        self.blklfile  = blklfile
        self.kadmin    = kadmin

    def query_svcprinc_attrs(self,proid):
        """ Query the princ,logging any errors      """
        """ Will return None on Success or an error """
        try:
            self.svcprinc = proid 
            command = self.kadmin + " -q \"getprinc \"" + self.svcprinc
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
                msg="QUERY: " + svcprinc + " attributes are currently: \n" + output
                logging.info(msg)
                return None
        except Exception as e:
            logging.error("Princ Query Error:",e)

    def rm_last_newline(self,string):
        """ Remove newline if it's the last character of a string """
        if string[-1] == "\n":
            return string[:-1]

    def mod_svcprinc_encs(self,user,action):
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

    def query_user_fwd_flag(self,user):
        """ Query the princ or log an Error """
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

    def mod_forward_flag(self,state):
        """ Modify the princ or log an Error """
        """ retun OK, NOTOK, or sys.exit     """
        try:

            if "on" in state:
                flag="+"
            elif "off" in state:
                flag="-"

            cmd = f"{self.kadmin} -q \"modprinc {flag}allow_forwardable {self.user}\""
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
                    return "OK"
                else:
                    msg="ACTION: allow_forwardable flag NOT turned " + state + " OK for " + self.user
                    logging.error(msg)
                    return "NOTOK"
        except Exception as e:
            print("Modify Error:",e)

    def check_if_enabled(self,user):
        """ Trust, but Verify.                                """
        """ What if the user was disabled/re-enabled recently? """
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
                msg="PRE-EXEC-CHECK: " + user + " -allow_tix attribute is currently "
                if "DISALLOW_ALL_TIX" in output:
                    state="set"
                    status="OK"
                    logging.info(status + ": " + msg + state)
                    return status 
                else:
                    state="not set"
                    status="NOTOK"
                    logging.error(msg + state)
                    return status 
        except Exception as e:
            logging.error("Enabled Query Error:",e)

    def OpenUserList(self):
        """ Open the Userlist and return it's members """
        candidates = []
        try:
            with open(self.svcprincfile,'r') as fh:
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
