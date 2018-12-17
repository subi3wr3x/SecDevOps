#!/usr/bin/perl -w

use Net::Telnet;

my $host    = $ARGV[0];
my $port    = $ARGV[1];
my $timeout = $ARGV[2];

if (my $telnet = Net::Telnet->new(Host=>"$host", Timeout=>"$timeout",Port=>"$port") ) {

print "I can connect to  $host on port $port  OK\n";

} else {

print "I cannot connect to  $host on port $port  OK\n";

}

