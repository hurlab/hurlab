#! /usr/bin/perl -w

#******************************************************************************
#
#                L519 Home Homework #4-1
#
#                                         Written By Junguk HUR
#                                                juhur@indiana.edu
#
#  Desc:  This script accepts a sequence file in FASTA format
#         and will calculate the percentages of each character
#         Refer to README_find_percent.doc for more details
#
#******************************************************************************

# To use this perl script in a strict manner with all possible warnings
use strict;
use warnings;

# To use the common subroutin collection
require "./commonsubs.pl";

# Declaration of package to be used for commandline options
use Getopt::Long;

# GetOpt configuration for bundling and ignorecase
Getopt::Long::Configure ("bundling" , "ignore_case_always");

# Variable Init. for arguments and options
my $displayOption = 0;    # Option for display output

# Getting user's argument from command line
GetOptions ( "d" => \$displayOption );


# ------------------------------------------------------------------------------
#         File and Option Check
# ------------------------------------------------------------------------------
#
# This script accepts the first argument as a input file
unless ( defined $ARGV[0])
{
     # print an error message and exit the program if not exist
     displayERROR ();
    die ( "\n\tProper input file has not specified\n",
          "\nSample Usage:\n\n",
          "\t\$ perl find_percent.pl <SEQ FASTA FILE NAME>\n",
          "\nFor more detail, refer to README_find_percent.doc\n" );
}else
{
     unless ( open (INPUT , $ARGV[0] ))
     {
          # print an error message and exit the program if not exist
          fileErrorMessage ( $ARGV[0] );
          exit;
     }
}


# ------------------------------------------------------------------------------
#         Sequence File Loading and Check for Error
# ------------------------------------------------------------------------------
#
# Sequence file be containing either DNA or protein sequences.

# Initialize array for sequences
my @preambleLines=();     # for preamble only
my @fullSeq=();           # for full sequence only
my $seqLineCount=0;       # for counting sequence line

# Open Result File
open ( RESULT, ">".$ARGV[0].".pcount" );

foreach my $seqLine ( <INPUT> )
{
   # remove new line and carrier character for each line
   $seqLine =~ s/[\r|\n]//g;

   # if a preamble line present, add up the total seq number
   if ( $seqLine =~ /^\>(.*)/ )
   {
        push @preambleLines, $1;
        push @fullSeq, '';
   }else     # if it is a sequence line
   {
        my $tmpSeqLine = uc ($seqLine);

        # remove any blank, tab, number
        $tmpSeqLine =~ s/[\s|\t|\d]//g;

        # combine seq lines
        $fullSeq[$#fullSeq] .= $tmpSeqLine;
   }
}
close INPUT;


# ------------------------------------------------------------------------------
#         Count of Each Char
# ------------------------------------------------------------------------------

# Count for each sequence (divided by preamble)
for ( my $i =0; $i <= $#fullSeq ; $i ++ )
{
        # Sequence check
        my %seqCheckResult = seqCheckDNAProtein( $fullSeq[$i]);

        if ( $seqCheckResult{'SEQCHECK'} eq 'DNA' )
        {
            if ( $displayOption == 0)
            {
                print "The sequence $preambleLines[$i] ".
                      " is a DNA sequence\n".
                      "The result file name is ".$ARGV[0].".pcount\n";
            }
        }elsif ( $seqCheckResult{'SEQCHECK'} eq 'PROTEIN' )
        {
            if ( $displayOption == 0)
            {
                print "The sequence $preambleLines[$i] ".
                      " is a protein sequence\n".
                      "The result file name is ".$ARGV[0].".pcount\n";
            }
        }elsif ( $seqCheckResult{'SEQCHECK'} eq 'DNAError' )
        {
            if ( $displayOption == 0)
            {
                print "The sequence $preambleLines[$i] ".
                      "contains an errorneous DNA\n".
                      "Skipping this sequence\n";
            }
            goto endOfCurrentSequence;
        }elsif ( $seqCheckResult{'SEQCHECK'} eq 'ProteinError' )
        {
            if ( $displayOption == 0)
            {
                print "The sequence $preambleLines[$i] ".
                      "contains an errorneous charaters\n".
                      "Skipping this sequence\n";
            }
            goto endOfCurrentSequence;
        }

        # Remove the sequence check tag from the hash
        delete $seqCheckResult{'SEQCHECK'};

        # Calculate each char's probability
        my $totalNumOfChar =0;

        foreach ( keys %seqCheckResult )
        {
            $totalNumOfChar += $seqCheckResult{$_};
        }

        # Display the preamble
        print RESULT '>'.$preambleLines[$i]."\n";
        foreach ( keys %seqCheckResult )
        {
#            printf RESULT ( $_.': '."%.3f\n", ( $seqCheckResult{$_}/$totalNumOfChar ) );
             # To provide more accurate calculation, the value of probability
             # is printed as it is. Otherwise, in some case, the sum of
             # all probabilities go beyond 1
             print RESULT $_.': '.( $seqCheckResult{$_}/$totalNumOfChar )."\n";
        }

         # End of Current Sequence
         endOfCurrentSequence:
}

close RESULT;
exit;

