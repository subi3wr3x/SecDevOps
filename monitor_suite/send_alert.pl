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

my $sender  = 'root';
my $timeout = "5";

my $rcpt    = $ARGV[3] || 'root';

my $body    = "$ARGV[2]" ;
my $subject = "$ARGV[1]";
my $host    = "$ARGV[0]";

$smtp = Net::SMTP->new($host,
                           Timeout => "$timeout", 
                           Debug   => 1,
                          );


$smtp->mail("$sender");
$smtp->to("$rcpt");
$smtp->data();
$smtp->datasend("To: $rcpt\n") ; 
$smtp->datasend("From: $sender\n") ; 
$smtp->datasend("Subject: $subject\n") ; 
$smtp->datasend("$body");
$smtp->dataend();
$smtp->quit;
