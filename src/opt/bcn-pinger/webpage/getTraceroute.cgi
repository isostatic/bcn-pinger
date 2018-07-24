#!/usr/bin/perl 
use strict;
use Date::Parse;
use Date::Format;
use CGI qw/param/;
print "Content-Type: text/plain\n\n";
# http://delhi.bcnportal.co.uk/pinger/getTraceroute.cgi?log=8.8.8.8&date=Tue%2024%20Jul%2017:56:49%20BST%202018

my $BASE = "/opt/bcn-pinger/";
my $_date = param("date");
my $time = str2time($_date);


my $log = "";
my $_log = param("log");
if ($_log =~ /([a-z0-9.]+)/) {
	my $ip = $1;
	my $day = time2str("%Y-%m-%d", $time, "GMT");
	$log = "$BASE/log/$ip.$day.trace";
}


if (! -e "$log") {
	$log = "$log.bz2";
	if (! -e "$log") {
		print "Can't find traceroute logs for $_date\n";
		exit;
	}
}

my $cat = "/bin/cat";
if ($log =~ /bz2$/) { $cat = "/bin/bzcat"; }
open(LOG, "$cat $log |");
my $previousOutput = "";
my $output = "";
while (<LOG>) {
	my $origLine = $_;
	if ($origLine =~ /2.* Traceroute to .* start/) {
		$previousOutput = $output;
		$output = "";
	}
	if ($origLine =~ /[\(\s](\d+\.\d+\.\d+\.\d+)[\)\s]/) {
		my $ip = $1;
		s/\d+\.\d+\.\d+\.\d+/<b>$ip<\/b>/g;
	}
	s/ (\d\d:\d\d:\d\d) GMT/ <b>$1<\/b> GMT/;
	$output .= $_;
	if ($origLine =~ /(2.*) Traceroute to .* end/) {
		my $logTime = str2time($1);

		my $dateTime = time2str("%Y-%m-%d %T %Z", $logTime, "GMT");
		my $checkTime = time2str("%Y-%m-%d %T %Z", $time, "GMT");
#		print "Check $1 == $dateTime later than $checkTime\n";
		if ($logTime > $time) {
			last;
		}
	}
}
close(LOG);
print $previousOutput;
print "\n";
print $output;
