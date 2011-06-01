#!/usr/bin/perl -T
#
# Padlock
# Secure File Upload System
#
#
# login.cgi
# Authenticates a user for secure file upload.
# Transitional CGI from user/password login to sesssion logins
#
# Matt Perry <mperry@slone.bu.edu>
# 07/01/2004
#

use strict;
use Padlock;
use CGI;

my($p, $q);

$q = new CGI;
$p = new Padlock(user     => $q->param('username'),
                 password => $q->param('password'),
                );

print $q->redirect('/cgi-bin/main.cgi');
                     
# EOF: login.cgi                     
