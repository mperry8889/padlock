#
# Padlock::HTML.pm
#
# HTML control module
# 

use strict;
package Padlock::HTML;


# header - print out top part of html
sub header {

   print <<HTML;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
  "http://www.w3.org/TR/html4/loose.dtd">
<html>
   <head>
      <title>
         Slone Epidemiology Center: Secure File Transfer
      </title>
      <style type="text/css">
         <!--
         a:link {
            color: #cc0033;
            text-decoration: none;
         }
         a:visited {
            color: #cc0033;
            text-decoration: none;
         }
         a:hover {
            color: #cc0033;
            text-decoration: underline;
         }
 
         a:active {
            color: #cc0033;
            text-decoration: none;
         }
         .style_small_radio {
            font-size: 1;
            font-family: verdana;
         }
         .style_small_submit {
            font-size: 1;
            font-family: verdana;
         }
         .style_med_submit {
            font-size: -1;
            font-family: verdana;
         }
         -->
      </style>
   </head>

   <body bgcolor="#ffffff" text="#000000" link="#cc0033" vlink="#cc0033" alink="#cc0033">

   <center>
HTML

   if (Padlock->cread('mode') eq 'manager') {
      print <<MANAGER;
   <table align="center" width="85%" cellspacing=0 cellpadding=0>
      <tr>
         <!-- <td>
            <font face="verdana" size="-1">
               <b><a href="http://www.bu.edu/slone">Slone Epidemiology Center</a></b> > <b><a href="/cgi-bin/main.cgi">Secure File Transfer</a></b>
            </font>
         </td> -->

         <td align="right">
            <font face="verdana" size=1>
               switch to: <a href="/cgi-bin/main.cgi?m=viewer">file viewer</a> - file manager
            </font>
         </td>
      </tr>
   </table>
MANAGER
   }
   elsif (Padlock->cread('mode') eq 'viewer') {
      print <<VIEWER;
   <table align="center" width="85%" cellspacing=0 cellpadding=0>
      <tr>
         <!-- <td>
            <font face="verdana" size="-1">
               <b><a href="http://www.bu.edu/slone">Slone Epidemiology Center</a></b> > <b><a href="/cgi-bin/main.cgi">Secure File Transfer</a></b>
            </font>
         </td> -->

         <td align="right">
            <font face="verdana" size=1>
               switch to: <a href="/cgi-bin/main.cgi?m=manager">file manager</a> - file viewer
            </font>
         </td>
      </tr>
   </table>
VIEWER
   }
   else {

   }

   print <<HTML;
   
   <table align="center" width="85%" cellspacing=0 cellpadding=0>
      <tr>
         <td width="15%" valign="top">
            <table width="100%" cellspacing=0 cellpadding=1>
               <tr>
                  <td bgcolor="#000000" valign="top">
                     <table width="100%" cellspacing=0 cellpadding=3>
                        <tr>
                           <td bgcolor="#ffffff" valign="top">
                              <center>
                                 <font face="verdana" size="-1">
                                    <a href="/cgi-bin/main.cgi?d=/">Main Menu</a> - <a href="/cgi-bin/main.cgi">File Listing</a> - <a href="/cgi-bin/upload.cgi">Upload Files</a> <!-- - <a href="/cgi-bin/configure.cgi">Settings</a> - <a href="/cgi-bin/help.cgi">Help</a> --> - <a href="/cgi-bin/logout.cgi">Log Out</a>
                                 </font>
                              </center>
                           </td>
                        </tr>
                     </table>                  
                  </td>
               </tr>
            </table>
         </td>
      </tr>
      <tr>
         <td bgcolor="#ffffff" valign="top" align="left"><br>
HTML

}


sub footer {

   print <<HTML;
          </td>
       </tr>
    </table>
    <hr noshade size=1 width="85%" align="center">
    <center>
       <font face="verdana" size=1>
          Padlock v1.0 - Protected by <a href="/about/ssl.html">SSL</a> <a href="/about/ssl.html"><img src="/images/secure_ssl_lock.gif" border=0></a><br>
          Slone Epidemiology Center<br>
          <a href="/about/contact.html">contact</a>
       </font>
    </center>
   </body>
</html>

HTML

}

1;
