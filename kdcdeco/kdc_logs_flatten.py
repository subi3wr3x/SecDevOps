#!usr/bin/python3

""" Given a MIT Kerberos Infratstructure that is shut down and migrated    """
""" we analyze the logs files to see who is still hitting the old boxes.   """

"""
This:

Feb 26 17:02:01 krb5.example.com krb5kdc[26922](info): AS_REQ (7 etypes {23 -133 -128 3 1 24 -135}) 192.168.1.3: \
ISSUE: authtime 1235664121, etypes {rep=23 tkt=16 ses=23}, kprutser@EXAMPLE.COM for krbtgt/EXAMPLE.COM@EXAMPLE.COM

becomes this:

|Feb 26 17:02:01|krb5.example.com|192.168.1.3|hostname_of_192.168.1.3|kprutser@EXAMPLE.COM|krbtgt/EXAMPLE.COM@EXAMPLE.COM|

for easy shuffling into Pandas 
"""

import os                                                        
import re                                                        
import sys                                                        
import glob,os                                                        
import random                                                        
import socket                                                        
import itertools                                                        
                                                     

sep='|'                                                                                
#Modify your KDC name pattern and 'REALM' as needed:
data_pat = re.compile("(2017-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]).*?([a-z][a-z]ikdc0[0-9]).*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):.*?([a-zA-Z0-9_\.\/\-]{2,50}@[a-zA-Z0-9\.]{2,20})\s+for\s+([a-zA-Z0-9_\.\/\-]{2,50}@REALM)")                                                        
kdc_csv="/tmp/kdc_all.txt"                                                                

open(kdc_csv,'w').close                                                                
#Put your logs in here to analyze """
os.chdir("/tmp/kdc-deco/")                                                                        

def lookup(x):                                                                                
    try:                                                                                        
        hn = socket.gethostbyaddr(x)[0]                                                                                        
    except socket.error as msg:                                                                                                
        print ('Error:',msg,'for',x)                                                                                                
        hn = 'nohost'                                                                                                        
    return hn                                                                                                        

seen={}     
#Modify your file name pattern as needed
for kdclog in glob.glob("kdc-*"):                                                                                                                
    with open(kdclog) as file:                                                                                                                        
    count=0                                                                                                                                
    for line in file:                                                                                                                                
        data_is_valid  = data_pat.search(line)                                                                                                                                
        if data_is_valid:                                                                                                                                        
            time    = data_is_valid.group(1) 
            kdc     = data_is_valid.group(2)                                                                                                                                                
            IP      = data_is_valid.group(3)                                                                                                                                                        
            cprinc  = data_is_valid.group(4)                                                                                                                                                                
            sprnc   = data_is_valid.group(5)                                                                                                                                                                        
        if IP not in seen:                                                                                                                                                                                
            print (IP,': No')                                                                                                                                                                                
            hn=lookup(IP)                                                                                                                                                                                        
            seen[IP]=hn                                                                                                                                                                                                
        else:                                                                                                                                                                                                        
            hn=seen[IP]                                                                                                                                                                                                        
    #print (IP,': Yes')                                                                                                                                                                                                                
    for x,y in seen.items():                                                                                                                                                                                                                        
        print (x,y)                                                                                                                                                                                                                                
    string=time + sep + kdc + sep + IP  + sep + hn + sep + cprinc + sep + sprnc + "\n"                                                                                                                                                                                                                                        
    with open(kdc_csv,'a') as mfyi:                                                                                                                                                                                                                                        
        mfyi.write(string)                                                                                                                                                                                                                                        
        count+=1                                                                                                                                                                                                                                        
        print(count)                                                                                                                                                                                                                                        
