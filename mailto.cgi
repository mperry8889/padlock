#!/usr/bin/perl

my($mail) = $ENV{QUERY_STRING};

if ($mail eq "webmaster") {
   print "Location: mailto:mperry\@slone.bu.edu\n\n";
}
print "Location: mailto:$mail\@slone.bu.edu\n\n";

