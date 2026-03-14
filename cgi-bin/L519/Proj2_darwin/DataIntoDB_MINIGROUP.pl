#!/usr/bin/perl
use strict;
use DBI;

my $inFile = $ARGV[0];
my $projNum = $ARGV[1];

my $DB        = "DBI:mysql:database=juhurdb";
my $username  = "juhur";
my $password  = "bioinformatics";

my $dbh = DBI->connect($DB, $username, $password, {PrintError => 0})
    || die "Could not open database, ", $DBI::errstr;


# Upload
open (FILE,$inFile);
while ( <FILE> )
{   my $line=$_;   $line =~ s/\r\n//g;
    if ($line eq "")
    {   next;
    }elsif ( $line =~ /\-\-\-/ )
    {   # New Entry Begins From Here
        if (($evaluator ne "") && ( $GroupByMember{$evaluator} ne $presenter))
        {   my $dbCommand = "insert into PersonalEval values ('$evaluator', ".
                         "$projNum, '$presenter', $overall_quality, ".
                         "'$you_liked_most', '$suggestion')";
            $dbh->do($dbCommand) || die "Got an error on inserting : $DBI::errstr\n";
            my $dbCommand2 = "SELECT * FROM PersonalEval WHERE ".
                             "StudentName = $evaluator AND ".
                             "ProjectNumber = $projNum";

            my $sth = $dbh->prepare( $dbCommand2 );
            $sth->execute();

            while(my @row=$sth->fetchrow_array())
            {   print "@row\n";
            }
        }
        # Init for tmp values
        $overall_quality=0;          $you_liked_most='';
        $suggestion='';              $evaluator='';
        $presenter='';               $dbCommand='';
    }elsif ( $line =~ /^\#Evaluator\s+(\S.*)/ )
    {   $evaluator = $1;
    }elsif ( $line =~ /^\#Presenter\s+(\S.*)/ )
    {   $presenter = $1;
    }elsif ( $line =~ /^\#OveralQuality\s+(\d+)/ )
    {   $overall_quality = $1;
    }elsif ( $line =~ /^\#YouLikeMost/ )
    {   my @tmpSplit = split ( /\t/, $line );
        if ( $#tmpSplit == 0 )
        {   $you_liked_most = "__";
        }else
        {   $you_liked_most = $tmpSplit[$#tmpSplit];
        }
    }elsif ( $line =~ /^\#Suggestion/ )
    {   $line =~ s/\n|\r//g;
        my @tmpSplit = split ( /\t/, $line );
        if ( $#tmpSplit == 0 )
        {   $suggestion = "__";
        }else
        {   $suggestion = $tmpSplit[$#tmpSplit];
        }
    }
}   close FILE;
$dbh->disconnect;
exit;