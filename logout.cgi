#!/usr/bin/perl -T
#
# Padlock
# Secure File Upload System
#
#
# logout.cgi
# Logs out a user by expiring their cookie, and therefore ending their session. 
#
# Matt Perry <mperry@slone.bu.edu>
# 07/09/2004
#

use strict;
use Padlock;
use CGI;

my($p, $q);

$q = new CGI;
$p = new Padlock(session => $q->cookie('Padlock'));
$p->logout();
print $q->redirect('/index_bottom.html');
                     
# EOF: login.cgi                     
