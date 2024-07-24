#!/usr/bin/perl 
use strict;
use Socket;
use Date::Parse;
use Date::Format;
use CGI qw/param/;
my $summCSV = 0;
my $_summ = param("summ");
if ($_summ == 2) { $summCSV = 2; }
if ($_summ == 1) { $summCSV = 1; }


if ($summCSV == 2) {
    print "IP, Hostname, Comment, From, To, Took (seconds), packets received, packets sent, received%, lost%, one-in-X lost\n";
    exit;
}

if ($summCSV == 0) {
print "Content-Type: text/html\n\n";
print "<html>
<head>
<style>
.expand {
    text-decoration: none;
	display: none;
}
.trace {
	display: none;
	padding-left: 20px;
	border: thin blue solid;
}
.detail {
	display: none;
}
.missing {
	color: red;
}
</style>
<link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.0/css/theme.default.min.css'>
<script type='text/javascript' src='https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js'></script>
<script type='text/javascript' src='https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.0/js/jquery.tablesorter.min.js'></script>
<script type='text/javascript' src='https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.0/js/jquery.tablesorter.widgets.min.js'></script>
<script src='readLog.js'></script> 
</head>
<body>\n";
}

$ENV{PATH} = "";
my $BASE = "/opt/bcn-pinger/";
my $TZ_num = "+0530"; my $TZ_name = "IST";
my $comment = "";
my $comments = {};


my $firstTime = 0;
my $lastTime = 0;


my $log = "";
my $ip = "";
my $filter = "";
my $_filter = param("filter");
if ($_filter =~ /([a-z0-9.-:]+)/) {
	$filter = $1;
}
my $_log = param("log");
$_log =~ s/\.log$//;
if ($_log =~ /([a-z0-9.]+)/) {
	$ip = $1;
	$log = "$BASE/log/$ip.log";
}
open(CONF, "<$BASE/etc/config");
while (<CONF>) {
	chomp;
	my @a = split(/,/);
	$comments->{@a[0]} = @a[3];
}
if (! -f $log) {
	if ($summCSV == 0) { print "Select a log<br>\n\n"; }
	opendir(DIR,"$BASE/log/");
	my @out;
	while (readdir(DIR)) {
		next unless /([a-z0-9.]+).log$/;
		my $ip = $1;
		my $c = $comments->{$ip};
		my $hostname = gethostbyaddr(inet_aton($ip), AF_INET);
#		push (@out, "<a href='readLog.cgi?skip=1&log=$ip'>$ip</a> ($hostname) $c<br>");
		push (@out, "<tr><td><a href='readLog.cgi?skip=1&hours=240&log=$ip'>$ip</a> <a href='readLog.cgi?hours=24&log=$ip'>(today)</a></td><td>$hostname</td><td>$c</td></tr>");
	}
	closedir(DIR);
	
        if ($summCSV == 0) {
        	print "<table id='list'>";
        	my $ip_filter = "";
        	if ($filter =~ /ip:(.*)/) { $ip_filter = $1; }
        	print "<thead><th data-value='$ip_filter'>IP</th><th>Host</th><th> </th></thead>";
        	print "<tbody>";
        	foreach (sort(@out)) { print; };
        	print "</tbody></table>";
        	print "\n</body></html>\n";
        }
        exit 0;
}

open(CONF, "<$BASE/etc/config");
while (<CONF>) {
	chomp;
	if (/^$ip,([^,]*),([^,]*),*(.*)/) {
		$TZ_num = $1;
		$TZ_name = $2;
		if ($3 ne "") { $comment = $3; }
		last;
	}
}
close(CONF);

my $hours = 99999;
if (param("hours") =~ /([0-9]+)/) {
	$hours = $1;
}

my $skipGood = 0;
if (param("skip")) {
	$skipGood = 1;
}
my $requireddate = "";
if (param("date") =~ /(\d{4}-\d{2}-\d{2})/) {
	$requireddate = $1;
	my $rqTime = str2time("$requireddate", "GMT");
	my $secsInPast = time()-$rqTime;
	if ($secsInPast < (26*3600)) {
		if ($summCSV == 0)  { print "For current logs see <a href='readLog.cgi?log=$ip&hours=24&skip=$skipGood'>Last 24 hours</a><br>"; }
	} else {
		my $rqDateNice = time2str("%A %o %B %Y", $rqTime, "GMT");
		$hours = 99999;
		if ($skipGood) {
			if ($summCSV == 0) { print "Showing only outages on <b>$rqDateNice</b>. <a href='readLog.cgi?log=$ip&date=$requireddate&skip=0'>Show all lines for $requireddate</a><br>"; }
		} else {
			if ($summCSV == 0) { print "Showing all lines on <b>$rqDateNice</b>. <a href='readLog.cgi?log=$ip&date=$requireddate&skip=1'>Show only outages for $requireddate</a><br>"; }
		}
		my @dates = qw/-28 -7 -1 0 1 7 28/;
		foreach (@dates) {
			my $targetTime = $rqTime+(($_+0.5)*86400);
			if ($targetTime > time()) { 
				next;
			}
			my $d = time2str("%Y-%m-%d", $targetTime, "GMT");
			my $niced = time2str("%e-%b", $targetTime, "GMT");
			if ($_ == 0) { 
				if ($summCSV == 0) { print "<b>$niced</b> "; }
			} else {
				if ($summCSV == 0) { print "<a href='readLog.cgi?log=$ip&date=$d&skip=$skipGood'>$niced</a> "; }
			}
		}
		if ($summCSV == 0) { print "<br>"; }
	}
} else {
	if ($skipGood) {
		if ($summCSV == 0) { print "Not showing bad lines: (<a href='readLog.cgi?log=$ip&hours=24'>Show all lines from the last 24 hours</a> <a href='readLog.cgi?log=$ip&hours=240'>Show all lines from the last 10 days</a> <a href='readLog.cgi?log=$ip'>Show all lines</a>)<br>"; }
	} else {
		if ($summCSV == 0) { print "(<a href='readLog.cgi?log=$ip&skip=1'>Only show lines when there were losses</a>)<br>"; }
	}
}
if ($hours == 99999) {
	if ($summCSV == 0) { print "(<a href='readLog.cgi?log=$ip&hours=24'>Only show lines from the last 24 hours</a> <a href='readLog.cgi?log=$ip&hours=240'>Only show lines from the last 10 days</a>)<br>"; }
} else {
	if ($summCSV == 0) { 
            print "(Only showing lines from the last $hours hours. ";
	    print "<a href='readLog.cgi?log=$ip&skip=1&hours=24'>Show bad lines from the last 24 hours</a> <a href='readLog.cgi?log=$ip&skip=1&hours=240'>Show bad lines from the last 10 days</a> <a href='readLog.cgi?log=$ip'>Show all bad lines</a>)<br>";
	    my $d = time2str("%Y-%m-%d", time()-86400, "GMT");
	    print "<a href='readLog.cgi?log=$ip&skip=$skipGood&date=$d'>Show lines from yesterday ($d)</a><br>";
        }
}
if ($summCSV == 0) { 
    print "$comment<br>";
    print "<div class='loading'>....loading....</div>";
    print "<pre>";
}
my $line = "";
my $lostSome = 0;
my $lines = 1000 + ($hours * 4000);

my $maxage = (24+$hours) * 3600;


#print "Tail $lines of $log in last $hours hours\n";

my @toRead = ();

my @logdates = ();
opendir(LOGDIR, "$BASE/log");
while (readdir LOGDIR) {
	my $file = $_;
	my $full = "$BASE/log/$file";
	next unless ($full =~ /$log/);
	my $fdate = $file; $fdate =~ s/.bz2//; $fdate =~ s/.*log.//;
	push(@logdates, $fdate) unless ($fdate =~ /log/);
	if ($requireddate =~ /.../) {
		next unless ($full =~ /$requireddate/);
	}
	my @stats = stat($full);
	my $age = time - @stats[9];
	if ($maxage > $age) {
		if ($full =~ /.bz2$/) {
			push(@toRead, $full);
		}
	}
}
closedir(LOGDIR);
@toRead = sort(@toRead);
if ($requireddate !~ /../) {
	push(@toRead, $log);
}
if ($#toRead < 0 && $requireddate =~ /../) {
	@logdates = sort(@logdates);
	my $first = @logdates[0];
	if ($summCSV == 0) { print "No logs found from $requireddate - earliest is <a href='readLog.cgi?log=$ip&date=$first&skip=$skipGood'>$first</a>"; }
}

my $totalSent = 0;
my $totalReceived = 0;

foreach my $toR (@toRead) {
	my $cat = "/bin/cat";
	if ($toR =~ /bz2$/) { $cat = "/bin/bzcat"; }
#	print "READ $cat $toR\n";
	open(LOG, "$cat $toR | /usr/bin/tail -n$lines |");
	my $now = time();
	my $line = "";
	my $detail = "";
	my $lastSeq = 0;
	my $baseTime = 0;
	while (<LOG>) {
		chomp;
		if (/(.*20[12][0123456789])$/) { 
			my $local = $1;
			my $time = str2time($local);
			$baseTime = $time;
			my $gmstring = time2str("%Y-%m-%d %T %Z", $time, "GMT");
			my $GMT = time2str("%T %Z", $time, "GMT");
			my $IST = time2str("%T %Z", $time, "$TZ_num"); 
			$IST =~ s/\Q$TZ_num/$TZ_name/;
			if ($time + (3600*$hours) > $now) { 
                            if ($firstTime < 0) { 
                                $firstTime++;
                            } elsif ($firstTime < 1000000) {
                                $firstTime = $baseTime;
                            }
				if ($skipGood == 0 || $lostSome == 1) {
					my $printline = $line;
                                        if ($printline =~ /received ([0-9]*)\/([0-9]*):/) {
                                            $totalReceived += $1;
                                            $totalSent += $2;
                                        }
					unless ($printline =~ /received 60.60/) {
						if ($skipGood == 0) {
							$printline =~ s/(received ..?\/..:)/<b style='color: red;'>$1<\/b>/;
						}
					}
                                        if ($summCSV == 0) {
					    print $printline;
					    print " <a href='#' class='expand'>+</a><div class='detail'>$detail</div>";
					    print " <a href='#' class='traceroute' ip='$ip' date='$gmstring'>rte</a><div class='trace'>&nbsp;</div>";
                                        }
				}
			}
			$lastSeq = 0;
			$detail = "\t$local\n";
			$line = "\n$local ($GMT, $IST) onwards: "; 
		} else {
			my $date = "";
			if ($_ =~ /icmp_seq=([0-9]*) /) {
				unless ($lastSeq + 1 == $1) {
					my $numMiss = $1 - $lastSeq - 1;
					$detail .= "<span class='missing'>\t\t(missing $numMiss packets)</span>\n";
				}
				$lastSeq = $1;
#				my $GMT = time2str("%T %Z", $baseTime + $lastSeq, "GMT"); ## this takes too long to run on server
				my $thisTime = $baseTime + $lastSeq;
				$date = " (<span class='toDate'>$thisTime</span>)";
			} elsif ($_ =~ /ping statistics /) {
				my $numMiss = 60 - $lastSeq; 
				if ($numMiss > 0) { 
					$detail .= "<span class='missing'>\t\t(missing $numMiss packets)</span>\n\n"; 
				}
			}
			$detail .= "\t$_$date\n";
		}
		if (/([0-9]+) packets transmitted, ([0-9]+) received, /) { 
			$lostSome = 0;
			if ($1 != $2) { $lostSome = 1; }
			$line .= "received $2/$1: "; 
		}
		if (/rtt min.avg.max.mdev = ([^ ]*) ms/) { 
			my $mamd = $1;
			my ($min, $avg, $max, $dev) = split(/\//, $mamd);
			my $PATH="PATH unknown "; 
			# hard coded values FIXME
			if ($min < 160) { $PATH = "PATH 1"; }
			elsif ($min > 210 && $min < 250) { $PATH = "PATH 2"; }
			elsif ($min > 400  && $min < 500) { $PATH = "PATH 3"; }
			if ($ip !~ /172.26./) { $PATH = ""; }
			$line .= "$PATH rtt (min,avg,max,dev) $mamd"; 
		}
	}
	close(LOG);
	if ($skipGood == 0 || $lostSome == 1) {
		if ($summCSV == 0) {
                    print $line;
                }
	}
        $lastTime = $baseTime;
}

my $precision = 100;
my $totalLost = $totalSent - $totalReceived;

my $oneIn = "n/a";
if ($totalLost > 0) { $oneIn = int($totalSent/$totalLost); }

if ($totalSent == 0) { $totalSent = 1; }
my $totalThrough = int($precision*100*$totalReceived/$totalSent)/$precision;
my $totalLostPC = int($precision*100*(1-$totalReceived/$totalSent))/$precision;


if ($summCSV == 1) {
    #print("(Skipped outputting lines, this is the day's summary)\n");
    my $fromString = time2str("%Y-%m-%d %T %Z", $firstTime, "GMT");
    my $toString = time2str("%Y-%m-%d %T %Z", $lastTime, "GMT");
    my $timeTook = $lastTime - $firstTime;
    my $c = $comments->{$ip};
    my $hostname = gethostbyaddr(inet_aton($ip), AF_INET);
    print "$ip, $hostname, $c, $fromString, $toString, $timeTook, $totalReceived, $totalSent. $totalThrough%, $totalLostPC%, $oneIn\n"; 
} else {
    print "<br><br>Total packets: $totalReceived/$totalSent. $totalThrough% got through, $totalLostPC% loss (1 in $oneIn).\n";
    print "\n</body></html>\n";
}
