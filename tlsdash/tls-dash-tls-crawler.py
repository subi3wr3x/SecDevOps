#!/usr/bin/python3

""" Connect to Various TLS/SSL URLs and collect their expiration Dates """

import io
import re
import sys
import ssl
import json
import socket
import pickle
import pycurl
import OpenSSL
import subprocess
from collections import namedtuple
from datetime import date,time,datetime


"""                           Script Start                             """

""" NB:Issue31870 no timeout available for ssl.get_server_certificate  """
""" use socket.setdefaulttimeout instead                               """

socket.setdefaulttimeout(2)

def get_SSL_Expiry_Date(host, port) -> 'byte string':
    """ Get Cert; return expire date as 'ASN1 Generalized time string' """
    cert = ssl.get_server_certificate((host, port))
    x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
    return x509.get_notAfter()

def get_SSL_Expiry_DateCmd(host, port) -> 'text':
    """ Get Cert using openssl for the unfortunate client ssl workaround """
    command="timeout 5 bash -c \"echo q | openssl s_client -connect " \
        + host + ":" + str(port) + " 2>/dev/null \
        | openssl x509 -enddate -noout\""
    ph = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, \
        stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    output, error = ph.communicate()
    return output.decode('utf-8'),error

def dnslookup(url) -> 'text':
    """ See if a given DNS name is valid or not """ 
    try:
        hn = socket.gethostbyaddr(url)[0] 
    except socket.error as msg: 
        hn = 'nohost'
    return hn 

def CreateUrlList(viplist):
    """                         Data Extraction                            """
    """ Some URLs have port number appended in the lb_virtual.label field, """
    """ some don't, Attempt to keep the data in  URLS consistent.          """
    """ Always add tuple of virtual,port,ipaddress to URLS                 """
    URLS=[]
    patt=re.compile('[0-9]')
    for each in viplist['data']:
        virtual          = each['lb_virtual.label']
        vname,vsep,vport = virtual.rpartition('.')
        tcpport          = each['lb_virtual.port']
        ipaddress        = each['lb_virtual.ip_address']
        if patt.match(vport):
            virtual = vname
        if not ipaddress:
            ipaddress = "None"
        #Ignore these
        if tcpport in {80,0}:
            pass
        else:
           URLS.append((virtual,tcpport,ipaddress))
    return URLS

######################  Start Script ##################################
try:
    conffile="tls-dash.conf"
    with open(conffile) as fh:
        applist = fh.readlines()
except Exception as e:
    print("File Problem: " + str(e))
    sys.exit(5)

for line in applist:
    app,appid = line.split(":")
    cdbm_cert_data = app + ".json"
    print('\nLoading data from ' + cdbm_cert_data)
    try:
        with open(cdbm_cert_data) as fh:
            viplist = json.load(fh)
    except ValueError as e:
        print("Error loading Tai data from: " + cdbm_cert_data)
        sys.exit(5)
    except Exception as e:
        print("File Problem: " + str(e))
        sys.exit(6)

    URLS = CreateUrlList(viplist)

    dshdict = {}
    mychars=[':','GMT']
    dshbrd = namedtuple('DashData', ['EXPIREDATE','STATUS'])
    now=datetime.now()
    SOON=[];OK=[];DECO=[]; FAILED=[]

    for entry in URLS:

        url,tcpport,ipaddress = entry
        htmlname=url 

        dnsname=dnslookup(url)
        if dnsname == 'nohost':
            url=ipaddress
        status="NA"
        
        print("Connect to " + htmlname + " " + str(tcpport)) 
        try:
            expiredata = get_SSL_Expiry_Date(url,tcpport)
        except socket.timeout as e:
            msg="Connection Failed"
        except socket.gaierror as e:                            
            msg="Address related error"
        except TimeoutError as e:
            msg="Connection Timeout"
        except ConnectionRefusedError as e:
            msg="Connection Refused"
        except ConnectionResetError as e:
            msg="Connection Reset" 
        except ssl.SSLError as e:
            #print('here' + url)
            expiredata,error = get_SSL_Expiry_DateCmd(url,tcpport)
            if all(x in expiredata for x in mychars):
                status="OK"
                expdate = expiredata.split('=')[1].rstrip('\n')
                msg =  datetime.strptime(expdate,'%b %d %H:%M:%S %Y %Z') 
            else:
                msg="SSL Related error"
        except ssl.SSLEOFError as e:
            #print('here2' + url)
            expiredata,error = get_SSL_Expiry_DateCmd(url,tcpport)
            if all(x in expiredata for x in mychars):
                status="OK"
                expdate = expiredata.split('=')[1].rstrip('\n')
                msg =  datetime.strptime(expdate,'%b %d %H:%M:%S %Y %Z') 
            else:
                msg="SSL Related error"
        else:
            status="OK"
            msg = datetime.strptime(expiredata.decode('ascii'),'%Y%m%d%H%M%SZ')

        if status == 'NA':
            days_left = 'NA'
            print(" F " +htmlname,msg,status)
            FAILED.append((htmlname,tcpport,msg,days_left,status))
        else:
            #OK
            delta      = msg - now
            days_left  = str(delta.days)
            if int(days_left)    > 60:
                print(" O " +htmlname,msg,status)
                OK.append((htmlname,tcpport,msg,days_left,status))
            elif int(days_left)  < -7:
                print(" D " +htmlname,msg,status)
                DECO.append((htmlname,tcpport,msg,days_left,status))
            else:
                print(" S " +htmlname,msg,status)
                SOON.append((htmlname,tcpport,msg,days_left,status))
        #dshdict[((htmlname,tcpport))] = (msg,status,days_left)
    if len(SOON) < 1: 
        SOON.append(('NA','NA','NA','NA','NA'))
    if len(FAILED) < 1: 
        FAILED.append(('NA','NA','NA','NA','NA'))
    if len(DECO) < 1: 
        DECO.append(('NA','NA','NA','NA','NA'))
    if len(OK) < 1: 
        OK.append(('NA','NA','NA','NA','NA'))
    dshdict['SOON']   = SOON
    dshdict['OK']     =   OK 
    dshdict['DECO']   = DECO 
    dshdict['FAILED'] = FAILED 

######################  Save Data for Later  ##################################

    html_data = app + ".pickle"
    try:
        with open(html_data,'wb') as fh:
            pickle.dump(dshdict,fh)
    except Exception as e:
        print("File Problem: " + str(e))
        sys.exit(6)
