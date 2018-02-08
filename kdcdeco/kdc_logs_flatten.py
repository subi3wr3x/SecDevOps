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
import json
import socket                                                        

sep='|'
time_pat= "(2018-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.*?)"
kdc_pat="([a-z0-9]{1,99}.example.com)"
IP_pat="(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
clprinc_pat="([a-zA-Z0-9_\.\/\-]{2,99}@example.com)"
sprinc_pat= "([a-zA-Z0-9_\.\/\-]{2,99}@example.com)"
kdc_log_file_glob="mit_kdc_log*"                                                                
wdir = "/tmp/"
kdc_csv= wdir + "kdc_all.txt"
output_csv = wdir + 'kdc_all.txt'
dns_hosts = wdir + 'all_hosts_dns_map.txt'

data_pat = re.compile( time_pat                          \
                       + "\s+"                           \
                       + kdc_pat                         \
                       + "\s+krb5kdc\[[0-9]{1,10}\].*?"  \
                       + IP_pat                          \
                       + ":.*?"                          \
                       + clprinc_pat                     \
                       + "\s+for\s+"                     \
                       + sprinc_pat)
               
def lookup(x):                                                                                
    try:                                                                                        
        hn = socket.gethostbyaddr(x)[0]                                                                                        
    except socket.error as msg:                                                                                                
        print ('Error:',msg,'for',x)                                                                                                
        hn = 'nohost'                                                                                                        
    return hn                                                                                                        

os.chdir(".")      
if glob.glob(kdc_log_file_glob):
    
    #Create the local DNS cache file once for all kdc logs
    if os.path.exists(dns_hosts) and  os.path.getsize(dns_hosts) > 0:
        with open(dns_hosts, 'r') as fp:
            resolved_hosts = json.load(fp)
    else:
        print('Not loading',dns_hosts)
        resolved_hosts={}
    
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
                        print("Bailing: invalid sub matches:",e)
                        sys.exit()                                                                                                                                                                        
                    
                    if IP not in resolved_hosts:         #Lookup the hostname                                                                                                                                                                                 
                            print (IP,': Not yet seen')                                                                                                                                                                                
                            hn = lookup(IP)                                                                                                                                                                                        
                            resolved_hosts[IP] = hn                                                                                                                                                                                                
                    else:                                #We know the hostname                                                                                                                                                                     
                        hn = resolved_hosts[IP]                                                                                                                                                                                                        
                    
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
                    print('Warning: No matches found in ' + kdclog)
    
    with open(dns_hosts, 'w') as outfile:
        json.dump(resolved_hosts, outfile)
                                                                                                                                                                                                                                                 
else:
    print("No files found matching " + kdc_log_file_glob)
    