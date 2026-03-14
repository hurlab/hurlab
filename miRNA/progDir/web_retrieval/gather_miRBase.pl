#!/usr/bin/perl -w

use strict;
use LWP::UserAgent;

my @MIID = ();
if (defined $ARGV[0])
{   open (MIRBASE, $ARGV[0]) || die "! Can't open $ARGV[0]\n\n";
}else
{   #open (MIRBASE, "../miRBase/miFam.dat") || die "! Can't open ../miRBase/miFam.dat\n\n";
    die "! > gather_miRBase.pl <miRBase family data file>\n\n";
}

while(<MIRBASE>)
{   my $line = $_;
    $line =~ s/\r|\n//g;
    if ($line =~ /(MI\d+)/)
    {   push @MIID, $1;
    }
}   close MIRBASE;


open (RETRIEVED, ">$ARGV[0]"."_Target.txt") || die "! Can't write to miRBase_Target.txt\n\n";
open (FAILED, ">$ARGV[0]"."_Target_Failed.txt") || die "! Can't write to miRBase_Target_Failed.txt\n\n"; 
my $ua = LWP::UserAgent->new;
$ua->timeout(30);
my (%matureID2MIRANDA, %matureID2TARGETSCAN);
for (my $i=0; $i <= $#MIID; $i++)
{   print "! Processing ".($i+1).' / '.($#MIID +1)." : $MIID[$i] ...\t";
    my $miRBaseURL = "http://microrna.sanger.ac.uk/cgi-bin/sequences/mirna_entry.pl?acc=$MIID[$i]";
    my $result = $ua->get($miRBaseURL);
    my @lineContent = split(/\n/, $$result{'_content'});
    my $stemloopSeqID = '';
    my $genomicCoordinate = '';
    my $matureSeqID1 = '';
    my $matureSeqID2 = '';
    my $currentMatureSeqID = '';
    foreach my $line (@lineContent)
    {   if ($line =~ /^\s+Stem-loop sequence (\S+)/)
        {   $stemloopSeqID = $1;
        }elsif ($line =~ /^\s+Mature sequence (\S+)/)
        {   if ($matureSeqID1 eq "")
            {   $matureSeqID1 = $1;
                $currentMatureSeqID = $matureSeqID1;
            }else
            {   $matureSeqID2 = $1;
                $currentMatureSeqID = $matureSeqID2;
            }
        }elsif ($line =~ /(http:\/\/microrna.sanger.ac.uk\/cgi-bin\/targets\/\S+)\">/)
        {   $matureID2MIRANDA{$currentMatureSeqID} = $1;
        }elsif ($line =~ /(http:\/\/www.targetscan.org\/cgi-bin\/targetscan\/targetscan.cgi?\S+)\">/)
        {   $matureID2TARGETSCAN{$currentMatureSeqID} = $1;
        }elsif ($line =~ /(http:\/\/www.ensembl.org\/\S+\/contigview\?\S+)\">/)
        {   $genomicCoordinate = $1;
        }
    }

    if ($stemloopSeqID eq "")
    {   # Nothing was retrieved
        print FAILED $MIID[$i]."\n";
        print "Failed\n";
    }else
    {   print "Retrieved\n";
        print RETRIEVED $MIID[$i]."\tRETRIEVED\t";
        print RETRIEVED $stemloopSeqID."\t".$genomicCoordinate."\t".$matureSeqID1."\t";
        if (defined $matureID2MIRANDA{$matureSeqID1})
        {   print RETRIEVED $matureID2MIRANDA{$matureSeqID1}."\t";
        }else
        {   print RETRIEVED "\t";
        }
        if (defined $matureID2TARGETSCAN{$matureSeqID1})
        {   print RETRIEVED $matureID2TARGETSCAN{$matureSeqID1}."\t";
        }else
        {   print RETRIEVED "\t";
        }
        if ($matureSeqID2 ne "")
        {   print RETRIEVED $matureSeqID2."\t";
        }else
        {   print RETRIEVED "\t";
        }
        if (defined $matureID2MIRANDA{$matureSeqID2})
        {   print RETRIEVED $matureID2MIRANDA{$matureSeqID2}."\t";
        }else
        {   print RETRIEVED "\t";
        }
        if (defined $matureID2TARGETSCAN{$matureSeqID2})
        {   print RETRIEVED $matureID2TARGETSCAN{$matureSeqID2}."\n";
        }else
        {   print RETRIEVED "\n";
        }
    }   
}   close FAILED;   close RETRIEVED;