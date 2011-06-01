#!/usr/bin/perl -w
# ### FIXME: no -T because of Directory::Copy ###
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
# files= or dirs= parameters -- make an array of files or dirs
my(@cp);
if ($q->param('files') || $q->param('dirs')) {

   for ($q->param('files'), $q->param('dirs')) {
      for (split(/\,/, $_)) {
         $p->check($_);        # don't push the untainted, full dir
         next if ($_ eq '/');

         push(@cp, $_);
      }
   }

}
# file:: and dir:: parameters -- make a hash of files or dirs
my(%cp);
for ($q->param) {
   if ($_ =~ m/cp::/) {
      s/cp::(.+)/$1/;
      $cp{$1} = $q->param("cp::$1");
   }
}

###############################################################################
# %cp hash -- move files/dirs
if (%cp) {
   
   my(@overwrite);
   
   for (keys(%cp)) {
      if ($p->cwd eq $_) {
         $p->cset(cwd => $cp{$_});
         $p->cdump();
      }

      # if file exists, do a soft-overwrite
      my($owi);
      if (-e $p->realpath($cp{$_}) || -d _) {
   
         $owi = 0;
         while (-e $p->realpath($cp{$_}).".$owi" || -d _) {
            $owi++;
         }
         $p->mv($cp{$_}, "$cp{$_}.$owi");
         push(@overwrite, "$cp{$_} -> $cp{$_}.$owi");
         $p->cp($_, $cp{$_});
         $p->log("$cp{$_} exists!  Moving to $cp{$_}.$owi");
      
      }
      else {
         $p->cp($_, $cp{$_});
      }
      $p->log($p->realpath($_).' moved to '.$p->realpath($cp{$_}));
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

if (!@cp) { push(@cp, $p->fullpath('.')); }
for (@cp) { if ($_ eq '/') { print $q->redirect('/cgi-bin/main.cgi'); } }

   #-----------[ HTML OUTPUT ]-------------------------------------------------
   print $q->header(-type => 'text/html', -expires => 'now');
   $p->html_header();
   print q|
<font face="verdana" size=4>
   Rename Files/Directories
</font>
<hr noshade size=1 width="100%">
<form action="/cgi-bin/cp.cgi" method="POST">
|;
for (@cp) {
   print q||;
}
print q|
<font face="verdana" size="-1">
Please enter new names for the following files/directories:
<br><br>
<table width="100%" align="center" cellspacing=3 cellpadding=0>
|;

   for (@cp) {
      print q|
   <tr>
      <td align="right">
         <font face="verdana" size="-1">|, 
         $_, q|
         </font>
      </td>
      <td width=20><code>-></code></td>
      <td align="left"><input type="text" name="cp::|,$_,q|" size=50 class="style_small_submit" value="|,$_,q|"></td>
   </tr>
|;
   }
   print q|
</table>
<br>
<center>
<font face="verdana" size="-1">
   <input type="submit" value="Copy" class="style_small_submit"><input type="reset" value=" Clear " class="style_small_submit">
</font>
</center>
</form>
|;

   $p->html_footer();   
   #-----------[ HTML OUTPUT ]-------------------------------------------------


# EOF: cp.cgi
