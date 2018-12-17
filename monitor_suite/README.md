# Monitor Suite - (vive 2005!)
This is the Source of: 
<P>
https://www.linuxjournal.com/article/8216 - 2005!
<br>
and
<br>
https://www.linuxjournal.com/article/8269 - 2005!

### Prerequisites
Bash/Linux
Install wget.
Install NET::SMTP Perl module.
Install NET::telnet Perl module.

### Installing
```
git clone https://github.com/jouellnyc/ShellandPerl/Monitor_Suite

```

```
The following steps are performed as the root user

Create a local user named monitorsuite.
adduser monitorsuite

Extract Files.
cd /tmp

tar zxvf monitor_suite.tgz


Install Monitor Suite using install.sh

Note1: the syntax is: ./install.sh path_to_install_scripts web_document_root

Note2: Do not enter a trailing slash for path_to_install_scripts or web_document_root!!


./install.sh /usr/local/admin/bin /var/www


Edit the main config file, /etc/monitorsuite/monitor_suite.conf
Set WEBSRV to the Fully Qualified Domain Name of the Web Server that will run monitor_suite.

Set at least one SMTP variable (i.e SMTP1,2,3) to the SMTP server to send alerts through.

Set RECIPIENT and CC (optional) to addresses receiving alerts.


Add Services you wish to monitor
Edit web_document_root/webmon/conf/urls.txt to add HTTP URLS to monitor

Edit web_document_root/dnsmon/conf/dnsservers.txt to add DNS Servers URLS to monitor

Edit web_document_root/smtpmon/conf/smtpservers.txt to add SMTP Servers to monitor


For monitor_dns.sh only:
Edit /etc/monitorsuite/monitor_dns.conf

Set HOSTCHECK as the Defined host to check for DNS queries.
```


### Usage
To Complete installation set up each script to run in cron for the user monitorsuite every 5 minutes.
crontab -e -u monitorsuite 

0,5,10,15,20,25,30,35,40,45,50,55 * * * * /usr/local/admin/bin/monitor_web.sh > /dev/null 2>&1 
0,5,10,15,20,25,30,35,40,45,50,55 * * * * /usr/local/admin/bin/monitor_dns.sh > /dev/null 2>&1 
0,5,10,15,20,25,30,35,40,45,50,55 * * * * /usr/local/admin/bin/monitor_smtp.sh > /dev/null 2>&1

Monitor Suite DashBoard for each service (dns,smtp,web) will be available at:
http://yourwebserver/xxxmon/xxxmon.html

I.E http://yourwebserver/webmon/webmon.html

### Screen Shots 
Webadmin Dashboard
<BR>
![Webadmin Dashboard](web_admin.jpg?raw=true "Webadmin Dashboard")
<BR>
ServerStats Dashboard
<BR>
![ServerStats Dashboad](sys_admin.jpg?raw=true "Webadmin Dashboard")

## Author
[https://github.com/jouellnyc](mailto:jouellnyc@gmail.com)

## License
This project is licensed under the MIT License
