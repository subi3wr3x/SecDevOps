#!/usr/bin/python3

""" Given a MIT Kerberos Infratstructure that is shut down and migrated    """
""" we analyze the logs files to see who is still hitting the old boxes.   """

"""
This log file:

Feb 26 17:02:01 krb5.example.com krb5kdc[26922](info): AS_REQ (7 etypes {23 -133 -128 3 1 24 -135}) 192.168.1.3: \
ISSUE: authtime 1235664121, etypes {rep=23 tkt=16 ses=23}, kprutser@EXAMPLE.COM for krbtgt/EXAMPLE.COM@EXAMPLE.COM

becomes this csv formatted line:

| Time          |     KDC        |CLient IP  |Client hostname        |Client Principal    |Service Principal             |    
|Feb 26 17:02:01|krb5.example.com|192.168.1.3|hostname_of_192.168.1.3|kprutser@EXAMPLE.COM|krbtgt/EXAMPLE.COM@EXAMPLE.COM|

for easy shuffling into Pandas
 
"""

import os                                                        
import re                                                        
import sys
import glob                                                        
import socket                                                        

sep='|'
year="2018"
time_pat=(year + "-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.*?")
realm="example.com"
kdc_pat="[a-z0-9]{1,99}." + realm
IP_pat="\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
clprinc_pat="[a-zA-Z0-9_\.\/\-]{2,99}@" + realm
sprinc_pat="[a-zA-Z0-9_\.\/\-]{2,99}@" + realm
kdc_log_file_glob="mit_kdc_log*"                                                                
kdc_csv="/tmp/kdc_all.txt"
data_pat = re.compile( (time_pat)                        \
                       + "\s+"                           \
                       + (kdc_pat)                       \
                       + "\s+krb5kdc\[[0-9]{1,10}\].*?"  \
                       + (IP_pat)                        \
                       + ":.*?"                          \
                       + (clprinc_pat)                   \
                       + "\s+for\s+"                     \
                       + (sprinc_pat) )
                
def lookup(x):                                                                                
    try:                                                                                        
        hn = socket.gethostbyaddr(x)[0]                                                                                        
    except socket.error as msg:                                                                                                
        print ('Error:',msg,'for',x)                                                                                                
        hn = 'nohost'                                                                                                        
    return hn                                                                                                        

os.chdir(".")                                                                        
seen={}     
if glob.glob(kdc_log_file_glob):
    #Zero out the destination if the source log files exist - everytime
    open(kdc_csv,'w').close                                                                                              
    for kdclog in glob.glob(kdc_log_file_glob):             
        for line in open(kdclog):                                                                                                                                
            data_is_valid  = data_pat.search(line)                                                                                                                                
            if data_is_valid:      
                try:
                    time    = data_is_valid.group(1) 
                    kdc     = data_is_valid.group(2)                                                                                                                                                
                    IP      = data_is_valid.group(3)                                                                                                                                                        
                    cprinc  = data_is_valid.group(4)                                                                                                                                                                
                    sprnc   = data_is_valid.group(5)
                except IndexError as e:
                    print("Bailing: no sub matches:",e)
                    sys.exit()                                                                                                                                                                        
                if IP not in seen:                                                                                                                                                                                
                        print (IP,': No')                                                                                                                                                                                
                        hn = lookup(IP)                                                                                                                                                                                        
                        seen[IP] = hn                                                                                                                                                                                                
                else:                                                                                                                                                                                                        
                    hn = seen[IP]                                                                                                                                                                                                        
                    string = time  \
                          + sep    \
                          + kdc    \
                          + sep    \
                          + IP     \
                          + sep    \
                          + hn     \
                          + sep    \
                          + cprinc \
                          + sep    \
                          + sprnc  \
                          + "\n"                                                                                                                                                                                                                                        
                    with open(kdc_csv,'a') as myfile:                                                                                                                                                                                                                                        
                        myfile.write(string)
            else:
                    print('No matches')                                                                                                                                                                                                                                        
else:
    print("No files found matching " + kdc_log_file_glob)
    