#!/usr/bin/perl -wT
#
# Padlock
# Secure File Upload System
#
#
# cp.cgi
# Copy files or directories.
#
# Matt Perry <mperry@slone.bu.edu>
# 07/12/04
#

use strict;
use CGI;
use Padlock;

my($q, $p);
$q = new CGI;

# if cookie expired, send back to main
if (!$q->cookie('Padlock')) {
   print $q->redirect('/index_bottom.html');
   exit(0);
}

# else fire up a new session
$p = new Padlock(session => $q->cookie('Padlock'));


###############################################################################
# dir parameter -- make directories
if ($q->param('dir')) {
   $p->check($p->fullpath($q->param('dir')));
   $p->mkdir($p->fullpath($q->param('dir')));
   $p->log($p->realpath($q->param('dir')).' created');

   print $q->redirect('/cgi-bin/main.cgi');
}

# default action: ask what dir the user wants to make

#-----------[ HTML OUTPUT]-------------------------------------------------
print $q->header(-type => 'text/html', -expires => 'now');
$p->html_header();

print q|
<font face="verdana" size=4>
   Make Directory
</font>
<hr noshade size=1 width="100%">
<form action="/cgi-bin/mkdir.cgi" method="POST">
<font face="verdana" size="-1">
Please enter the name of the directory you want to create:
<br><br>
<center>
   <input type="text" name="dir" size=80 class="style_small_submit"><br>
   <input type="submit" value="Create" class="style_small_submit">
</center>
</font>
</form>
|;

$p->html_footer();
#-----------[ HTML OUTPUT]-------------------------------------------------

# EOF: mkdir.cgi
