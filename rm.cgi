#!/usr/bin/perl -w
# ######### FIXME: no taint mode because of File::Path::rmtree() ############
#
# Padlock
# Secure File Upload System
#
#
# rm.cgi
# Delete files or directories.
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
# files= or dirs= parameters -- make an array of files or dirs
my(@rm);
if ($q->param('files') || $q->param('dirs')) {

   for ($q->param('files'), $q->param('dirs')) {
      for (split(/\,/, $_)) {
         $p->check($_);        # don't push the untainted, full dir
         next if ($_ eq '/');

         push(@rm, $_);
      }
   }

}


###############################################################################
# files/dirs confirmed -- delete
if (@rm && $q->param('confirm') && ($q->param('confirm') eq 'y')) {

   print $q->redirect('/cgi-bin/main.cgi');
 
   for (@rm) {
      $p->rm($_);
   }
  
   # write to log
   for (@rm) {
      $p->log($p->collapse($p->home.'/'.$_)." deleted");
   }
   
   # send an e-mail
   if ($p->cread('flags') =~ /e/) {
      use Net::SMTP;
      my($e) = new Net::SMTP($p->cread('MAILSERVER'));
      
      $e->mail($p->cread('MAILFROM'));
      $e->to($p->email);
      $e->data();
      $e->datasend('From: '.$p->cread('MAILFROM')."\n");
      $e->datasend('To: '.$p->email."\n");
      $e->datasend('Subject: SEC File Transfer System: Delete - '.scalar(localtime)."\n\n");

      $e->datasend('Username:  '.$p->cread('user')."\n");
      $e->datasend('Timestamp: '.scalar(localtime)."\n");
      $e->datasend("\n");

      $e->datasend("The following files/directories were deleted from the Slone Epidemiology Center secure file transfer system:\n\n");
      for (@rm) {
         $e->datasend("- ".$_."\n");
      }
      $e->datasend("\n");

      $e->datasend("\n\n");
      $e->datasend('_' x 80);
      $e->datasend("\n");
      $e->datasend(qq|This is an automatically generated e-mail.  Please do not reply.  If you have any questions, comments, or concerns please visit the contact page at <https://padlock.bu.edu/about/contact.html>.|);
      $e->dataend();
      $e->quit;

   }
   
   exit(0);
   
}


###############################################################################
# list files/dirs for confirmation
if (@rm && !$q->param('confirm')) {

   #-----------[ HTML OUTPUT ]-------------------------------------------------
   print $q->header(-type => 'text/html', -expires => 'now');
   $p->html_header();
   print q|
<font face="verdana" size=4>
   Confirm Delete
</font>
<hr noshade size=1 width="100%">
<font face="verdana" size="-1">
Okay to remove the following files/directories? |; for (@rm) { if (-d $p->collapse($p->home.'/'.$_)) { print qq|Please note that the contents of the directories below will be deleted as well.|; last } } print q|
<br><br>
<table width="100%" align="left" cellspacing=3 cellpadding=0>
|;

   for (@rm) {
      print q|
   <tr>
      <td width=30>&nbsp;</td>
      <td align="left">
         <font face="verdana" size="-1"><li>|,
            $_, q|</li>
         </font>
      </td>
   </tr>
|;
   }
   print q|
</table></table>

<center>
<font face="verdana" size="-1">
   <a href="/cgi-bin/rm.cgi?confirm=y|; 
   for ($q->param) { print "&$_=".$q->param($_); } 
   print q|">Yes</a> - <a href="/cgi-bin/main.cgi">No</a><br>
</font>
</center>
|;

   $p->html_footer();   
   #-----------[ HTML OUTPUT ]-------------------------------------------------

   exit(0);

}


# default action: assume current directory

# don't delete root directory
if ($p->fullpath('.') eq '/') { 
   print $q->redirect('/cgi-bin/main.cgi');
}

print $q->redirect('/cgi-bin/rm.cgi?dirs='.$p->fullpath('.'));


# EOF: rm.cgi
