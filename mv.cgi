#!/usr/bin/perl -wT
#
# Padlock
# Secure File Upload System
#
#
# mv.cgi
# Rename files or directories.
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
my(@mv);
if ($q->param('files') || $q->param('dirs')) {

   for ($q->param('files'), $q->param('dirs')) {
      for (split(/\,/, $_)) {
         $p->check($_);        # don't push the untainted, full dir
         next if ($_ eq '/');

         push(@mv, $_);
      }
   }

}
# file:: and dir:: parameters -- make a hash of files or dirs
my(%mv);
for ($q->param) {
   if ($_ =~ m/mv::/) {
      s/mv::(.+)/$1/;
      $mv{$1} = $q->param("mv::$1");
   }
}

###############################################################################
# %mv hash -- move files/dirs
if (%mv) {
   
   my(@overwrite);
   
   for (keys(%mv)) {
      if ($p->cwd eq $_) {
         $p->cset(cwd => $mv{$_});
         $p->cdump();
      }

      # if file exists, do a soft-overwrite
      my($owi);
      if (-e $p->realpath($mv{$_}) || -d _) {
   
         $owi = 0;
         while (-e $p->realpath($mv{$_}).".$owi" || -d _) {
            $owi++;
         }
         $p->mv($mv{$_}, "$mv{$_}.$owi");
         push(@overwrite, "$mv{$_} -> $mv{$_}.$owi");
         $p->mv($_, $mv{$_});
         $p->log("$mv{$_} exists!  Moving to $mv{$_}.$owi");
      
      }
      else {
         $p->mv($_, $mv{$_});
      }
      $p->log($p->realpath($_).' moved to '.$p->realpath($mv{$_}));
   }

   if (@overwrite) {

      my($l);

      #-----------[ HTML OUTPUT ]-------------------------------------------------
      print $q->header(-type => 'text/html', -expires => 'now');
      $p->html_header();
      print q|
<font face="verdana" size=4>
   Files/Directories Exist
</font>
<hr noshade size=1 width="100%">
<font face="verdana" size="-1">
Some files previously existed.  The old files were moved out of the way to make room for the new.
<br><br>
<table width="100%" align="center" cellspacing=3 cellpadding=0>
|;

   for (@overwrite) {
      $l = $_;
      $l =~ s|->|<code>-></code>|;
      
      print q|
   <tr>
      <td width=30>&nbsp;</td>
      <td align="left">
         <font face="verdana" size="-1">|, 
         $_, q|
         </font>
      </td>
   </tr>
|;
   }
   print q|
</table>
<br>
<center>
<font face="verdana" size="-1">
   <a href="/cgi-bin/main.cgi">Back to File Manager</a>
</font>
</center>
|;

   $p->html_footer();   
   #-----------[ HTML OUTPUT ]-------------------------------------------------
     
   }
   else {
      print $q->redirect('/cgi-bin/main.cgi');
   }
   
   exit(0);

}


###############################################################################
# list files/dirs to get new targets

if (!@mv) { push(@mv, $p->fullpath('.')); }
for (@mv) { if ($_ eq '/') { print $q->redirect('/cgi-bin/main.cgi'); } }

   #-----------[ HTML OUTPUT ]-------------------------------------------------
   print $q->header(-type => 'text/html', -expires => 'now');
   $p->html_header();
   print q|
<font face="verdana" size=4>
   Rename Files/Directories
</font>
<hr noshade size=1 width="100%">
<form action="/cgi-bin/mv.cgi" method="POST">
|;
for (@mv) {
   print q||;
}
print q|
<font face="verdana" size="-1">
Please enter new names for the following files/directories:
<br><br>
<table width="100%" align="center" cellspacing=3 cellpadding=0>
|;

   for (@mv) {
      print q|
   <tr>
      <td align="right">
         <font face="verdana" size="-1">|, 
         $_, q|
         </font>
      </td>
      <td width=20><code>-></code></td>
      <td align="left"><input type="text" name="mv::|,$_,q|" size=50 class="style_small_submit" value="|,$_,q|"></td>
   </tr>
|;
   }
   print q|
</table>
<br>
<center>
<font face="verdana" size="-1">
   <input type="submit" value="Rename" class="style_small_submit"><input type="reset" value=" Clear " class="style_small_submit">
</font>
</center>
</form>
|;

   $p->html_footer();   
   #-----------[ HTML OUTPUT ]-------------------------------------------------


# EOF: mv.cgi
