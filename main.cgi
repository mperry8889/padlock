#!/usr/bin/perl -wT
#
# Padlock
# Secure File Upload System
#
#
# main.cgi
# Lists files in a user's directory.  Allows directory traversal and file 
# management.  Initially hides file managing features through different 
# viewing methods -- "viewer" and "manager".
#
# Matt Perry <mperry@slone.bu.edu>
# 07/09/04
#

use strict;
use CGI;
use Padlock;

my($q, $p);
$q = new CGI;

# if cookie expired, send back to main
if (!$q->cookie('Padlock')) {
#   print $q->redirect('/index_bottom.html');
#   exit(0);
print $q->header;print"didnt take cookie";
}

# else fire up a new session
$p = new Padlock(session => $q->cookie('Padlock'));


###############################################################################
# file:: parameters -- make an array of files for operation
my(@files);
for ($q->param) {
   if ($_ =~ m/^file::(.+)$/) {
      push(@files, $1);
   }
}

###############################################################################
# f parameter - send file
if ($q->param('f')) {

   my($qstr) = 'files='.$q->param('f');
   print $q->redirect('/cgi-bin/download.cgi?'.$qstr);
   exit(0);
   
}

###############################################################################
# d paramater - change directory
if ($q->param('d')) {
   $p->cd($q->param('d'));
}

###############################################################################
# filemanager :: delete - delete selected files
if ($q->param('action') && ($q->param('action') eq 'delete') && @files && 
   ($p->cread('mode') eq 'manager')) {

   my($qstr) = querystring(@files);
   print $q->redirect('/cgi-bin/rm.cgi'.$qstr);
   exit(0);
   
}


###############################################################################
# filemanager :: copy - copy selected files
if ($q->param('action') && ($q->param('action') eq 'copy') && @files && 
   ($p->cread('mode') eq 'manager')) {

   my($qstr) = querystring(@files);
   print $q->redirect('/cgi-bin/cp.cgi'.$qstr);
   exit(0);
   
}


###############################################################################
# filemanager :: rename - rename selected files
if ($q->param('action') && ($q->param('action') eq 'rename') && @files && 
   ($p->cread('mode') eq 'manager')) {

   my($qstr) = querystring(@files);
   print $q->redirect('/cgi-bin/mv.cgi'.$qstr);
   exit(0);
   
}


###############################################################################
# filemanager :: download - download selected files 
if ($q->param('action') && ($q->param('action') eq 'download') && @files) {

   my($qstr) = querystring(@files);
   print $q->redirect('/cgi-bin/download.cgi'.$qstr);
   exit(0);
   
}


###############################################################################
# m parameter - change view mode
if ($q->param('m')) {
   $p->cset(mode => $q->param('m'));
   $p->cdump();
}


###############################################################################
# default action: display current directory

# generate list
my(@d, @ls, @list);

# if old sorting method is the same as the new one, then reverse the sort
if ($p->cread('lastsort') && $q->param('sort') &&
      ($p->cread('lastsort') eq $q->param('sort'))) {
   @ls = reverse($p->ls($p->cwd, sort => $q->param('sort') || 'name'));
   
   # get directories back on top
   for (reverse(@ls)) {
      if (!-d $_) {
        last; 
      }
      unshift(@ls, pop(@ls));
   }
   
   $p->cset(lastsort => 'reversed');
   $p->cdump();
}
else {
   @ls = $p->ls($p->cwd, sort => $q->param('sort') || 'name');
   
   $p->cset(lastsort => $q->param('sort') || 'name');
   $p->cdump();
}

# generate the HTML listing
push(@list, '<tr><td width=15 align="right" bgcolor="#f7f7f7"><a href="/cgi-bin/main.cgi?d="'.$p->fullpath('..').'"><img src="/images/parent.gif" border=0></td><td width="60%" align="left" bgcolor="#f7f7f7"><font face="verdana" size=-1><a href="/cgi-bin/main.cgi?d='.$p->fullpath('..').'">Parent Directory</a></font></td><td width="20%" align="left" bgcolor="#f7f7f7"><font face="verdana" size="-1"></font></td><td width="20%" align="left" bgcolor="#f7f7f7"><font face="verdana" size="-1"></font></td></tr>');

my($i) = 0;
for (@ls) {
   next if m/^[.]{1,2}$/;
   my($bgcolor) = ($i++ % 2 == 0 ? '#ffffff' : '#f7f7f7');
   if ($p->cread('mode') eq 'manager') {
      if (-d $_) {
         push(@list, '<tr><td align="right" bgcolor="'.$bgcolor.'"><a href="/cgi-bin/main.cgi?d='.$p->fullpath($_).'"><img src="/images/folder.gif" border=0></a></td><td width="60%" align="left" bgcolor="'.$bgcolor.'"><font face="verdana" size=-1><a href="/cgi-bin/main.cgi?d='.$p->fullpath($_).'">'.$_.'</a></font></td><td width="20%" align="left" bgcolor="'.$bgcolor.'"><font face="verdana" size="-1"></font></td><td width="20%" align="left" bgcolor="'.$bgcolor.'"><font face="verdana" size="-1"></font></td></tr>');
      }
      else {
         push(@list, '<tr><td align="right" bgcolor="'.$bgcolor.'"><input type="checkbox" name="file::'.$p->fullpath($_).'"></td><td width="60%" align="left" bgcolor="'.$bgcolor.'"><font face="verdana" size=-1><a href="/cgi-bin/main.cgi?f='.$p->fullpath($_).'">'.$_.'</a></font></td><td width="20%" align="left" bgcolor="'.$bgcolor.'"><font face="verdana" size="-1">'.$p->filemod($p->fullpath($_)).'</font></td><td width="20%" align="left" bgcolor="'.$bgcolor.'"><font face="verdana" size="-1">'.$p->filesize($p->fullpath($_)).'</font></td></tr>');
      }
   }
   else {
      if (-d $_) {
         push(@list, '<tr><td align="right" bgcolor="'.$bgcolor.'"><a href="/cgi-bin/main.cgi?d='.$p->fullpath($_).'"><img src="/images/folder.gif" border=0></a></td><td width="60%" align="left" bgcolor="'.$bgcolor.'"><font face="verdana" size=-1><a href="/cgi-bin/main.cgi?d='.$p->fullpath($_).'">'.$_.'</a></font></td><td width="20%" align="left" bgcolor="'.$bgcolor.'"><font face="verdana" size="-1"></font></td><td width="20%" align="left" bgcolor="'.$bgcolor.'"><font face="verdana" size="-1"></font></td></tr>');
      }
      else {
         push(@list, '<tr><td align="right" bgcolor="'.$bgcolor.'"><a href="/cgi-bin/main.cgi?f='.$p->fullpath($_).'"><img src="/images/file.gif" border=0></a></td><td width="60%" align="left" bgcolor="'.$bgcolor.'"><font face="verdana" size=-1><a href="/cgi-bin/main.cgi?f='.$p->fullpath($_).'">'.$_.'</a></font></td><td width="20%" align="left" bgcolor="'.$bgcolor.'"><font face="verdana" size="-1">'.$p->filemod($p->fullpath($_)).'</font></td><td width="20%" align="left" bgcolor="'.$bgcolor.'"><font face="verdana" size="-1">'.$p->filesize($p->fullpath($_)).'</font></td></tr>');
      }
   }
}
#---------------[ HTML OUTPUT ]-------------------------------------------------
print $q->header(-type => 'text/html', -expires => 'now');

$p->html_header();

if ($p->cread('mode') eq 'manager') {
   print q|
<form action="/cgi-bin/main.cgi" method="POST" class="style_small_submit">
<table width="100%">
   <tr>
      <td align="left" valign="bottom">
         <font face="verdana" size=4>
            Index of |, $p->cwd, q|
         </font>
      </td>
      <td align="right" valign="bottom">
         <font face="verdana" size="-1">Selected files:</font>&nbsp;
         <select name="action" class="style_small_submit">
         <option value="download">Download</option>
         <option value="rename">Rename</option>
         <option value="copy">Copy</option>
         <option value="delete">Delete</option>
         </select><input type="submit" value="X" class="style_small_submit">
      </td>
   </tr>
</table>
|;
}
else {
   print q|
<font face="verdana" size=4>
   Index of |, $p->cwd, q|
</font><br>|;
}

print q|
<hr noshade size=1 width="100%">
<table width="100%" cellspacing=0 cellpadding=3>
   <tr>
      <td>
         <img src="/images/transparent.gif">
      </td>
      <td width="60%" align="left">
         <font face="verdana" size=-1>
            <b><a href="/cgi-bin/main.cgi?sort=name">Filename</a></b>
         </font>
      </td>
      <td width="20%" align="left">
         <font face="verdana" size=-1>
            <b><a href="/cgi-bin/main.cgi?sort=modified">Last Modified</a></b>
         </font>
      </td>
      <td width="20%" align="left">
         <font face="verdana" size=-1>
            <b><a href="/cgi-bin/main.cgi?sort=size">File Size</a></b>
         </font>
      </td>
   </tr>
</table>
<hr noshade size=1 width="100%">
<table width="100%" cellspacing=0 cellpadding=3>
|;

for (@list) {
   print "$_\n";
}

print q|</table>|;

if ($p->cread('mode') eq 'manager') {
   print q|
</form>
<hr noshade size=1 width="100%">
<center>
   <font face="verdana" size="-1">
      <a href="/cgi-bin/mkdir.cgi">New Directory</a> - <a href="/cgi-bin/cp.cgi">Copy Directory</a> - <a href="/cgi-bin/mv.cgi">Rename Directory</a> - <a href="/cgi-bin/rm.cgi">Delete Directory</a>
   </font>
</center>
|;
}

$p->html_footer();
#---------------[ HTML OUTPUT ]-------------------------------------------------


# create a query string from an array of file values
sub querystring {
   my(@keys) = @_;
    
   return('?files='.join(',', @keys));
}

# EOF: main.cgi
