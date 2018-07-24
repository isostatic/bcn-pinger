#!/usr/bin/perl 
use strict;
use Socket;
use Date::Parse;
use Date::Format;
use CGI qw/param/;

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
<script src='jquery.js'></script> 
<script src='readLog.js'></script> 
</head>
<body>\n";

$ENV{PATH} = "";
my $BASE = "/opt/bcn-pinger/";
my $TZ_num = "+0530"; my $TZ_name = "IST";
my $comment = "";
my $comments = {};




my $log = "";
my $ip = "";
my $_log = param("log");
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
	print "Select a log<br>\n\n";
	opendir(DIR,"$BASE/log/");
	my @out;
	while (readdir(DIR)) {
		next unless /([a-z0-9.]+).log$/;
		my $ip = $1;
		my $c = $comments->{$ip};
		my $hostname = gethostbyaddr(inet_aton($ip), AF_INET);
#		push (@out, "<a href='readLog.cgi?skip=1&log=$ip'>$ip</a> ($hostname) $c<br>");
		push (@out, "<tr><td><a href='readLog.cgi?skip=1&hours=240&log=$ip'>$ip</a></td><td>$hostname</td><td>$c</td></tr>");
	}
	closedir(DIR);
	print "<table border>";
	foreach (sort(@out)) { print; };
	print "</table>";
	print "\n</body></html>\n";
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
	print "Not showing bad lines: (<a href='readLog.cgi?log=$ip&hours=24'>Show all lines from the last 24 hours</a> <a href='readLog.cgi?log=$ip&hours=240'>Show all lines from the last 10 days</a> <a href='readLog.cgi?log=$ip'>Show all lines</a>)<br>";
	$skipGood = 1;
} else {
	print "(<a href='readLog.cgi?log=$ip&skip=1'>Only show lines when there were losses</a>)<br>";
}
if ($hours == 99999) {
	print "(<a href='readLog.cgi?log=$ip&hours=24'>Only show lines from the last 24 hours</a> <a href='readLog.cgi?log=$ip&hours=240'>Only show lines from the last 10 days</a>)<br>";
} else {
	print "(Only showing lines from the last $hours hours. ";
	print "<a href='readLog.cgi?log=$ip&skip=1&hours=24'>Show bad lines from the last 24 hours</a> <a href='readLog.cgi?log=$ip&skip=1&hours=240'>Show bad lines from the last 10 days</a> <a href='readLog.cgi?log=$ip'>Show all bad lines</a>)<br>";
}
print "$comment<br>";
print "<div class='loading'>....loading....</div>";
print "<pre>";
my $line = "";
my $lostSome = 0;
my $lines = 1000 + ($hours * 4000);

my $maxage = (24+$hours) * 3600;


#print "Tail $lines of $log in last $hours hours\n";

my @toRead = ();

opendir(LOGDIR, "$BASE/log");
while (readdir LOGDIR) {
	my $full = "$BASE/log/$_";
	next unless ($full =~ /$log/);
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
push(@toRead, $log);

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
		if (/(.*201[789])$/) { 
			my $local = $1;
			my $time = str2time($local);
			$baseTime = $time;
			my $gmstring = time2str("%Y-%m-%d %T %Z", $time, "GMT");
			my $GMT = time2str("%T %Z", $time, "GMT");
			my $IST = time2str("%T %Z", $time, "$TZ_num"); 
			$IST =~ s/\Q$TZ_num/$TZ_name/;
			if ($time + (3600*$hours) > $now) { 
				if ($skipGood == 0 || $lostSome == 1) {
					my $printline = $line;
					unless ($printline =~ /received 60.60/) {
						if ($skipGood == 0) {
							$printline =~ s/(received ..?\/..:)/<b style='color: red;'>$1<\/b>/;
						}
					}
					print $printline;
					print " <a href='#' class='expand'>+</a><div class='detail'>$detail</div>";
					print " <a href='#' class='traceroute' ip='$ip' date='$gmstring'>rte</a><div class='trace'>&nbsp;</div>";
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
		print $line;
	}
}
print "\n</body></html>\n";
