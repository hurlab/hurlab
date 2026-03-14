#! /usr/bin/perl -w
# This was done originally by Arvind Gopu
# Thanks Arvind for letting me use this CGI script

use CGI;
my $query = new CGI;

$proc_id = $query->param('proc_id');

print $query->header;
print $query->start_html("Apache on Darwin");
print "<h1> Apache on Darwin</h1>\n";

print "<p>This CGI script was obtained from Arvind Gopu. I appreciate his help</p>\n\n";
print "<p>Use this to kill runaway 'apache' processes on darwin.informatics.indiana.edu! </p>";
print "<p>Check the Process ID (PID) from Darwin by ps -ef |more </p>";
print $query->start_form;
print "<em>Process Id to kill?</em>:";
print $query->textfield('proc_id');
print $query->submit();

if ($proc_id ne "") {
    system ("kill -9 $proc_id");
    print "<p> Aahhhh got the sucker $proc_id ! (unless it was a non-apache process) <br> </p>\n";
    print "<p> Just to confirm doing ps -gx | grep $proc_id | grep -v \"grep\" gave back this... (nothing indicates the process was killed. Wooo hooo!) </p>\n";
#    $test = system("ps -gx | grep $proc_id | grep -v \"grep\"");
#    system("ps -gx | grep $proc_id | grep -v \"grep\"");

}

else {
    print "<p> Nothing to kill so far.. Waiting to pounce on processes!</p> " if ($proc_id eq "");
}

&print_tail();
print $query->end_html;

sub print_tail {
    print "<hr width=\"100%\" align=\"center\" TITLE=\"Copyright, Contact and Page Information Section\">
<div>
<font size=-2>
<address>Junguk Hur, Arvind Gopu</address>
<!-- hhmts start -->
Last Modified: Fri Sep 16 04:37:00 EST 2005
<!-- hhmts end -->
</font>
</div>";
}