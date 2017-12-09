#!usr/bin/python3

""" Given a MIT Kerberos Infratstructure that is shut down and migrated """
""" we analyze the logs files to see whos is still hit the old boxes.   """

import os                                                        
import re                                                        
import sys                                                        
import glob,os                                                        
import random                                                        
import socket                                                        
import itertools                                                        
import numpy as np                                                        
import pandas as pd                                                        
import requests                                                        

sep='|'                                                                                
data_pat = re.compile("(2017-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]).*?([a-z][a-z]ikdc0[0-9]).*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):.*?([a-zA-Z0-9_\.\/\-]{2,50}@[a-zA-Z0-9\.]{2,20})\s+for\s+([a-zA-Z0-9_\.\/\-]{2,50}@is1.morgan)")                                                        
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
for kdclog in glob.glob("kdc-*"):                                                                                                                
    with open(kdclog) as file:                                                                                                                        
    count=0                                                                                                                                
    for line in file:                                                                                                                                
        data_is_valid  = data_pat.search(line)                                                                                                                                
        if data_is_valid:                                                                                                                                        
            time    = data_is_valid.group(1)                                                                                                                                        
            kdc     = data_is_valid.group(2)                                                                                                                                                
            IP      = data_is_valid.group(3)                                                                                                                                                        
            proid   = data_is_valid.group(4)                                                                                                                                                                
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
    string=time + sep + kdc + sep + IP  + sep + hn + sep + proid + sep + sprnc + "\n"                                                                                                                                                                                                                                        
    with open(kdc_csv,'a') as mfyi:                                                                                                                                                                                                                                        
        mfyi.write(string)                                                                                                                                                                                                                                        
        count+=1                                                                                                                                                                                                                                        
        print(count)                                                                                                                                                                                                                                        
