#! /usr/bin/perl -w

my $passwd='';
my %password=();
open ( PASS, "./passwd.txt" );
while ( <PASS> )
{   chomp ( my $line = $_);
    $line =~ s/\r|\n//g;
    my @tmpSplit = split (/\t/, $line);
    $password{$tmpSplit[0]}=$tmpSplit[2];
}
close PASS;


my @class=();
my %email=();
open ( CLASS, "./fullMembers.txt") || die "Can't open class member\n";
while (<CLASS>)
{   chomp ($line=$_);
    $line =~ s/\r|\n//g;
    my @tmpSplit = split (/\t/, $line);
    push @class, $tmpSplit[0];
    $email{$tmpSplit[0]}=$tmpSplit[1];
}
close CLASS;


foreach (@class)
{   open (MESS, ">./message.txt");
    print MESS "\n!! This is an automatically generated message.\n";
    print MESS "!! DON'T REPLY TO THIS EMAIL\n";
    print MESS "!! If you have any question, send it to juhur\@indiana.edu\n\n";
    print MESS "Hi $_\n";
    print MESS "Here is your password to L519 Project Evaluation Form\n";
    print MESS "http://darwin.informatics.indiana.edu/cgi-bin/col/courses/L519/Eval/Proj2/EvalProj2.cgi\n";
    print MESS "Password : $password{$_}\n";
    print MESS "You will need this password to evaluate other groups' projects.\n\n";
    print MESS "One of your group member will have to introduce your webpage to others during the next lab session\n\n";
    print MESS "Thanks,\nJunguk\n\n";
    print MESS "!! DON'T REPLY TO THIS EMAIL\n\n";
    close MESS;

    system ("mail -s \"Password to L519 Group Project Evaluation Form\" $email{$_} \< message.txt");
}