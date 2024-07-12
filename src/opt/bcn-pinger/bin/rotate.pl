#!/usr/bin/perl
use strict;
my $old = "/opt/bcn-pinger/log";

while (<>) {
    chomp;
    my $f = $_;
    if (/\/20..\//) {
        # already moved
        next;
    }
    if (/.*log.(20..)-(..)-(..).bz2/ || /.*(20..)-(..)-(..).trace/) {
        my $target = "$old/$1/$2/$3";
        
        if (! -d $target) {
            print("Make $target\n");
            `mkdir -p $target`;
            if (! -d $target) {
                die("Can't make directory $target");
            }
        }
        while (-f "$target/$f") {
            print("$f exists in $target");
            $f = "$f.$$";
        }
        print("Move '$f' to '$target'\n");
        `mv $f $target`;
    }
}
