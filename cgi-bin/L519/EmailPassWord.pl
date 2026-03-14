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
    print MESS "Hi $_\n\n";
    print MESS "Here is your password to L519 Project Evaluation Form\n\n";
    print MESS "http://darwin.informatics.indiana.edu/cgi-bin/col/courses/L519/Eval/Eval.cgi\n\n";
    print MESS "Password : $password{$_}\n\n";
    print MESS "You will need this password to evaluate other groups' project.\n\n";
    print MESS "Thanks,\n\nJunguk\n\n";
    close MESS;

    system ("mail -s \"Password to L519 Group Project Evaluation Form\" $email{$_} \< message.txt");
}