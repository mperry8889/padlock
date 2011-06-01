#
#
#
#
#
#
#
#
#
#
#

use strict qw/vars subs refs/;
package Padlock::File;


sub copy {
  
   my($self, $source, $target) = @_;

   if (!$source) { Padlock->error("Copy failed: no source specified"); }
   if (!$target) { Padlock->error("Copy failed: no target specified"); }
   $source = $self->collapse($source);
   $target = $self->collapse($target);

   # copying a dir
   if (-d $source) {
      require Directory::Copy;
      Directory::Copy::dircopy($source, $target) ||
         Padlock->error("Error copying $source to $target");
   }
   # copying a file
   else {
      require File::Copy;
      File::Copy::copy($source, $target) || 
         Padlock->error("Error copying $source to $target");
   }

   return(1);
   
}

sub move {

   require File::Copy;
   my($self, $source, $target) = @_;

   if (!$source) { Padlock->error("Move failed: no source specified"); }
   if (!$target) { Padlock->error("Move failed: no target specified"); }
   $source = $self->collapse($source);
   $target = $self->collapse($target);

   File::Copy::move($source, $target) || 
      Padlock->error("Error moving $source to $target");
      
   return(1);

}

sub mkdir {

   require File::Path;
   my($self, $target) = @_;

   if (!$target) { Padlock->error("mkdir failed: no target specified"); }
   $target = $self->collapse($target);

   if (-e $target) { Padlock->error("Error creating $target: file exists!"); }
   
   File::Path::mkpath($target) ||
      Padlock->error("Error creating $target");
   
   return(1);
   
}

sub remove {

   require File::Path;
   my($self, $target) = @_;

   if (!$target) { Padlock->error("mkdir failed: no target specified"); }
   $target = $self->collapse($target);

   File::Path::rmtree($target) ||
      Padlock->error("Error in mkdir of $target");
   
   return(1);
   
}

sub list {

   my($self, $target, %param) = @_;
   my(@list);
   my(@d);
   
   if (!$target) { use Cwd; $target = getcwd(); }
   $target = $self->collapse($target);

   opendir(LIST_DIR, $target) || Padlock->error("Can't list $target: $!");
   if ($param{sort} eq 'size') {
      for (sort { uc($self->size($a)) <=> uc($self->size($b)) } (readdir(LIST_DIR))) {
         if (-d $_) {
            push(@d, $_);
            @d = sort { uc($a) cmp uc($b) }(@d);    # keep dirs sorted alphabetically
         }
         else {
            push(@list, $_);
         }
      }
   }
   elsif ($param{sort} eq 'modified') {
      for (sort { 
                 (stat($a))[9] <=> (stat($b))[9]
                } (readdir(LIST_DIR))) {
         if (-d $_) {
            push(@d, $_);
            @d = sort { uc($a) cmp uc($b) }(@d);
         }
         else {
            push(@list, $_);
         }
      }
   }
   else {
      for (sort { uc($a) cmp uc($b) }(readdir(LIST_DIR))) {
         if (-d $_) {
            push(@d, $_);
            @d = sort { uc($a) cmp uc($b) } (@d);
         }
         else {
            push(@list, $_);
         }
      }
   }
   closedir(LIST_DIR);
   
   # listings should have sorted dirs on top of sorted files
   for (reverse(@d)) {
      unshift(@list, $_);
   }
   
   return(@list);
   
}

sub chdir {

   my($self, $target) = @_;
   
   if (!$target) { Padlock->error("chdir failed: no target specified"); }
   $target = $self->collapse($target);

   chdir($target) || Padlock->error("chdir to $target failed: $!");
   
}

# size - return formatted filesize
sub size {

   my($self, $file) = @_;
   my(@units) = qw/b kb mb gb tb/;
   my($i) = 0;
      
   $file = $self->collapse($file);
   
   return((stat($file))[7]);
   
}

# modtime - return formatted modification time
sub modtime {

   use POSIX qw/strftime/;
   my($self, $file) = @_;

   $file = $self->collapse($file);

   return(strftime("%d-%b-%Y %k:%M", localtime((stat($file))[9])));
                  # DD-mmm-YYYY HH:MM format 
   
}


# send - send a file
sub send {

   use CGI;
   my($self, $file) = @_;
   my($filename);
   my($q) = new CGI;

   $filename = $file;
   $filename =~ s/^.*(\\|\/)(.+)/$2/;
   
   open(FILE, $file) || Padlock->error("Can't open requested file ($file): $!");
   if (-B $file) {
      binmode(FILE);
   }

   print $q->header(-type => 'application/octet-stream',
                    -attachment => $filename,
                   );
   while (<FILE>) {
      print;
   }
   close(FILE);

}


# collapse - cleans up a given path
sub collapse {

   my($self, $path) = @_;
   my($lead) = "";
   my($suffix) = "";
   my(@real);

   if ($path =~ m/^\//) { $lead = "/"; }
   if ($path =~ m/\/$/) { $suffix = "/"; }
   for (split /\//, $path) {
      next if /^$/;
      next if /^[.]{1}$/;

      if (/^[.]{2}$/) {
         pop(@real);
         next;
      }

      push(@real, $_);
   }
   $path = $lead;
   $path .= join('/', @real);
   $path .= $suffix;

   if (!@real) { $path = '/'; }
   if ($path eq $lead) { $path = '/'; }
   if ($path eq '//') { $path = '/'; }

   return($path);

}

# check - checks the validity of a path and returns an untainted version of it
sub check {

   my($self, $path) = @_;
   
   # reject disallowed characters
   if ($path !~ m/^([A-Za-z0-9-_\.\[\]+\/\ ]+)$/) {
      Padlock->error("Invalid characters in path ($path) - rejected");
   }
   
   # get collapsed path
   $path = $self->collapse($path);
  
   # check that it's in the list of accepted paths
   for (split(/:/, Padlock->cread('VALID'))) {
      if ($path =~ m/$_/) {
         $path =~ m/(.+)/;
         return($1);
      }
   }

   Padlock->error("Invalid path ($path): not in accepted list");
      
}

1;
