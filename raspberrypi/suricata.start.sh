#!/bin/sh

PID_FILE="/var/run/suricata/suricata.pid"
[[ -e $PID_FILE ]] && rm $PID_FILE
/opt/suricata/bin/suricata -c /opt/suricata/etc/suricata/suricata.yaml -D -i eth0 not host listener.logz.io or host api.dataplicity.com
