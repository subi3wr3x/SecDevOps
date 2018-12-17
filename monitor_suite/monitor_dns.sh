#!/bin/bash
#
# Title      :   Monitor_dns.sh
# Author     :   john@monitorsuite.net
# Purpose    :   Check DNS servers
#                and save a history
#
# Submit as
#
#         #Monitor_dns.sh
#         0,5,10,15,20,25,30,35,40,45,50,55 * * * * /usr/local/admin/bin/monitor_dns.sh
#
#         in crontab to monitor every 5 minutes
#
######################################################################
# Start Script - Do not touch below this line !!!
######################################################################
SRV_CONF_FILE="/etc/monitorsuite/monitor_suite.conf"
source $SRV_CONF_FILE
DNS_CONF_FILE="$WEBROOT/dnsmon/conf/monitor_dns.conf"
source $DNS_CONF_FILE
trap clean_up INT QUIT TERM

#############################################
# A. Are all the binaries/support files  OK?
#############################################

which awk       2>&1 > /dev/null  || { echo AWK       does not exist ; exit 1; }
which basename  2>&1 > /dev/null  || { echo BASENAME  does not exist ; exit 1; }
which cut       2>&1 > /dev/null  || { echo CUT       does not exist ; exit 1; }
which date      2>&1 > /dev/null  || { echo DATE      does not exist ; exit 1; }
which grep      2>&1 > /dev/null  || { echo GREP      does not exist ; exit 1; }
which hostname  2>&1 > /dev/null  || { echo HOSTNAME  does not exist ; exit 1; }
which netstat   2>&1 > /dev/null  || { echo NETSTAT   does not exist ; exit 1; }
which ping      2>&1 > /dev/null  || { echo PING      does not exist ; exit 1; }
which sed       2>&1 > /dev/null  || { echo SED       does not exist ; exit 1; }

[[ -e $COMMAND         ]]    || { echo COMMAND: $COMMAND                    does not exist ; exit 1; }
[[ -e $SRV_CONF_FILE   ]]    || { echo SRV_CONF_FILE:  $SRV_CONF_FILE       does not exist ; exit 1; }
[[ -e $DNS_CONF_FILE  ]]    || { echo  DNS_CONF_FILE: $DNS_CONF_FILE        does not exist ; exit 1; }
[[ -e $CONNECT         ]]    || { echo CONNECT: $CONNECT                    does not exist ; exit 1; }
[[ -e $SERVERSFILE     ]]    || { echo SERVERSFILE: $SERVERSFILE            does not exist ; exit 1; }
[[ -e $SMTPALERT       ]]    || { echo SMTPALERT: $SMTPALERT                does not exist ; exit 1; }
[[ -z $DASHBRD         ]]    && { echo DASHBRD must have a value.                          ; exit 1; }
[[ -z $WEBROOT         ]]    && { echo WEBROOT must have a value.                          ; exit 1; }

umask 022

I_AM_RUNNING_FILE="$WEBROOT/$SCRPTHOME/checkfiles/$(basename $0)_is_running.txt";

if [[ -e $I_AM_RUNNING_FILE   ]];then
    echo  "Warning: Another copy of $0 may be running"
    echo  "If you are sure it's not, run the following command:"
    echo  "rm $I_AM_RUNNING_FILE"
    echo  "Then rerun $0"
    exit 1
else
    touch $I_AM_RUNNING_FILE
fi
###########################
# B. Functions
###########################
report () {

STATE=$1
COLOR=$2

cat > $STAT <<EOF
<HTML>
<HEAD><TITLE> $SVC Service Status for $SRV: $STATE </TITLE></HEAD>
<BODY>
<H3>$SVC Service Status for $SRV: $COLOR $STATE $EF </H3>
<P>
EOF

cat >> $STAT <<EOF
<TABLE CELLPADDING=3 CELLSPACING=0 BORDER=1>
<TR><TH colspan=3> Checks </TH></TR>
<TR><TH> $SVC </TH><TH>Ping </TH><TH>Port $PORT</TH></TR>
<TR><TD> $NC </TD\><TD> $PC </TD><TD> $TC </TD></TR>
</BODY>
</HTML>
EOF

echo  >> $WLOG
}


mail_alert () {

STATE="$1"
SUBJECT="$SVC Service for $SRV is $STATE on $DAYNAME at $HOUR:$MIN"
BODY="

$(date)

Please review this log for full details:
$EMLINK

"
#Send to secondary SMTP servers if first fails
$SMTPALERT "$SMTP1" "$SUBJECT" "$BODY" "$RECIPIENT" "$CC" 2> $MLOG  || \
$SMTPALERT "$SMTP2" "$SUBJECT" "$BODY" "$RECIPIENT" "$CC" 2> $MLOG  || \
$SMTPALERT "$SMTP3" "$SUBJECT" "$BODY" "$RECIPIENT" "$CC" 2> $MLOG
date >> $WLOG

}

clean_up () {
	rm -f $I_AM_RUNNING_FILE
	exit $1
}

#Start Actual Commands

################################
# C. HTML and other variables
################################

LINKTAG="</A><BR>"
REDIMG="<IMG SRC="../../images/critical.gif">"
GREENIMG="<IMG SRC="../../images/ok.gif">"
GREEN="<font color="#348017">"
RED="<font color="#C11B17">"
EF="</font>"

HOUR=$(date +%H)
MIN=$(date +%M)
DAY=$(date +%d)
SECS=$(date +%S)
YEAR=$(date +%EY)
MNTH=$(date +%B)
DAYNAME=$(date +%A)

SVC="DNS"

################################
# D. Are we on the network?
################################
cd $WEBROOT/$SCRPTHOME || exit 1

#OK to assume one default gateway
ping -c  2 $(netstat -nr | grep UG  | awk '{ print $2 }')  > /dev/null
if (( $? != 0 )); then

    echo "Not on Network - Exiting" > $DASHBRD
    exit 1

fi

##############################
# E. Create basic HTML Page
##############################
NUM_OF_SERVERS=$(wc -l $SERVERSFILE |  cut -b 1-2)
cd $WEBROOT/$SCRPTHOME || exit 1

cat > $DASHBRD <<EOF
<HTML>
<HEAD><TITLE>Monitor_$SVC (Monitoring $NUM_OF_SERVERS $SVC Servers) </TITLE>
<META http-equiv="refresh" content="30"></HEAD>
<BODY>
<P>
EOF

date >> $DASHBRD

cat >> $DASHBRD <<EOF
- <A HREF="http://$WEBSRV/$SCRPTHOME/history">History</A>
<P>
<TABLE CELLPADDING=3 CELLSPACING=0 BORDER=1>
<TR><TH>$SVC Server</TH><TH>Status</TH><TH>Log</TH></TR>
EOF

##############################
# F. Main foreach loop for SVC
##############################

for SRV in  $(cat $SERVERSFILE);
do
	mkdir -p $WEBROOT/$SCRPTHOME/history/$YEAR/$MNTH/$DAY/$SRV
	CMDLINE="$COMMAND -W $TIMEOUT -R $RETRIES $HOSTCHECK. $SRV"
	WLOG="history/$YEAR/$MNTH/$DAY/$SRV/$SRV.$HOUR.$MIN.$SECS.LOG"
	WLOGLINK="<A HREF=\"http://$WEBSRV/$SCRPTHOME/$WLOG\">"
	CHECKFILE="$WEBROOT/$SCRPTHOME/checkfiles/down.$SRV"
	EMLINK="http://$WEBSRV/$SCRPTHOME/$WLOG"
	MLOG="history/$YEAR/$MNTH/$DAY/$SRV/smtp.$SRV.$HOUR.$MIN.$SECS.LOG"
	SHOW="http://$WEBSRV/$SCRPTHOME/status/$SRV.html"
	STAT="$WEBROOT/$SCRPTHOME/status/$SRV.html"
        PORT="53"


	date >           $WLOG
	#Don't switch order... 
	echo
        echo "Starting to check $SVC Service for $SRV"
        echo "  Checking $SRV 1st attempt"

	TC="NA"  
	PC="NA"   
	NC="NA"   

	#Check #1 - Main Service  Check
	echo                  >> $WLOG
	echo "$SVC Check:"    >> $WLOG
	echo "=========="     >> $WLOG
	echo "$CMDLINE"       >> $WLOG
	echo ""               >> $WLOG



	$CMDLINE  >> $WLOG 2>&1
	if (( $? != 0 ));then 

                echo "  Checking $SRV 2nd attempt"

		$CMDLINE  > /dev/null 2>&1
		if (( $? != 0 ));then 

			STATE="down"
			COLOR="$RED"
			NC="$REDIMG"

			echo "  $SVC on $SRV is $STATE" 
                        echo "" 												  >> $WLOG
                        echo "$SVC CHECK ran twice without success."                                                              >> $WLOG

			echo  \<TR\>\<TD\>\<A HREF\="$SHOW"\>$SRV\<\/A\> \</TD\>                                                  >> $DASHBRD
			echo  \<TD\> $REDIMG $RED $STATE  $EF  \</TD\> \<TD\> $WLOGLINK Last Result $LINKTAG \</TD\> \</TR\>      >> $DASHBRD


			if [[ ! -e $CHECKFILE ]];then
				touch $CHECKFILE 
				mail_alert $STATE "$SRV" && echo "  mail_alert $STATE"
			else
				echo                                                    >>  $WLOG
				echo "Alert already alert sent for $SRV  - waiting"| tee -a $WLOG
			fi


			#Check #2 - Port Check
			echo                  >> $WLOG
			echo "Port Check:"    >> $WLOG
			echo "==========="    >> $WLOG

			$CONNECT $SRV $PORT $TIMEOUT  > /dev/null 2>&1 
			if (( $? != 0 ));then 

				TC="$REDIMG"
				echo "I cannot connect to port $PORT on $SRV" >> $WLOG
			else 
				TC="$GREENIMG"
				echo "I can connect to port $PORT on $SRV OK" >> $WLOG
			fi 

			#Check #3 - Ping Check
			echo                  >> $WLOG
			echo "Ping Check:"    >> $WLOG
			echo "==========="    >> $WLOG

			ping -c 4 $SRV >> $WLOG  2>&1
			if (( $? != 0 )); then

				 PC="$REDIMG"
				 echo "$SRV Does NOT respond to ping"	>> $WLOG
				 echo ""				>> $WLOG

			else

				 PC="$GREENIMG"
			         echo ""		>> $WLOG
				 echo "$SRV: ping OK" 	>> $WLOG
			fi


		fi

	else
			STATE="up" 
			COLOR="$GREEN"
			NC="$GREENIMG"

			echo "  $SVC on $SRV is $STATE" 
			echo  \<TR\>\<TD\>\<A HREF\="$SHOW"\>$SRV\<\/A\> \</TD\>                                                   >> $DASHBRD
			echo  \<TD\> $GREENIMG  $GREEN $STATE $EF\</TD\> \<TD\> $WLOGLINK Last Result $LINKTAG \</TD\> \</TR\>    >> $DASHBRD

				if  [[  -e $CHECKFILE ]];then
				    rm $CHECKFILE | tee  -a $WLOG
				    echo        "  $SRV is back $STATE"  
				    echo              >> $WLOG
				    mail_alert $STATE  "$SRV" &&  echo "  mail_alert $STATE"
				fi
	fi

	report "$STATE" "$COLOR" "$PC" "$NC" "$TC"
done
echo '</TABLE></BODY></HTML>'                                                                                                     >> $DASHBRD
clean_up
