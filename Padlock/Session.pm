#
# Padlock::Session.pm
#
# Session control module
#
 
use strict;
package Padlock::Session;

# auth - authenticate a user
sub auth {

   my($self, %param) = @_;

   # username/password login
   if ($param{user} && $param{password}) {

      my($line);

      # read global config
      open(PASSWD_FILE, Padlock->cread('USERFILE')) ||
         Padlock->error("Can't open passwd file: $!");
      while (<PASSWD_FILE>) {
         chomp;
         if ($_ =~ m/^$param{user}\|(.+)$/i) {
            $line = $_;
            last;
         }
      }
      close(PASSWD_FILE);

      # check username, password
      if (!$line) { Padlock->error("User $param{user} not found"); }
      my($user, $pass, $flags, $home, $email) = split(/\|/, $line);

      if (crypt($param{password}, $pass) ne $pass) {
         Padlock->error('Incorrect password');
      }

      # good login -- set up environment, generate session
      Padlock->cset(user => $user, flags => $flags, home => $home,
                    email => $email, cwd => '/', expire => time + 600,
                    root => '/', session => $self->session(),
                    mode => 'viewer',);
      Padlock->cset(ip => Padlock->getip()) if 
         (Padlock->cread('INTERFACE') eq 'WEB');
      Padlock->cset(string => Padlock::Session->string()) if 
         (Padlock->cread('INTERFACE') eq 'WEB');

      $self->set_cookie() if (Padlock->cread('INTERFACE') eq 'WEB');

      # write to log
      Padlock->log("\n");
      Padlock->log('User '.Padlock->cread('user').' logged in');
      Padlock->log('IP: '.Padlock->cread('ip')) if 
         (Padlock->cread('INTERFACE') eq 'WEB');

   }
   # session login
   elsif ($param{session}) {

      my($session, $string) = split(/::/, $param{session});
      
      Padlock->error("Can't do session-login without web interface")
         unless (Padlock->cread('INTERFACE') eq 'WEB');

      if (!$string) {
         Padlock->error("Error authenticating session");
      }
      if (!$session) {
         Padlock->error("No session specified.  Can't log in");
      }

      # restore session's environment
      Padlock->cimport($session);

      # make sure user is valid
      if (Padlock->getip() ne Padlock->cread('ip')) {
         Padlock->log("\n");
         Padlock->log('*** UNAUTHORIZED ACCESS ***');
         Padlock->log('ERROR FROM IP '.Padlock->getip());
         Padlock->log('*** MISMATCHED IP ADDRESSES ***');
         Padlock->error("Session error: unauthorized access");
      }
      #if ($string ne Padlock->cread('string')) {
      #   Padlock->log("\n");
      #   Padlock->log('*** UNAUTHORIZED ACCESS ***');
      #   Padlock->log('ERROR FROM IP '.Padlock->getip());
      #   Padlock->log('*** MISMATCHED STRINGS ***');
      #   Padlock->error("Session error: unauthorized access");
      #}

      # re-cookie
      Padlock->cset(expire => time + 600, string => $self->string());
      $self->set_cookie();

   }
   # else error
   else {
      Padlock->log("\n");
      Padlock->log('Failed login attempt by '.$param{user});
      Padlock->log('IP: '.Padlock->getip()) if
         (Padlock->cread('INTERFACE') eq 'WEB');
      Padlock->error('No login information given');
   }

   # dump config to disk
   Padlock->cset(VALID => Padlock->cread('VALID').':'.Padlock->home);
   Padlock->cdump();
   Padlock->cd(Padlock->cwd);

   return(1);

}

sub logout {

   my($self) = @_;
   my($session);

   #$session = Padlock->cread('session');
   $self->set_cookie('+1s');
   Padlock->log('User '.Padlock->cread('user').' logged out');
   return(1);
   
}

# session - generate new session ID
sub session {

   require Padlock::File;
   
   my($self) = @_;
   my($session);

   for (1 .. 20) {
      $session .= sprintf("%x", rand(15));
   }

   # if session already exists, recurse and generate a new one
   if (-e Padlock::File->check(Padlock->cread('SESSIONS').'/'.$session)) {
      $session = $self->session();
   }

   return($session);

}

# string - generate a random garbage string
sub string {

   my($self) = @_;
   my($string);
   
   # 50 chars of random crap of chrs() from 65-122
   for (1 .. 50) {
      $string .= chr(65 + rand(57));
   }

   return($string);
   
}

# set_cookie - generate and write cookie to browser
sub set_cookie {

   my($self, $expire) = @_;
   my($c);

   # create, write cookie
   use CGI::Cookie;
   $c = new CGI::Cookie( -name     => 'Padlock',
                         -value    => Padlock->cread('session').'::'.Padlock->cread('string'),
                         -expires  => $expire || "+15m",
                         -path     => '/cgi-bin',
                         -secure   => 1,
                         -domain   => '.bu.edu',
                       );

   print "Set-cookie: $c\n";
   return(1); 

}

1;
