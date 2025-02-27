#!/usr/bin/python3
import os
import re

print("Content-Type: text/plain\n\n")

expectedLogs = os.popen("cat /opt/bcn-pinger/etc/config|grep -v \\#|grep ,|cut -d , -f 1|sort|uniq|wc -l").read().strip()
numRecentLogs = os.popen("/usr/bin/find /opt/bcn-pinger/log/ -name \"*.log\" -mmin -10 | wc -l").read().strip()
df = os.popen("df --output=avail /opt/bcn-pinger/log/ | tail -n 1").read().strip()
df = int(df)

status="OK"
if (int(numRecentLogs) < int(expectedLogs)):
    status="WARNING"
if (df < 100000):
    # 100M space free
    status="WARNING"
if (numRecentLogs == 0):
    status="CRITICAL"
if (df < 1000):
    # 1M space free
    status="WARNING"

print(f"expectedLogs={expectedLogs}")
print(f"numRecentLogs={numRecentLogs}")
print(f"df={df}")
print(f"status={status}")

if (status != "OK"):
    os.popen("cat /opt/bcn-pinger/etc/config|grep -v \\#|grep ,|cut -d , -f 1|sort|uniq > /tmp/pinger.health.expected").read()
    os.popen("/usr/bin/find /opt/bcn-pinger/log/ -name \"*.log\" -mmin -10|sed -e 's/.log$//' -e 's/.*log.//'|sort|uniq > /tmp/pinger.health.found").read()
    diff = os.popen("diff -y /tmp/pinger.health.expected /tmp/pinger.health.found").read().strip()
    print("================================================================================")
    print("* expected *                                                    * found *")
    print(diff)
    print("================================================================================")
    for line in diff.splitlines():
        if ("<" in line):
            _ip = line.split()[0]
            match = re.search(r"([0-9.]+)", _ip)
            if match:
                ip = match.group(1)
                print(f"sudo -u nobody /opt/bcn-pinger/bin/bcn-pinger {ip} &");
                print("disown %1")
