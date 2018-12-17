#!/usr/bin/perl -w
#
# Title  :   smtp.pl 
# Author :   John_Ouellette@yahoo.com
# Files  :   smtp.pl 
# Pupose :   Send email through SMTP server
#
#
# Submit as 

use Net::SMTP;

my $timeout = $ARGV[1] || "5";
my $host    = $ARGV[0];


if (my $smtp = Net::SMTP->new($host, Timeout => "$timeout", Debug   => 1,) ) {

 $smtp->banner() or die "$1";

} else {

 print "Failed to complete SMTP handshake.\n";
 exit 1;

}

