my @class=();
open ( CLASS, "./fullMembers.txt") || die "Can't open class member\n";
while (<CLASS>)
{   chomp ($line=$_);
    $line =~ s/\r|\n//g;
    push @class, $line;
}
close CLASS;

open (RESULT, ">./passwd.txt");
foreach (@class)
{   my $pass=int(rand(10)*100000);
    $pass=substr($pass,0,4);
    print RESULT $_."\t".$pass."\n";
}
close RESULT;