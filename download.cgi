#!/usr/bin/perl -wT
#
# Padlock
# Secure File Upload System
#
#
# download.cgi
# Sends a file to the user.
#
# Matt Perry <mperry@slone.bu.edu>
# 07/14/04
#

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
# files parameter - send file
if ($q->param('files')) {

   my(@files) = split (/\,/, $q->param('files'));

   ### FIXME: single file breaks browsers like Konqueror ### 
   
   # single file - just send
   if ($#files == 0) {
      $p->filesend($files[0]);
   }
   # multi files - zip and send
   else {
      
#      require Padlock::File;
#      delete($ENV{PATH});
#      my($list);
      
#      map { $list .= $p->check($p->realpath($_)) . ' '; } @files;

#      system('/usr/bin/zip -u -j -q -9 '.
#         $p->check($p->cread('TMPDIR').'/'.$p->cread('session').'.zip').' '.
#         $list);
 
#      # unchecked call to send() because the file is outside the user's space
#      Padlock::File->send($p->check($p->cread('TMPDIR').'/'.
#         $p->cread('session').'.zip'));
      
#   }

      require Padlock::File;
      
      delete($ENV{PATH});
      my($list);
      my($download);

      $download = Padlock::File->check($p->cread('WWWROOT').'/'.
         $p->cread('DOWNLOAD').'/'.$p->cread('session').'.zip');
      map { $list .= Padlock::File->check($p->realpath($_)). ' '; } @files;

      system('/usr/bin/zip -u -j -q -9 '.$download.' '.$list);
      print $q->redirect($p->cread('DOWNLOAD').'/'.$p->cread('session').'.zip');
         
   }

   exit(0);
   
}

# default action: redirect to main, to display current directory

print $q->param('/cgi-bin/main.cgi');



# EOF: download.cgi
