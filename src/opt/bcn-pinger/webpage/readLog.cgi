#!/usr/bin/perl -T
use strict;
use Date::Parse;
use Date::Format;
use CGI qw/param/;

print "Content-Type: text/html\n\n";
print "<html><body>\n";

my $BASE = "/opt/bcn-pinger/";
my $TZ_num = "+0530"; my $TZ_name = "IST";



my $log = "";
my $ip = "";
my $_log = param("log");
if ($_log =~ /([0-9.]+)/) {
	$ip = $1;
	$log = "$BASE/log/$1.log";
}
if (! -f $log) {
	print "Select a log<br>\n\n";
	opendir(DIR,"$BASE/log/");
	while (readdir(DIR)) {
		next unless /([0-9.]+).log$/;
		print "<a href='readLog.cgi?skip=1&log=$1'>$1</a><br>";
	}
	closedir(DIR);
	print "\n</body></html>\n";
	exit 0;
}

open(CONF, "<$BASE/etc/config");
while (<CONF>) {
	if (/^$ip,([^,]*),(.*)/) {
		$TZ_num = $1;
		$TZ_name = $2;
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
	print "(Only showing minutes with losses, <a href='readLog.cgi?log=$ip'>Show all lines</a>)<br>";
	$skipGood = 1;
} else {
	print "(<a href='readLog.cgi?log=$ip&skip=1'>Only show lines when there were losses</a>)<br>";
}
if ($hours == 99999) {
	print "(<a href='readLog.cgi?log=$ip&hours=24'>Only show lines from the last 24 hours</a>)<br>";
} else {
	print "(Only showing lines from the last $hours hours. <a href='readLog.cgi?log=$ip'>Show all lines</a>)<br>";
}
print "<pre>";
my $line = "";
my $lostSome = 0;
open(LOG, "<$log");
my $now = time();
while (<LOG>) {
	chomp;
	if (/(.*2017)$/) { 
		my $local = $1;
		my $time = str2time($local);
		my $GMT = time2str("%T %Z", $time, "GMT");
		my $IST = time2str("%T %Z", $time, "$TZ_num"); 
		$IST =~ s/\Q$TZ_num/$TZ_name/;
		if ($time + (3600*$hours) > $now) { 
			if ($skipGood == 0 || $lostSome == 1) {
				print $line;
			}
		}
		$line = "\n$local ($GMT, $IST) onwards: "; 
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
print "\n</body></html>\n";
