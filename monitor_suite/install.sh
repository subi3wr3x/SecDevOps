#!/bin/bash

INSTALL_PATH=${1:-"/usr/local/admin/bin"}
WEBROOT=${2:-"/var/www/html"}
WHAT=${3:-"all"}
INSTALLUSER=${4:-"www-data"}

#Check for pesky ending forward slashes
if echo $WEBROOT | grep \/\$  2>&1 > /dev/null ; then
        echo Warning: Trailing Slash Detected in Entered WEBROOT - Removing
	WEBROOT=$(echo $WEBROOT |sed -e "s/\/$//")
fi

if echo $INSTALL_PATH | grep \/\$ 2>&1 > /dev/null ; then
        echo Warning: Trailing Slash Detected in Entered INSTALL_PATH - Removing
	INSTALL_PATH=$(echo $INSTALL_PATH |sed -e "s/\/$//")
fi

if  ! getent passwd $INSTALLUSER; then
    /usr/sbin/adduser $INSTALLUSER  --disabled-password --system --shell /bin/bash  --gecos 'Monitor User'
fi


echo "Installing with INSTALL_PATH=$INSTALL_PATH WEBROOT=$WEBROOT SERVICES=$WHAT USER=$INSTALLUSER"

mkdir -p $INSTALL_PATH
mkdir -p /etc/monitorsuite/
mkdir -p $WEBROOT/images/
echo
echo Installation Details:
echo ---------------------
echo '#Main Files'
echo

smtp_inst () {

#smtp

mkdir -p $WEBROOT/smtpmon  && echo Created $WEBROOT/smtpmon
mkdir -p $WEBROOT/smtpmon/history
mkdir -p $WEBROOT/smtpmon/conf
mkdir -p $WEBROOT/smtpmon/status
mkdir -p $WEBROOT/smtpmon/pagelogs
mkdir -p $WEBROOT/smtpmon/checkfiles
chown -R $INSTALLUSER $WEBROOT/smtpmon
chmod -R 755 $WEBROOT/smtpmon

cp monitor_smtp.sh $INSTALL_PATH/monitor_smtp.sh && echo $INSTALL_PATH/monitor_smtp.sh installed OK
echo
chmod 755 $INSTALL_PATH/monitor_smtp.sh
cp monitor_smtp.conf $WEBROOT/smtpmon/conf/monitor_smtp.conf
cp smtpservers.txt $WEBROOT/smtpmon/conf
}

dns_inst () {

#dns

mkdir -p $WEBROOT/dnsmon  && echo Created $WEBROOT/dnsmon
mkdir -p $WEBROOT/dnsmon/history
mkdir -p $WEBROOT/dnsmon/conf
mkdir -p $WEBROOT/dnsmon/status
mkdir -p $WEBROOT/dnsmon/pagelogs
mkdir -p $WEBROOT/dnsmon/checkfiles
chown -R $INSTALLUSER $WEBROOT/dnsmon
chmod -R 755 $WEBROOT/dnsmon

cp monitor_dns.sh $INSTALL_PATH/monitor_dns.sh && echo $INSTALL_PATH/monitor_dns.sh installed OK
echo
chmod 755 $INSTALL_PATH/monitor_dns.sh
cp monitor_dns.conf $WEBROOT/dnsmon/conf/monitor_dns.conf
cp dnsservers.txt $WEBROOT/dnsmon/conf
}

web_inst () {

#web

mkdir -p $WEBROOT/webmon  && echo Created $WEBROOT/webmon
mkdir -p $WEBROOT/webmon/history
mkdir -p $WEBROOT/webmon/conf
mkdir -p $WEBROOT/webmon/status
mkdir -p $WEBROOT/webmon/pagelogs
mkdir -p $WEBROOT/webmon/checkfiles
chown -R $INSTALLUSER $WEBROOT/webmon
chmod -R 755 $WEBROOT/webmon

cp monitor_web.sh $INSTALL_PATH/monitor_web.sh && echo $INSTALL_PATH/monitor_web.sh installed OK
echo
chmod 755 $INSTALL_PATH/monitor_web.sh
cp monitor_web.conf $WEBROOT/webmon/conf/monitor_web.conf
cp webservers.txt $WEBROOT/webmon/conf
}

case "$WHAT" in

"dns" )
  dns_inst;;
"smtp" )
  smtp_inst;;
"web" )
  web_inst;;
"all" )
   dns_inst;smtp_inst;web_inst;;
* )
   echo "Failed to install: $WHAT was an Invalid entry!!";;
esac
echo
#Files

echo '#Support Files'
echo
cp banner.pl  $INSTALL_PATH && echo $INSTALL_PATH/banner.pl installed OK
chmod 755 $INSTALL_PATH/banner.pl

cp connect.pl  $INSTALL_PATH && echo $INSTALL_PATH/connect.pl installed OK
chmod 755 $INSTALL_PATH/connect.pl

cp send_alert.pl  $INSTALL_PATH && echo $INSTALL_PATH/send_alert.pl installed OK
chmod 755 $INSTALL_PATH/send_alert.pl

echo


sed s#XXXXX#$WEBROOT#g etc/monitorsuite/monitor_suite.conf > out
sed s#YYYYY#$INSTALL_PATH#g out > /etc/monitorsuite/monitor_suite.conf
if echo $WHAT |egrep -i "all|smtp" > /dev/null; then 
	sed s#QQQQQ#$INSTALL_PATH#g  monitor_smtp.conf   >  $WEBROOT/smtpmon/conf/monitor_smtp.conf
fi


cp critical.gif $WEBROOT/images/
cp ok.gif $WEBROOT/images/

echo
echo Please continue with configuration Steps at http://www.monitorsuite.net/install.php
echo
