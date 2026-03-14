#! /usr/bin/perl -w

#******************************************************************************
#                L519 Home Homework #5-1
#
#                                         Written By Junguk HUR
#                                                juhur@indiana.edu
# Version 1.1
#    Modification : Display the endpoint score as well as the sum of all socres
#                   of alignment tables along the given path
#******************************************************************************

# To use this perl script in a strict manner with all possible warnings
use strict;
use warnings;

# To use the common subroutin collection
require "./commonsubs.pl";

# Declaration of package to be used for commandline options
use Getopt::Long;

# Variable Init. for arguments and options
my $seq1File = '';         # Sequence 1 input
my $seq2File = '';         # Sequence 2 input
my $matrixFile = '';       # Scoring matrix for sequence match
my $gapOpen = -10;         # Default gap opening score
my $gapExt = -1;           # Default gap extension score
my $numberOfAlignment = 3; # Maximum number of alignments

# Getting user's argument from command line
GetOptions ( "s1=s" => \$seq1File,
             "s2=s" => \$seq2File,
             "m=s"  => \$matrixFile,
             "g=s"  => \$gapOpen,
             "e=s"  => \$gapExt,
             "n=s"  => \$numberOfAlignment );


# ----------------------------------------------------------------------------
#                         Global Alignment
# ----------------------------------------------------------------------------
if(($seq1File eq "")||($seq2File eq "" )||($matrixFile eq ""))
{   print "#Error1: Some of the required options are missing.\n".
          "Please provide two sequence files and one scoring matrix file\n".
          "ex) global_align.pl -s1 <SEQ1> -s2 <SEQ2> -m <MATRIX> [-g GapOpen] [-e GapExt] [-n maxNum]\n";
    exit;
}else
{   # open matrix file, two sequence files
    my %matrix = open_score_matrix($matrixFile);
    my $matrixHeader = open_matrix_header($matrixFile);
    if ($matrixHeader eq "")   # If not ## header found
    {   $matrixHeader = "#Scoring Matrix: $matrixFile\n";
    }
    my ($seqHeader1, $sequence1) = getFASTASequence($seq1File, 'seq1');   # These are arrays
    my ($seqHeader2, $sequence2) = getFASTASequence($seq2File, 'seq2');   # These are arrays
    my $seqErrorExit = 'no';

    # Chech the sequence and Read the sequences into arrays
    my @seq1Array = ();     my @seq2Array = ();
    if (seqCheckProteinONLY(@$sequence1[0]) ne "PROTEIN")
    {   print "#Error4: The first sequence DOES NOT seem to be a protein sequence\n";
        $seqErrorExit = 'yes';
    }
    if (seqCheckProteinONLY(@$sequence2[0]) ne "PROTEIN")
    {   print "#Error5: The second sequence DOES NOT seem to be a protein sequence\n";
        $seqErrorExit = 'yes';
    }
    if ($seqErrorExit eq 'yes' )
    {   exit;
    }else
    {   @seq1Array = split ( //, $$sequence1[0] );
        @seq2Array = split ( //, $$sequence2[0] );
    }

    # Initialize Scoring Tables and Trace Back Array
    my @table = ();
    my @trace = ();

    # Initialize Direction Array
    # 0 = diagonal, 1=from left, 2=from up, 3 = diagonal or left
    # 4 = diagonal or up, 5=up or left, 6=up or left or diagonal
    my @direction = ( 0, 1, 2, 3, 4, 5, 6);

    # Initialize the scoring table
    initialize_tables( \@table, \@trace, $#seq1Array+1, $#seq2Array+2,
                       $gapOpen, $gapExt, \@direction, 'global' );

    # Now align the two sequences
    my @maxRow=();    my @maxCol=();   my $maxScore=0;
    align_sequences( \@table, \@trace, \@seq1Array, \@seq2Array, $gapOpen,
                     $gapExt, \@direction, 'global', \%matrix,
                     \@maxRow, \@maxCol, \$maxScore);

    # Possible sequences alignmented
    my @alignedSeq1 = ();     my @alignedSeq2 = ();    my %alignedScores = ();
    my $alignNum = 0;         my @alignedChar = ();

    # Trace back
    trace_back_global(\@table, \@trace, \@seq1Array, \@seq2Array, \@alignedSeq1,
                      \@alignedSeq2, \%alignedScores, \$alignNum, $numberOfAlignment );

    # --------------------------------------------------------------------------
    # Result Display
    # --------------------------------------------------------------------------
    print "#Alignment (Global) Succesfully Completed\n";
    print $matrixHeader;
    print "#Seq1 Length: ".($#seq1Array+1)." $$sequence1[0]\n";
    print "#Seq2 Length: ".($#seq2Array+1)." $$sequence2[0]\n";
    print "#GapOpening Penalty: $gapOpen\n";
    print "#GapExtension Penalty: $gapExt\n";

    # Sorting results by scores
    my @sorted_num = sort{$alignedScores{$b} <=> $alignedScores{$a}} keys(%alignedScores);
    my $count_alignment = 0;
    print "#Number of Alignments Found: ".($#sorted_num+1)."\n";
    if ($numberOfAlignment <= ($#sorted_num+1))
    {   print "#Number of Alignments Displayed: ".$numberOfAlignment."\n\n";
    }else
    {   print "#Number of Alignments Displayed: ".($#sorted_num+1)."\n\n";
    }

    foreach (@sorted_num)
    {   if($count_alignment == $numberOfAlignment)
        {   # Limit reached. Exit the loof
            last;
        }else
        {   $count_alignment++;
        }
        (my $percentIdentity, $alignedChar[$_]) = get_aligned_char($alignedSeq1[$_], $alignedSeq2[$_]);
        print ">>Rank.".$count_alignment." Global Alignment   Score:".
              sprintf("%.1f",$table[$#seq1Array+1][$#seq2Array+1]).
              "  Sum:".sprintf("%.1f",$alignedScores{$_}).
              "  Identity:$percentIdentity\%\n";
        printOutAlignments( $alignedSeq1[$_], $alignedSeq2[$_], $alignedChar[$_], 69, 1, 1 );
        print "\n";
    }
}
exit;


# ----------------------------------------------------------------------------
#               Subroutin collection for Global Alignments
# ----------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# sub trace_back_global
# This subroutin traces back from the end position of two aligned sequences.
# If a branch is found, it will evoke another subroutin named
# 'trace_back_global_sub' and continue to trace back the path
sub trace_back_global
{   my $table = $_[0];
    my $trace = $_[1];
    my $seq1Array = $_[2];
    my $seq2Array = $_[3];
    my $alignedSeq1 = $_[4];
    my $alignedSeq2 = $_[5];
    my $alignedScores = $_[6];
    my $alignNum = $_[7];
    my $numberOfAlignment = $_[8];

    my $i = $#$seq1Array+1;
    my $j = $#$seq2Array+1;
    my $currentNum = $$alignNum;
    my $branchFound = 'no';

    $$alignedSeq1[0] = '';
    $$alignedSeq2[0] = '';
    $$alignedScores{0} = 0;

    while($i >= 1 && $j >= 1)
    {   if($$trace[$i][$j] == 0)   # From diagonal
        {   $$alignedSeq1[$currentNum] = $$seq1Array[$i-1].$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $i--; $j--;
        }elsif($$trace[$i][$j] == 1)    # From left side
        {   $$alignedSeq1[$currentNum] = "-".$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $j--;
        }elsif($$trace[$i][$j] == 2)    # From up side
        {   $$alignedSeq1[$currentNum] = $$seq1Array[$i-1].$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = "-".$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $i--;
        }elsif($$trace[$i][$j] == 3)    # From either diagonal or left
        {   # Continue on the diagonal part
            $$alignedSeq1[$currentNum] = $$seq1Array[$i-1].$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $i--; $j--;

            # Continue on the left side part if possible
            if ($$alignNum != $numberOfAlignment - 1)
            {   # Where the number of current alignmnent is less than the threshold
                # Create another sequences and score values
                my $nextNum = $$alignNum + 1;
                $$alignedSeq1[$nextNum] = $$alignedSeq1[$currentNum];
                $$alignedSeq2[$nextNum] = $$alignedSeq2[$currentNum];
                $$alignedScores{$nextNum}= $$alignedScores{$currentNum};
                # Increase the total number of alignments
                $$alignNum++;
                trace_back_global_sub($table, $trace, $seq1Array, $seq2Array,
                                  $alignedSeq1, $alignedSeq2, $alignedScores,
                                  $alignNum, $i, $j, $nextNum, 1, $numberOfAlignment );
                $branchFound = 'yes'; #last;
            }
        }elsif($$trace[$i][$j] == 4)    # From either diagonal or up
        {   # Continue on the diagonal part
            $$alignedSeq1[$currentNum] = $$seq1Array[$i-1].$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $i--; $j--;
            # Continue on the up side part
            if ($$alignNum != $numberOfAlignment - 1)
            {   # Where the number of current alignmnent is less than the threshold
                # Create another sequences and score values
                my $nextNum = $$alignNum + 1;
                $$alignedSeq1[$nextNum] = $$alignedSeq1[$currentNum];
                $$alignedSeq2[$nextNum] = $$alignedSeq2[$currentNum];
                $$alignedScores{$nextNum}= $$alignedScores{$currentNum};
                # Increase the total number of alignments
                $$alignNum++;
                trace_back_global_sub($table, $trace, $seq1Array, $seq2Array,
                                  $alignedSeq1, $alignedSeq2, $alignedScores,
                                  $alignNum, $i, $j, $nextNum, 2, $numberOfAlignment );
                $branchFound = 'yes'; #last;
            }
        }elsif($$trace[$i][$j] == 5)    # From either left or up
        {   # Continue on the left side
            $$alignedSeq1[$currentNum] = "-".$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $j--;

            # Continue on the up side part
            if ($$alignNum != $numberOfAlignment - 1)
            {   # Where the number of current alignmnent is less than the threshold
                # Create another sequences and score values
                my $nextNum = $$alignNum + 1;
                $$alignedSeq1[$nextNum] = $$alignedSeq1[$currentNum];
                $$alignedSeq2[$nextNum] = $$alignedSeq2[$currentNum];
                $$alignedScores{$nextNum}= $$alignedScores{$currentNum};
                # Increase the total number of alignments
                $$alignNum++;
                trace_back_global_sub($table, $trace, $seq1Array, $seq2Array,
                                  $alignedSeq1, $alignedSeq2, $alignedScores,
                                  $alignNum, $i, $j, $nextNum, 2, $numberOfAlignment );
                $branchFound = 'yes'; #last;
            }
        }elsif($$trace[$i][$j] == 6)    # From either diagonal or left or up
        {   # Continue on the diagonal part
            $$alignedSeq1[$currentNum] = $$seq1Array[$i-1].$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $i--; $j--;
            # Continue on the left side part if possible
            if ($$alignNum != $numberOfAlignment - 1)
            {   # Where the number of current alignmnent is less than the threshold
                # Create another sequences and score values
                my $nextNum = $$alignNum + 1;
                $$alignedSeq1[$nextNum] = $$alignedSeq1[$currentNum];
                $$alignedSeq2[$nextNum] = $$alignedSeq2[$currentNum];
                $$alignedScores{$nextNum}= $$alignedScores{$currentNum};
                # Increase the total number of alignments
                $$alignNum++;
                trace_back_global_sub($table, $trace, $seq1Array, $seq2Array,
                                  $alignedSeq1, $alignedSeq2, $alignedScores,
                                  $alignNum, $i, $j, $nextNum, 1, $numberOfAlignment );
                $branchFound = 'yes'; #last;
            }

            # Continue on the up side part if possible
            if ($$alignNum != $numberOfAlignment - 2)
            {   # Where the number of current alignmnent is less than the threshold
                # Create another sequences and score values
                my $nextNum = $$alignNum + 1;
                $$alignedSeq1[$nextNum] = $$alignedSeq1[$currentNum];
                $$alignedSeq2[$nextNum] = $$alignedSeq2[$currentNum];
                $$alignedScores{$nextNum}= $$alignedScores{$currentNum};
                # Increase the total number of alignments
                $$alignNum++;
                trace_back_global_sub($table, $trace, $seq1Array, $seq2Array,
                                  $alignedSeq1, $alignedSeq2, $alignedScores,
                                  $alignNum, $i, $j, $nextNum, 2, $numberOfAlignment );
                $branchFound = 'yes'; #last;
            }
        }
    }

    #if($branchFound ne 'yes' )
    {   while($i > 0)   # For remaining seq1
        {   $$alignedSeq1[$currentNum] = $$seq1Array[$i-1].$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = "-".$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $i--;
        }
        while($j > 0)   # For remaining seq2
        {   $$alignedSeq1[$currentNum] = "-".$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $j--;
        }
    }
}

# ------------------------------------------------------------------------------
# sub trace_back_global_sub
# This subroutin traces back from the point whether two or more possible
# path are available. This is only used when a branch of path is found
sub trace_back_global_sub
{   my $table = $_[0];
    my $trace = $_[1];
    my $seq1Array = $_[2];
    my $seq2Array = $_[3];
    my $alignedSeq1 = $_[4];
    my $alignedSeq2 = $_[5];
    my $alignedScores = $_[6];
    my $alignNum = $_[7];
    my $i = $_[8];              # Remaining number of row
    my $j = $_[9];              # Remaining number of column
    my $currentNum = $_[10];    # Current Number of the aligned Sequence
    my $traceEndPosition = $_[11];
    my $original_i=$i;
    my $original_j=$j;
    my $numberOfAlignment=$_[12];

    my $backupTraceEndPosition = $$trace[$i][$j];
       $$trace[$i][$j] = $traceEndPosition;   # Temp. assign
    my $lastElementCheck = 'yes';
    my $branchFound = 'no';

    while($i >= 1 && $j >= 1)
    {   if($$trace[$i][$j] == 0)   # From diagonal
        {   $$alignedSeq1[$currentNum] = $$seq1Array[$i-1].$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $i--; $j--;
        }elsif($$trace[$i][$j] == 1)    # From left side
        {   $$alignedSeq1[$currentNum] = "-".$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $j--;
        }elsif($$trace[$i][$j] == 2)    # From up side
        {   $$alignedSeq1[$currentNum] = $$seq1Array[$i-1].$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = "-".$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $i--;
        }elsif($$trace[$i][$j] == 3)    # From either diagonal or left
        {   # Continue on the diagonal part
            $$alignedSeq1[$currentNum] = $$seq1Array[$i-1].$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $i--; $j--;

            # Continue on the left side part if possible
            if ($$alignNum != $numberOfAlignment - 1)
            {   # Where the number of current alignmnent is less than the threshold
                # Create another sequences and score values
                my $nextNum = $$alignNum + 1;
                $$alignedSeq1[$nextNum] = $$alignedSeq1[$currentNum];
                $$alignedSeq2[$nextNum] = $$alignedSeq2[$currentNum];
                $$alignedScores{$nextNum}= $$alignedScores{$currentNum};
                # Increase the total number of alignments
                $$alignNum++;
                trace_back_global_sub($table, $trace, $seq1Array, $seq2Array,
                                  $alignedSeq1, $alignedSeq2, $alignedScores,
                                  $alignNum, $i, $j, $nextNum, 1, $numberOfAlignment );
                $branchFound = 'yes'; #last;
            }
        }elsif($$trace[$i][$j] == 4)    # From either diagonal or up
        {   # Continue on the diagonal part
            $$alignedSeq1[$currentNum] = $$seq1Array[$i-1].$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $i--; $j--;
            # Continue on the up side part
            if ($$alignNum != $numberOfAlignment - 1)
            {   # Where the number of current alignmnent is less than the threshold
                # Create another sequences and score values
                my $nextNum = $$alignNum + 1;
                $$alignedSeq1[$nextNum] = $$alignedSeq1[$currentNum];
                $$alignedSeq2[$nextNum] = $$alignedSeq2[$currentNum];
                $$alignedScores{$nextNum}= $$alignedScores{$currentNum};
                # Increase the total number of alignments
                $$alignNum++;
                trace_back_global_sub($table, $trace, $seq1Array, $seq2Array,
                                  $alignedSeq1, $alignedSeq2, $alignedScores,
                                  $alignNum, $i, $j, $nextNum, 2, $numberOfAlignment );
                $branchFound = 'yes'; #last;
            }
        }elsif($$trace[$i][$j] == 5)    # From either left or up
        {   # Continue on the left side
            $$alignedSeq1[$currentNum] = "-".$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $j--;

            # Continue on the up side part
            if ($$alignNum != $numberOfAlignment - 1)
            {   # Where the number of current alignmnent is less than the threshold
                # Create another sequences and score values
                my $nextNum = $$alignNum + 1;
                $$alignedSeq1[$nextNum] = $$alignedSeq1[$currentNum];
                $$alignedSeq2[$nextNum] = $$alignedSeq2[$currentNum];
                $$alignedScores{$nextNum}= $$alignedScores{$currentNum};
                # Increase the total number of alignments
                $$alignNum++;
                trace_back_global_sub($table, $trace, $seq1Array, $seq2Array,
                                  $alignedSeq1, $alignedSeq2, $alignedScores,
                                  $alignNum, $i, $j, $nextNum, 2, $numberOfAlignment );
                $branchFound = 'yes'; #last;
            }
        }elsif($$trace[$i][$j] == 6)    # From either diagonal or left or up
        {   # Continue on the diagonal part
            $$alignedSeq1[$currentNum] = $$seq1Array[$i-1].$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $i--; $j--;
            # Continue on the left side part if possible
            if ($$alignNum != $numberOfAlignment - 1)
            {   # Where the number of current alignmnent is less than the threshold
                # Create another sequences and score values
                my $nextNum = $$alignNum + 1;
                $$alignedSeq1[$nextNum] = $$alignedSeq1[$currentNum];
                $$alignedSeq2[$nextNum] = $$alignedSeq2[$currentNum];
                $$alignedScores{$nextNum}= $$alignedScores{$currentNum};
                # Increase the total number of alignments
                $$alignNum++;
                trace_back_global_sub($table, $trace, $seq1Array, $seq2Array,
                                  $alignedSeq1, $alignedSeq2, $alignedScores,
                                  $alignNum, $i, $j, $nextNum, 1, $numberOfAlignment );
                $branchFound = 'yes'; #last;
            }

            # Continue on the up side part if possible
            if ($$alignNum != $numberOfAlignment - 2)
            {   # Where the number of current alignmnent is less than the threshold
                # Create another sequences and score values
                my $nextNum = $$alignNum + 1;
                $$alignedSeq1[$nextNum] = $$alignedSeq1[$currentNum];
                $$alignedSeq2[$nextNum] = $$alignedSeq2[$currentNum];
                $$alignedScores{$nextNum}= $$alignedScores{$currentNum};
                # Increase the total number of alignments
                $$alignNum++;
                trace_back_global_sub($table, $trace, $seq1Array, $seq2Array,
                                  $alignedSeq1, $alignedSeq2, $alignedScores,
                                  $alignNum, $i, $j, $nextNum, 2, $numberOfAlignment );
                $branchFound = 'yes'; #last;
            }
        }
    }
    # Restore the original traceback number for the last element
    if ($lastElementCheck eq 'yes')
    {   $$trace[$original_i][$original_j] = $backupTraceEndPosition;
        $lastElementCheck = 'no';
    }

    #if($branchFound ne 'yes' )
    {   while($i > 0)   # For remaining seq1
        {   $$alignedSeq1[$currentNum] = $$seq1Array[$i-1].$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = "-".$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $i--;
        }
        while($j > 0)   # For remaining seq2
        {   $$alignedSeq1[$currentNum] = "-".$$alignedSeq1[$currentNum];
            $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
            $$alignedScores{$currentNum} += $$table[$i][$j];
            $j--;
        }
    }
}

