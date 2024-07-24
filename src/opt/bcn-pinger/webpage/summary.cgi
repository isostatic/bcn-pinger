#!/bin/bash
cd /opt/bcn-pinger/log


H=24

if [[ $QUERY_STRING =~ hours=([0-9]+) ]]; then
H=${BASH_REMATCH[1]}
fi

D=`date +%s`

if [[ $QUERY_STRING =~ csv=1 ]]; then
echo "Content-Type: application/csv"
echo "Content-Disposition: attachment; filename=summary-`hostname`-${H}hours-$D.csv"
else
echo "Content-Type: text/plain"
fi
echo ""


unset QUERY_STRING
unset REQUEST_URI
unset REQUEST_SCHEME
unset REQUEST_METHOD
unset REMOTE_ADDR
unset REMOTE_PORT

echo "# Report at `date +%F_%T` for last $H hours on `hostname`"
../webpage/readLog.cgi summ=2
for I in *log; do ../webpage/readLog.cgi summ=1 log=$I hours=$H; done
