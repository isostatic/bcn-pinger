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
	print "Select a log\n\n";
	opendir(DIR,"$BASE/log/");
	while (readdir(DIR)) {
		next unless /([0-9.]+).log$/;
		print "<a href='readLog.cgi?log=$1'>$1</a><br>";
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

print "<pre>";
open(LOG, "<$log");
while (<LOG>) {
	chomp;
 # Thu 29 Jun 14:07:47 BST 2017
	if (/(.*2017)$/) { 
		my $local = $1;
		my $time = str2time($local);
		my $GMT = time2str("%T %Z", $time, "GMT");
		my $IST = time2str("%T %Z", $time, "$TZ_num"); 
		$IST =~ s/\Q$TZ_num/$TZ_name/;
		print "\n$local ($GMT, $IST) onwards: "; 
	}
	if (/([0-9]+) packets transmitted, ([0-9]+) received, /) { print "received $2/$1: "; }
	if (/rtt min.avg.max.mdev = ([^ ]*) ms/) { 
		my $mamd = $1;
		my ($min, $avg, $max, $dev) = split(/\//, $mamd);
		my $PATH="PATH unknown "; 
		if ($min < 160) { $PATH = "PATH 1"; }
		elsif ($min > 210 && $min < 250) { $PATH = "PATH 2"; }
		elsif ($min > 400  && $min < 500) { $PATH = "PATH 3"; }
		print "$PATH rtt (min,avg,max,dev) $1"; 
	}
}
close(LOG);
print "\n</body></html>\n";
