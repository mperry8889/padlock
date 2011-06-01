#!/usr/bin/perl -wT
#
# Padlock
# Secure File Upload System
#
#
# upload.cgi
# Accepts a file from the user.
#
# Matt Perry <mperry@slone.bu.edu>
# 07/13/04
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
# fileXX parameters -- make an array of files for upload
my(@files);
for ($q->param) {
   if ($_ =~ m/^file([\d]{2})/) {
      push(@files, $q->param($_));
   }
}

###############################################################################
# files array -- upload files
if (@files) { 
   
   my(@completed, @error, @overwrite, @log);
   my($owi); # overwrite index
   
   for ($q->param) {

      next unless m/^file([\d]{2})/;
      next unless $q->param($_);

      my($file, $filepath, $filename);
      
      $file = $q->upload($_);
      $filename = $q->param($_);
      $filename =~ s/^.*(\\|\/)(.+)/$2/;
      $filepath = $p->realpath($filename);
      
      # if file exists, add it to list to overwrite
      if (-e $filepath) {
         
         $owi = 0;
         while (-e "$filepath.$owi" || -d _) {
            $owi++;
         }
         
         push(@overwrite, "$filename -> $filename.$owi");
         push(@log, "$filename exists!  Moved to $filename.$owi");
         $p->mv($p->fullpath($filename), $p->fullpath("$filename.$owi"));
     }
      
      # $file contains a filehandle, $filename is the name of the file
      # so print the contents of the filehandle into the filename...      
      if ($file) {
         open(UPLOAD, ">$filepath") || $p->error("Can't open file ($filepath): $!");
         while (<$file>) {
            print UPLOAD $_;
         }
         close(UPLOAD);
         push(@log, "$filepath uploaded successfully");
         push(@completed, $filename);
      }
      else {
         push(@error, $filename);
         push(@log, "$filepath upload FAILED!");
      }

      
   }

   # nothing to overwrite -- looks ok
   if (@overwrite || @error) {
      # prompt for overwrite
   
      #-----------[ HTML OUTPUT ]-----------------------------------------------
      print $q->header(-type => 'text/html', -expires => 'now');
      $p->html_header();
   
      print q|
<font face="verdana" size=4>
   Upload Warning
</font>
<hr noshade size=1 width="100%">
|;

      if (@overwrite) {
         my($l);

         print q|
<font face="verdana" size="-1">
Some files previously existed.  The old files were moved out of the way to make room for the new.
<br><br>
<table width="100%" align="left" cellspacing=3 cellpadding=0>
|;

         for (@overwrite) {
            $l = $_;
            $l =~ s|->|<code>-></code>|;
            print q|
<tr>
   <td width=30>&nbsp;</td>
   <td align="left">
      <font face="verdana" size="-1"><li>|,
         $l, q|
      </font>
   </td>
</tr>
|;
         }

      print q|
</table>
<br><br>
You may rename or delete these files using "file manager" mode.
<br><br>
|;

      }

      if (@error) {

         print q|
<font face="verdana" size="-1">
Some files failed to upload.<br><br>
<table width="100%" align="left" cellspacing=3 cellpadding=0>
|;

         for (@error) {
            print q|
<tr>
   <td width=30>&nbsp;</td>
   <td align="left">
      <font face="verdana" size="-1"><li>|,
         $_, q|
      </font>
   </td>
</tr>
|;
         }

      print q|
</table>
<br><br>
Try re-uploading these files.  If the problem persists, please read the <a href="/cgi-bin/help.cgi">help file</a>.
<br><br>
|;

      }

      print q|
<center>
   <a href="/cgi-bin/main.cgi">Back to File Manager</a>
</center>
|;
      
      $p->html_footer();
      #-----------[ HTML OUTPUT ]-----------------------------------------------
   }
   
   # write to log
   for (@log) {
      $p->log($_);
   }
   
   # send e-mail
   if ($p->cread('flags') =~ /e/) {
      use Net::SMTP;
      my($e) = new Net::SMTP($p->cread('MAILSERVER'));

      $e->mail($p->cread('MAILFROM'));
      $e->to($p->email);
      $e->data();
      $e->datasend('From: '.$p->cread('MAILFROM')."\n");
      $e->datasend('To: '.$p->email."\n");
      $e->datasend('Subject: SEC File Transfer System: Upload - '.scalar(localtime)."\n\n");

      $e->datasend('Username:  '.$p->cread('user')."\n");
      $e->datasend('Timestamp: '.scalar(localtime)."\n");
      $e->datasend("\n");
      
      if (@completed) {
         $e->datasend("The following files were successfully transferred to Slone Epidemiology Center's secure upload system:\n\n");
         for (@completed) {
            $e->datasend("- ".$p->fullpath($_)."\n");
         }
         $e->datasend("\n");
      }
      if (@overwrite) {
         $e->datasend("The following existing files were renamed to accomidate new uploads:\n\n");
         for (@overwrite) {
            $e->datasend("- ".$_."\n");
         }
         $e->datasend("\n");
      }
      if (@error) {
         $e->datasend("The following files failed to upload:\n");
         for (@error) {
            $e->datasend("- ".$p->fullpath($_)."\n");
         }
         $e->datasend("\n");
      }
         
      $e->datasend("\n\n");
      $e->datasend('_' x 80);
      $e->datasend("\n");
      $e->datasend(qq|This is an automatically generated e-mail.  Please do not reply.  If you have any questions, comments, or concerns please visit the contact page at <https://padlock.bu.edu/about/contact.html>.|);
      $e->dataend();
      $e->quit;
   }
   
   if (!@overwrite && !@error) { print $q->redirect('/cgi-bin/main.cgi'); }
   exit(0); 

}


# default action: allow user to select files to upload

# number of files to be uploaded
my($n) = ($q->param('n') && ((abs($q->param('n')) > 0) && (abs($q->param('n')) < 100)) ?
         abs($q->param('n')) : 1);

#---------------[ HTML OUTPUT ]-------------------------------------------------
print $q->header(-type => 'text/html', -expires => 'now');

$p->html_header();

print q|
<table width="100%">
   <tr>
      <td align="left" valign="bottom">
         <font face="verdana" size=4>
            Upload Files
         </font>
      </td>
      <form action="/cgi-bin/upload.cgi" method="POST" class="style_small_submit" border=0>
      <td align="right" valign="bottom">
        <font face="verdana" size=1>
            Number of files: <input type="text" size=2 maxlength=2 name="n" class="style_small_submit"><input type="submit" value="X" class="style_small_submit">
         </font>
      </td>
      </form>
   </tr>
</table>
<hr noshade size=1 width="100%">
<font face="verdana" size="-1">
<center>
   Select file|.(($n == 1) ? '' : 's').q| to upload
</center>
<form action="/cgi-bin/upload.cgi" method="POST" enctype="multipart/form-data" class="style_small_submit">
<table align="center" width="100%" cellspacing=0 cellpadding=3>
|;

for (1 .. $n) {
   my($bgcolor) = (($_ % 2 == 0) ? '#ffffff' : '#f7f7f7'); 
   print q|
   <tr>
      <td align="center" bgcolor="|.$bgcolor.q|">
         <input type="file" name="file|.sprintf("%02d", $_).q|" class="style_med_submit" size=60>
      </td>
   </tr>
|;
}

print q|
</table>
<center>
   <input type="submit" value="Upload" class="style_small_submit"><br><br><br>
   <font size=1><i>Note: please don't click your browser's "stop" or "back" buttons during the transfer!</font>
</center>
</form>
|;

$p->html_footer();
#---------------[ HTML OUTPUT ]-------------------------------------------------

# EOF: upload.cgi
