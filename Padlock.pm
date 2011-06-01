#
# Padlock.pm
#
# Main interface library for Padlock file transfer system 
#

use strict;
package Padlock;
my($VER) = 1.00;

my($CONFIGFILE) = '/etc/padlock/padlock.conf';
my(%CONFIGHASH);

sub new {
   
   my($self, %param) = @_;
   require Padlock::Session;
   
   # initialize static values based on the main config file
   open(MAIN_CONFIG, $CONFIGFILE) || $self->error("Can't open $CONFIGFILE: $!");
   while (<MAIN_CONFIG>) {
      chomp;
      next unless m/^(.+)\s*=\s*(.+)$/;
      $self->cset($1 => $2);
   }
   close(MAIN_CONFIG);

   # change out of web interface if required
   if ($param{nocookie}) { $self->cset(INTERFACE => 'NOWEB'); }
   else { $self->cset(INTERFACE => 'WEB'); }
   
   # authenticate user
   Padlock::Session->auth(%param); 

   # user is ok!
   return(bless {});
   
}

# logout - log out user
sub logout {

   require Padlock::Session;
   Padlock::Session->logout();
   
}

# cset - set config hash
sub cset {

   my($self, %param) = @_;

   if (%param) {
      while (my($k, $v) = each(%param)) {
         $CONFIGHASH{$k} = $v;
      }
   }

   return(1);
   
}

# cread - read from config hash
sub cread { 

   my($self, $key) = @_;
   
   if ($CONFIGHASH{$key}) {
      return($CONFIGHASH{$key});
   }
   else {
      return(undef);
   }
   
}

# cdump - dump config file to disk
sub cdump {

   my($self) = @_;

   if (!$self->cread('session')) {
      $self->error("Can't dump: no session defined!");
   }
   else {

      my($file);
      require Padlock::File;

      # give another 10 mins for expiry
      $self->cset(expire => time + 600);
      
      # dump file
      $file = Padlock::File->check($self->cread('SESSIONS').'/'.
                                   $self->cread('session'));
      
      open(SESSION_FILE, ">".$file) ||
         $self->error("Can't open session file ($file): $!");
      while (my($k, $v) = each %CONFIGHASH) {
         print SESSION_FILE "$k=$v\n";
      }
      close(SESSION_FILE);
      
   }

   return(1);

}

# cimport - import config file from disk
sub cimport {

   require Padlock::File;
   my($self, $session) = @_;
   my($file);
   
   if (!$session) { 
      $session = $self->rcfg('session') || 
         $self->error("Can't import session: none given!");
   }

   $file = Padlock::File->check($self->cread('SESSIONS').'/'.$session);

   # if session no longer exists
   if (!-e $file) {
      $self->error("Session expired");
   }

   # open and import
   open(SESSION_IMPORT, $file) || 
      $self->error("Can't import session ($file): $!"); 
   while (<SESSION_IMPORT>) {
      next unless m/(.+)\s*=\s*(.+)/;
      $self->cset($1 => $2);
   }
   close(SESSION_IMPORT);

   return(1);
   
}

sub flags { return(Padlock->cread('flags')); }
sub email { return(Padlock->cread('email')); }
sub root  { return(Padlock->cread('root') || '/');  }
sub cwd   { return(Padlock->cread('cwd')  || '/');   }
sub home  { return(Padlock->cread('home'));  }


sub cp {
   
   require Padlock::File;
   my($self, $source, $target) = @_;
   
   $source = Padlock::File->check($self->home."/$source");
   $target = Padlock::File->check($self->home."/$target");

   Padlock::File->copy($source, $target);

   return(1);
   
}

sub mv {

   require Padlock::File;
   my($self, $source, $target) = @_;
   
   $source = Padlock::File->check($self->home."/$source");
   $target = Padlock::File->check($self->home."/$target");

   Padlock::File->move($source, $target);

   return(1);
 
}

sub rm {

   require Padlock::File;
   my($self, $target) = @_;

   $target = Padlock::File->check($self->home."/$target");

   if (-d $target) {
      $self->cset(cwd => Padlock::File->collapse($self->cwd.'/../'));
      $self->cdump();
      $self->cd($self->cwd);
   }
 
   Padlock::File->remove($target);
   
   return(1);

}

sub ls {

   require Padlock::File;
   my($self, $target, %param) = @_;

   if (!$target) { $target = './'; }
   $target = Padlock::File->check($self->home."/$target" ||
                                  $self->home);

   return(Padlock::File->list($target, %param));

}

sub cd {

   require Padlock::File;
   my($self, $target) = @_;
   my($temp_target) = $target || '/';
 
   $target = Padlock::File->check($self->home."/$target" ||
                                  $self->home.'/');

   if (substr($target, 0, length($self->home)) ne $self->home) {
      $target = $self->home;
      $temp_target = '/';
   }
         
   Padlock::File->chdir($target);

   $self->cset(cwd => Padlock::File->collapse($temp_target));
   
   return(1);


}

sub mkdir {

   require Padlock::File;
   my($self, $target) = @_;

   $target = Padlock::File->check($self->home."/$target");

   Padlock::File->mkdir($target);

   return(1);
   
}

sub filemod {

   require Padlock::File;
   my($self, $file) = @_;

   $file = Padlock::File->check($self->home."/$file");

   return(Padlock::File->modtime($file));

}

sub filesize {

   require Padlock::File;
   my($self, $file) = @_;
   my(@units) = qw/b kb mb gb tb/;
   my($i, $size) = (0, 0);
   
   $file = Padlock::File->check($self->home."/$file");

   $size = Padlock::File->size($file);
   while ($size / 1024 > 1) {
      $i++;
      $size = $size / 1024;
   }

   return(sprintf("%0.2f", $size).' '.$units[$i]);

}


sub filesend {

   require Padlock::File;
   my($self, $file) = @_;

   $file = Padlock::File->check($self->home."/$file");
   
   Padlock::File->send($file);

   return(1);

}

sub fullpath {
   
   my($self, $path) = @_;

   require Padlock::File;
   return(Padlock::File->collapse($self->cwd.'/'.$path));

}

sub realpath {

   my($self, $path) = @_;

   require Padlock::File;
   return(Padlock::File->check($self->home.'/'.$self->cwd.'/'.$path));

}

sub collapse {

   my($self, $path) = @_;
   
   require Padlock::File;
   return(Padlock::File->collapse($path));

}

sub check {

   my($self, $path) = @_;
   
   require Padlock::File;
   return(Padlock::File->check($self->home.'/'.$path));

}
sub html_header {

   require Padlock::HTML;
   Padlock::HTML->header();
   
}

sub html_footer {

   require Padlock::HTML;
   Padlock::HTML->footer();

}

# getip - get user's ip
sub getip {

   if ($ENV{REMOTE_ADDR}) {
      return($ENV{REMOTE_ADDR});
   }
   else {
      return(undef);
   }
   
}

sub log {

   require Padlock::File;
   
   my($self, $msg) = @_;
   my($file);
   my($timestamp);

   use POSIX qw/strftime/;
   $timestamp = strftime("[%D %H:%M]", localtime);
   
   
   # if no user, write to global log
   if (!$self->cread('user')) {   
      $file = Padlock::File->check($self->cread('DEFAULTLOG'));
   }
   # else write in user's log
   else {
      $file = Padlock::File->check($self->cread('LOGS').'/'.
                                   $self->cread('user').'.log');
   }

   open(LOG, '>>'.$file) || $self->error("Can't write to log ($file): $!");
   print LOG $timestamp, ' ', $msg, "\n";
   close(LOG);

   return(1);            

}

sub catch {

}

sub error {

   my($self, $msg) = @_;

   use CGI;
   my($q) = new CGI;

   print $q->header(-type => 'text/html', -expires => 'now');   
   html_header();
   print q|<font face="verdana" size="-1">|;
   print "Error: $msg";
   print q|</font>|;
   html_footer();
   exit(0);
   
   
}

1;

=head1 NAME

Padlock - Library for HTTP File Transfer

=head1 SYNOPSIS

 use CGI qw/:standard/;
 use Padlock;

 my($q) = new CGI;
 my($p) = new Padlock(session => $q->cookie('Padlock_ID'), str => $q->cookie('Padlock_Str'));

 $p->cd($p->home);

 for ($p->ls()) {
    print "$_\n";
 }


=head1 ABSTRACT


=head1 DESCRIPTION

=head2 Library

The Padlock library provides functionality for maintaining cookie-based sessions, file modification, and templated HTML output.  See "API" for details.

=head2 Function Scripts

Padlock function scripts interpret the library data and act as frontends to the file manager.

=head1 API

=head2 Cookie/Session Management

=over 4

=item C<new(username =E<gt> USER, password =E<gt> PASSWORD, [nocookie =E<gt> 0/1])>

=item C<new(session =E<gt> SESSION ID, str =E<gt> RANDOM STRING)>

Creates a new Padlock session.  Requires one of two login types, either username- and password-based, or cookie-based.  Username/password is self-explanatory.  The "nocookie" option, if set, prevents the C<auth()> procedure from writing a cookie to the user's browser.

For web-based use, Padlock requires that the username- and password-based session be converted into a session-based session.  This is usually done by logging in with username and password, setting a cookie, and redirecting the user:

 $p = new Padlock(username => $q->param('username'), password => $q->param('password'));
 # the nocookie option isn't set, so a cookie is set on the client machine

 $p->redirect('main.cgi');

This initiates a session, and further scripts can use the session-based login procedure:

 my($p) = new Padlock(session => $q->cookie('Padlock_ID'), str => $q->cookie('Padlock_Str'));

Note that the details of the session are dumped to disk immediately after creation.  See C<cdump()>.

=back

=head2 File Management

=over 4

=item C<home>

Returns the user's home directory in C<chroot()> fashion.  Implemented primarily for convenience.

 print $p->home;  # prints '/'

=item C<root>

Returns the user's root directory (full path name) in a B<non>-C<chroot()> fashion.

 print $p->root;  # prints '/var/secure_upload/users/testuser' for example

=item C<cp(SOURCE, TARGET)>

Copy a file or directory.  The root directory, "/", is interpreted as the B<user's> root directory, simulating a C<chroot()>.

Action is similar to that of the same-named UNIX command, in that directories can be copied (recursively), things can be copied into other directories, etc.

All arguments to C<cp()> are piped through C<check()> to verify that nothing ever escapes the user's home directory into the rest of the system.

=item C<mv(SOURCE, TARGET)>

Moves a file or directory.  See C<cp()>.

=item C<rm(FILE1, FILE2, ..., FILEN)>

Remove a file or directory.  See C<cp()>.

=item C<ls(DIR, [sort =E<gt> FIELD], [mixed =E<gt> 0/1])>

List a directory, sorted according to C<FIELD> (but defaults to sorting by filename).  Directories are suffixed with a "/".  

The C<MIXED> directive tells the lister wether or not the listing should have files and directories mixed together and then sorted, or sorted directories preceeding sorted files.  The default is 0, so they remain separate.

Valid C<FIELD>s are C<FILENAME>, C<FILESIZE>, C<EXTENSION>, C<DATE>.

=item C<cd(TARGET)>

Change directory.  Again, C<chroot()> is emulated.

 $p->cd('/');      # brings user home
 $p->cd($p->home); # does the same
 $p->cd();         # this too

=item C<upload(FILEHANDLE)>

Upload a file.  Must be used in conjunction with CGI.pm, with a call such as:

 $p->upload($q->upload('file'));

=item C<send(FILENAME)>

Uses an octet-stream header to send the file to the browser.  Works on any file in the user's directory.

=back

=head2 HTML

=over 4

=item C<redirect(URL)>

Redirect a user to a given URL.

=back

=head2 (Private) Helper Subroutines

=over 4

=over 4

=item C<catch()>

If the input value is NOT one (i.e., the operation failed and returned an error message) then the input  is passed off to the C<html_error()> method for log and display.

Most (publicly defined) methods are passed through the error catcher to avoid internal problems.  It's a good idea to send as much as possible through C<catch()> to avoid C<500 - Premature End of Script Headers> errors.

 $p->catch(open(FILE, "$file") || "Error!  Can't open $file: $!");

=back

=back

=head3 Configuration Hash

A configuration hash is maintained throughout the session; it gets dumped to a session file in between script runs, and can be modified during a run.

=over 4

=item C<cset()>

Sets a configuration directive.

=item C<cread()>

Reads a configuration directive.

=item C<cimport()>

Imports a dumped configuration hash.  Mainly useful for restoring a session.

=item C<cdump()>

Dumps a configuration hash to disk.  Used for inter-session maintenance of the current configuration.  This is called by B<anything> that modifies the user's environment (such as changing working directory, etc.).

=item C<flags>

Returns user's flags.  Same as C<$p-E<gt>cread('flags');>

=item C<email>

Returns user's e-mail address.  Same as C<$p-E<gt>cread('email');>

=item C<cwd>

Returns user's current working directory WITHIN the virtual C<chroot()>.  Same as C<$p-E<gt>cread('cwd');>

=back	

=head3 Cookie/Session Management

=over 4

=over 4

=item C<auth()>

Authenticates a user by either username/password or pre-existing session and random string.

=item C<cookie()>

Sets a cookie with updated expiration time and new random string.  Nothing special.

=back

=back

=head3 File Management

=over 4

=over 4

=item C<copy()>

Like C<cp()> above, except it does NOT simulate a C<chroot()>.  This can go ANYWHERE on the system (that the user can write to) so it should NOT be used under normal circumstances.

C<cp()> calls C<copy()> to do the actual copying, but many of the safeguards are built in to C<cp()>, so again, B<USE WITH EXTREME CAUTION!>

=item C<move()>

Moves a file or directory anywhere on the system.  See C<copy()>.

=item C<remove()>

Deletes a file or directory anywhere on the system.  See C<copy()>.

=item C<list()>

Lists a file or directory anywhere on the system.  See C<copy()>.

=item C<chdir()>

Changes directory to anywhere on the system.  C<cd()> has built-in safety checks to make sure the user doesn't escape his or her home directory.  This version lacks those, so B<USE WITH CARE!>

=item C<check()>

Checks and untaints a file or directory name.

C<check()> checks if the request file or path is inside of either the user's home directory or a preconfigured "safe" zone -- i.e., a temporary storage area. 

This is especially useful if using Perl's taint mode, because C<check()> returns an untainted version of its input which can then be sent to C<open()>, C<read()>, etc..

=item C<collapse()>

Collapses any given path into its cleanest format.  Helps avoid many errors.

 $p->collapse('/x//y/./././../z/a/.///b/../'); # returns /x/z/a/

=back

=back 

=head1 CONFIGURATION

Users are stored, by default, in F</etc/secure_upload/users>.  Don't touch this file.

By default, configuration is imported from F</etc/secure_upload/config>.  Edit this file to your liking.  

Directives are:

=over 4

=item C<sessions>

Location of where session files are located.  These files are generated by C<cdump()> and read by C<cimport()> at the end and beginning of each session, respectively.

 sessions = /var/secure_upload/sessions

=item C<root>

Defines the root directory for user files.  Default value is C</var/secure_upload/users>.  All home directories must be within this one (you can use C<mount --bind> to get around this, but the main idea is that all files need to be within a "protected" area so that C<check()> can make sure the paths aren't where they shouldn't be).

 root = /var/secure_upload/users

=item C<logdir>

Directory which holds logs of user transfer histories.

 logdir = /var/log/secure_upload 

=item C<admin>

Admin e-mail address.

 email = secureftp@slone.bu.edu

=item C<web_temp>

Temporary web-accessible space.  This is mainly used when a user requests a file he or she needs to be redirected to, or when viewing a file of some sort.

 web_temp = /var/www/temp

=item C<check_safe>

A colon-delimited list of directores regarded as "safe" by C<check()>.  

 check_safe = /var/www/temp:/tmp:/var/tmp

=back

=head1 USAGE

=head2 User Management

User management, for security's sake, is to be done via shell only.  There is no web frontend or library to provide this functionality, ONLY command-line scripts which must be run as the root user.

=head3 Adding Users

 ./adduser.pl -u USERNAME -d HOME -s 0/1 -e EMAIL

Adds a user.  The C<-d> flag should give a directory within the configured C<root>.  Leave no C<-e> flag to give no e-mail address.

The C<-s> flag specifies wether or not to make a system user.  This is useful for systems running Padlock and SSH, and you want users to be able to C<scp> and C<sftp> into the box.  The user shell is set to C</bin/false> by default.

=head3 Removing Users

 ./deluser.pl -u USERNAME

=head3 Modifying Users

 ./moduser.pl -u USERNAME -s 0/1 -e EMAIL -d HOME

Rewrites settings for C<USERNAME> to what's specified.  If something isn't specified, it uses what's there already.

=head3 Resetting Passwords

 ./chpass.pl -u USERNAME

Overwrites the password for C<USERNAME>.

=head2 Using the Library

You need to use this in conjunction with CGI.pm, to pass form values around.  From there, it's relatively simple to get anything done.

=head1 BUGS

No known bugs.

=head1 CHANGELOG

v1.0D - 06/18/2004 - Documentation draft 1

v0.77 - 06/15/2004 - "Old" code layout generally complete and usable.

=head1 AUTHOR

Matt Perry <mperry@slone.bu.edu>

Padlock was developed at Slone Epidemiology Center at Boston University.  Visit http://www.bu.edu/slone for more information.

=head1 VERSION

This is Padlock v1.00 (06/30/04)


