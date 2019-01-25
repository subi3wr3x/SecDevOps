#!/usr/bin/python3

""" Connect to Various TLS/SSL URLs and collect their expiration Dates """

""" Import Modules """
import io
import re
import sys
import ssl
import json
import socket
import pycurl
import OpenSSL
import subprocess
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
    """ Get Cert using openssl -  workaround for client auth sites """
    command="echo q | openssl s_client -connect " + host + ":" + str(port) + \
        " 2>/dev/null | openssl x509 -enddate -noout"
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
        URLS.append((virtual,tcpport,ipaddress))
    return URLS

def ConnectToHosts(URLS): 
    """   Connect to TLS servers. There  are likey 3 states:                     """
    """   Down,DNS issue, or SSL Issue - catch them all                          """
    """   Note: No provision for Slow Loris....                                  """
    """   Some vip "names" aren't DNS names..use the IP to connect               """
    urldict={}
    mychars=[':','GMT']
    for entry in URLS:
        url,tcpport,ipaddress = entry

        #If no DNS name, connect to IP
        #but always display hostname in HTML
        htmlname=url 
       
        dnsname=dnslookup(url)
        if dnsname == 'nohost':
            url=ipaddress
        status="NA"
        
        print ("Connect " + url)
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
        except ssl.SSLError as e:
            msg="SSL error/MATE" 
        except ConnectionResetError as e:
            msg="Connection Reset" 
        except ssl.SSLEOFError as e:
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
        urldict[(htmlname,tcpport)] = (msg,status) 
        """ urldict is (url/port) : ('expiredate','status') #Sucess  or    """
        """ urldict is (url/port) : ('conn  msgs','status') #Fail          """
    return urldict

def CalcDelta(urldict,app):
    """ Format HTML and determine color based on expiration data     """ 
    HTMLH='''\
    <html>
    <head>
        <link href="sort.css"  rel="stylesheet" type="text/css"/>
        <script type="text/javascript" src="jquery.js"></script> 
        <script type="text/javascript" src="sort.js"></script> 
        <title>{title}</title>
    </head> 
    <body> 
        <div id="wrapper">
        <h1>{h1}</h1>
        <table id="mytable" cellpadding="7" align="center"> 
        <tr>
            <th onclick="sort_name();">URL</th> 
            <th onclick="sort_age();">Days Left</th>
            <th>Expire Date</th>
            <th>Last Connection</th>
        </tr>
        <tbody id="table1">
    '''.format(h1=app,title=app)

    HTMLB="""
        </tbody>
        </table>
        <input type="hidden" id="name_order" value="asc">
        <input type="hidden" id="age_order" value="asc">
        </div>
    </body>
    </html>"""

    now=datetime.now()
    htmlfile = app + ".html"
    fh = open(htmlfile,'w')
    fh.write(HTMLH)
    fh.close()

    with open(htmlfile,'a') as fh:

        for urlandport,data in urldict.items(): 
            url,tcpport = urlandport
            msg,status = data
            #print(url)        
            if status == 'OK':
                delta      = data[0] - now
                days_left  = str(abs(delta.days))
                color      = 'green'  if int(days_left) > 400 \
                        else 'orange' if int(days_left) < 100 \
                        else 'red'
                sclr       = 'green'
            else:
                days_left  = 'NA'
                expiration = 'NA' 
                color      = 'blue'
                sclr       = 'blue'
                msg,status = status,msg
                #Swap dashboard order on failure  
            fh.write(
                     "<tr>" + "<td>" + url + " " + str(tcpport) + "</td>"     + \
                     "<td><font color="+color+">"+days_left+"</font>"+"</td>" + \
                     "<td><font color="+color+">"+ str(msg)+"</font>"+"</td>" + \
                     "<td><font color="+sclr+">"+str(status)+"</font>"+"</td>"+"</tr>"
                     )
    fh = open(htmlfile,'a')
    fh.write(HTMLB)
    fh.close()


applist = ["siteminder", "securid"]

for app in applist:
    cdbm_cert_data = app + ".json"
    print('Loading data from ' + cdbm_cert_data)
    try:
        with open(cdbm_cert_data) as fh:
            viplist = json.load(fh)
    except ValueError as e:
        print("Error loading json data from: " + cdbm_cert_data)
        sys.exit(5)
    except FileNotFoundError as e:
        print("Fatal: " + cdbm_cert_data + " does not exist")
        sys.exit(6)
    urlslist = CreateUrlList(viplist)
    urldict  = ConnectToHosts(urlslist)
    CalcDelta(urldict,app)
