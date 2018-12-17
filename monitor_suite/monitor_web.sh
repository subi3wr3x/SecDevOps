#!/bin/bash
#
# Title      :   Monitor_web.sh
# Author     :   john@monitorsuite.net
# Purpose    :   Check HTTP servers
#                and save a history
#
# Submit as
#
#         #Monitor_web.sh
#         0,5,10,15,20,25,30,35,40,45,50,55 * * * * /usr/local/admin/bin/monitor_web.sh
#
#         in crontab to monitor every 5 minutes
#
######################################################################
# Start Script - Do not touch below this line !!!
######################################################################
SRV_CONF_FILE="/etc/monitorsuite/monitor_suite.conf"
source $SRV_CONF_FILE
WEB_CONF_FILE="$WEBROOT/webmon/conf/monitor_web.conf"
source $WEB_CONF_FILE
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

[[ -e $COMMAND       ]]    || { echo COMMAND: $COMMAND              does not exist ; exit 1; }
[[ -e $SRV_CONF_FILE ]]    || { echo SRV_CONF_FILE: $SRV_CONF_FILE  does not exist ; exit 1; }
[[ -e $WEB_CONF_FILE ]]    || { echo WEB_CONF_FILE: $WEB_CONF_FILE  does not exist ; exit 1; }
[[ -e $CONNECT       ]]    || { echo CONNECT: $CONNECT              does not exist ; exit 1; }
[[ -e $SMTPALERT     ]]    || { echo SMTPALERT: $SMTPALERT          does not exist ; exit 1; }
[[ -e $URLSFILE      ]]    || { echo URLSFILE: $URLSFILE            does not exist ; exit 1; }
[[ -z $DASHBRD       ]]    && { echo DASHBRD must have a value.                ; exit 1; }
[[ -z $WEBROOT       ]]    && { echo WEBROOT must have a value.                ; exit 1; }

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

cat > $STATUSPAGE <<EOF
<HTML>
<HEAD><TITLE> $SVC Service Status for $URL: $STATE </TITLE></HEAD>
<BODY>
<H3>$SVC Service Status for $URL: $COLOR $STATE $EF </H3>
<P>
<TABLE CELLPADDING=3 CELLSPACING=0 BORDER=1>
<TR><TH colspan=3> Checks </TH></TR>
<TR><TH> $SVC </TH><TH>Ping </TH><TH>Port $PORT</TH></TR>
<TR><TD> $NC </TD> <TD> $PC </TD><TD> $TC </TD></TR>
</BODY>
</HTML>
EOF

}



mail_alert () {

STATE="$1"
SUBJECT="$SVC Service for $URL is $STATE on $DAYNAME at $HOUR:$MIN"
BODY="

$(date)

Please review this log for full details:
$EMLINK

"
#Send to secondary SMTP servers if first fails
$SMTPALERT "$SMTP1" "$SUBJECT" "$BODY" "$RECIPIENT" "$CC" 2> $MLOG  || \
$SMTPALERT "$SMTP2" "$SUBJECT" "$BODY" "$RECIPIENT" "$CC" 2> $MLOG  || \
$SMTPALERT "$SMTP3" "$SUBJECT" "$BODY" "$RECIPIENT" "$CC" 2> $MLOG

}

create_plog () {

cat >  $PLOG <<EOF
<TR><TD><A HREF="$SHOW">$URL</A></TD>
<TD>$NC $COLOR  $STATE  $EF </TD><TD> $WLOGLINK Last Result $LINKTAG </TD></TR>
EOF

}

add_url2_dshbrd () {

cat >> $DASHBRD << EOF
	<?php

	if(!file_exists("$PLOG"))
	 {
	 echo ("<TR><TD>Checking <A HREF=$URL>$URL</A></TD> <TD>Please</TD> <TD>Wait...</TD></TR>");
	 }
	else
	 {
	include("$PLOG");
	 }
	?>
EOF

}

clean_up () {

	rm -f $I_AM_RUNNING_FILE
	exit $1

}

get_port () {

#Get True Port if URL is like http://host:5678
if  echo $URL| cut -d "/" -f3- | grep : > /dev/null 2>&1 ;then
  PORT=$(echo $URL | cut -d "/" -f3 | cut -d ":" -f2)
fi

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

SVC="HTTP"

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
NUM_OF_SERVERS=$(wc -l $URLSFILE |  cut -b 1-2)
cd $WEBROOT/$SCRPTHOME || exit 1

DATE=$(date)

cat > $DASHBRD <<EOF
<HTML>
<HEAD><TITLE>Monitor_Web (Monitoring $NUM_OF_SERVERS $SVC Services) </TITLE>
<META http-equiv="refresh" content="15"></HEAD>
<BODY>
<P>
$DATE
- <A HREF="http://$WEBSRV/$SCRPTHOME/history">History</A>
<P>
<TABLE CELLPADDING=3 CELLSPACING=0 BORDER=1>
<TR><TH>URL</TH><TH>Status</TH><TH>Log</TH></TR>
EOF


##############################
# F. Main foreach loop for SVC
##############################

if [ $DEBUG == "1" ];then
  WGETOPTS="-d -S"
fi

if [ $CHECKCERT  == "0" ];then
  WGETOPTS="$WGETOPTS --no-check-certificate"
fi


for URL in  $(cat $URLSFILE)

do

	ENV=$(echo $URL| cut -d "/" -f3- | sed s#/#_#g | sed s#?#_#g | sed s#=#_#g | sed s#:#_#g)
	PLOG="$WEBROOT/$SCRPTHOME/pagelogs/$ENV.$YEAR.$MNTH.$HOUR.$MIN.$SECS.php"
	add_url2_dshbrd 

(
	mkdir -p $WEBROOT/$SCRPTHOME/history/$YEAR/$MNTH/$DAY/$ENV
	CHECKFILE="$WEBROOT/$SCRPTHOME/checkfiles/down.$ENV"
	PAGELOG="$WEBROOT/$SCRPTHOME/pagelogs/$YEAR.$MNTH.$ENV.$HOUR.$MIN.$SECS.LOG"
	SHOW="http://$WEBSRV/$SCRPTHOME/status/$ENV.html"
	STATUSPAGE="$WEBROOT/$SCRPTHOME/status/$ENV.html"
	MLOG="history/$YEAR/$MNTH/$DAY/$ENV/smtp.$ENV.$HOUR.$MIN.$SECS.LOG"
	WLOG="history/$YEAR/$MNTH/$DAY/$ENV/$ENV.$HOUR.$MIN.$SECS.LOG"
	WLOGLINK="<A HREF="http://$WEBSRV/$SCRPTHOME/$WLOG">"
	EMLINK="http://$WEBSRV/$SCRPTHOME/$WLOG"
	PHYSHOST=$(echo $URL| cut -d "/" -f3 | cut -d ":" -f1)
	PORT="80"

	CMDLINE="$COMMAND $WGETOPTS -T $TIMEOUT -t $RETRIES $URL -O $PAGELOG" 
	date                                                         >  $WLOG

	#Don't switch order...
	echo                                                        >>  $WLOG
	echo
	echo Starting to check "$SVC" Service for $URL
	echo

	TC="NA"  
	PC="NA"   
	NC="NA"   

	#Check #1 - Main Service  Check
	echo                  >> $WLOG
	echo "$SVC Check:"    >> $WLOG
	echo "=========="     >> $WLOG
	echo "$CMDLINE"       >> $WLOG
	echo ""               >> $WLOG



	echo "  Checking $URL 1st attempt"
	$CMDLINE >>  $WLOG 2>&1 
	if (( $? != 0 ));then 

		echo "  Checking $URL 2nd attempt"

		$CMDLINE  > /dev/null 2>&1 
		if (( $? != 0 ));then 

			STATE="down"
			COLOR="$RED"
			NC="$REDIMG"

			echo "  $SVC on $URL is $STATE" 
			echo                                                                                           >> $WLOG
			echo "$SVC Check ran twice without success."                                                   >> $WLOG


			if [[ ! -e $CHECKFILE ]];then
				mail_alert $STATE "$URL" && echo "  mail_alert $STATE for $URL" | tee -a $WLOG
				echo 1 >  $CHECKFILE 
			else
				NUM_PAGES_SENT=$(cat $CHECKFILE)
				if [[ $NUM_PAGES_SENT -lt $NUM_PAGES_MAX ]];then 
					mail_alert $STATE "$URL" && echo "  mail_alert $STATE Page # $((NUM_PAGES_SENT += 1)) for $URL" | tee -a $WLOG
					echo $NUM_PAGES_SENT > $CHECKFILE
				else
					echo                                                        >>  $WLOG
					echo "   Max Alerts ($NUM_PAGES_MAX) already sent for $URL  - waiting" | tee -a $WLOG
				fi
			fi

			create_plog
			get_port

			#Check #2 - Port Check
			echo                  >> $WLOG
			echo "Port Check:"    >> $WLOG
			echo "==========="    >> $WLOG


			$CONNECT $PHYSHOST $PORT $TIMEOUT  2>&1  > /dev/null
			if (( $? != 0 ));then 

				TC="$REDIMG"
				echo "I cannot connect to port $PORT on $PHYSHOST" >> $WLOG
			else 
				TC="$GREENIMG"
				echo "I can connect to port $PORT on $PHYSHOST OK" >> $WLOG
			fi 


			#Check #3 - Ping Check
			echo                  >> $WLOG
			echo "Ping Check:"    >> $WLOG
			echo "==========="    >> $WLOG

			ping -c 4 $PHYSHOST >> $WLOG  2>&1
			if (( $? != 0 )); then

				 PC="$REDIMG"
				 echo "$PHYSHOST Does NOT respond to ping" >> $WLOG
				 echo ""                                   >> $WLOG

			else

				 PC="$GREENIMG"
				 echo ""                                   >> $WLOG
				 echo "$PHYSHOST: ping OK"                 >> $WLOG
			fi
		fi       

	else 

		STATE="up"
		COLOR="$GREEN"
		NC="$GREENIMG"

		echo "  $SVC on $URL is $STATE" 


		if  [[  -e $CHECKFILE ]];then
		    rm $CHECKFILE | tee  -a $WLOG
		    echo        "  $URL is back $STATE"  
		    echo              >> $WLOG
		    mail_alert $STATE  "$URL" &&  echo "  mail_alert $STATE" | tee -a $WLOG
		fi

                create_plog


	fi

	report
)&
done
wait

echo '</TABLE></BODY></HTML>'                                                                                             >> $DASHBRD
clean_up 
