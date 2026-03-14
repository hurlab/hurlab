#! /usr/bin/perl -w

#******************************************************************************
#                L519 Home Homework #5-2
#
#                                         Written By Junguk HUR
#                                                juhur@indiana.edu
#
#  Desc: This script will align two sequences by the Smith-waterman
#        local alignment algorithm. Gap penalties and optionally
#        entered otherwise default values will be used.
#        Thsi will find all the possible global alignments, but users
#        may set the maximum number of outputs to be displayed
#
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
#                         Local Alignment
# ----------------------------------------------------------------------------
if(($seq1File eq "")||($seq2File eq "" )||($matrixFile eq ""))
{   print "#Error1: Some of the required options are missing.\n".
          "Please provide two sequence files and one scoring matrix file\n".
          "ex) local_align.pl -s1 <SEQ1> -s2 <SEQ2> -m <MATRIX> [-g GapOpen] [-e GapExt] [-n maxNum]\n";
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
    # 7 = stop here. It's no more positive path
    my @direction = ( 0, 1, 2, 3, 4, 5, 6, 7);

    # Initialize the scoring table
    initialize_tables( \@table, \@trace, $#seq1Array+1, $#seq2Array+2,
                       $gapOpen, $gapExt, \@direction, 'local' );

    # Now align the two sequences
    my @maxRow=();    my @maxCol=();  my $maxScore=0;
    align_sequences( \@table, \@trace, \@seq1Array, \@seq2Array, $gapOpen,
                     $gapExt, \@direction, 'local', \%matrix,
                     \@maxRow, \@maxCol, \$maxScore);

    # Possible sequences alignmented
    my @alignedSeq1 = ();     my @alignedSeq2 = ();    my %alignedScores = ();
    my $alignNum = 0;         my @alignedChar = ();    my $currentNum=0;
    my @startingPositionSeq1 = ();     my @startingPositionSeq2 = ();
    # Trace back
    $alignedSeq1[0] = '';
    $alignedSeq2[0] = '';
    $alignedScores{0} = 0;

    for(my $i=0; $i<=$#maxRow; $i++)
    {   trace_back_local(\@table, \@trace, \@seq1Array, \@seq2Array, \@alignedSeq1,
                         \@alignedSeq2, \%alignedScores, \$alignNum, $alignNum,
                          $maxRow[$i], $maxCol[$i], $trace[$maxRow[$i]][$maxCol[$i]],
                          $maxRow[$i], $maxCol[$i], \@startingPositionSeq1,
                          \@startingPositionSeq2);
        if ($i != $#maxRow )
        {   $alignNum++;
            $alignedSeq1[$alignNum] ='';
            $alignedSeq2[$alignNum] ='';
            $alignedScores{$alignNum}=0;
        }
    }



    # --------------------------------------------------------------------------
    # Result Display
    # --------------------------------------------------------------------------
    print "#Alignment (Local) Succesfully Completed\n";
    print $matrixHeader;
    print "#Seq1 Length: ".($#seq1Array+1)." $$sequence1[0]\n";
    print "#Seq2 Length: ".($#seq2Array+1)." $$sequence2[0]\n";
    print "#GapOpening Penalty: $gapOpen\n";
    print "#GapExtension Penalty: $gapExt\n";
    # Sorting results by scores
    my @sorted_num = sort{$alignedScores{$b} <=> $alignedScores{$a}} keys(%alignedScores);
    my $count_alignment = 0;

    if ($maxScore == 0)
    {   print "#Number of Alignment Found: 0\n".
              "#Number of Alignment Displayed: 0\n\n".
              "No LOCAL alignment is available\n";
    }else
    {   print "#Number of Alignments Found: ".($#sorted_num+1)."\n";
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
            print ">>Rank.".$count_alignment." Local Alignment   Score:".
                  sprintf("%.1f",$maxScore).
                  "  Sum:".sprintf("%.1f",$alignedScores{$_}).
                  "  Identity:$percentIdentity\%\n";
            if ( $startingPositionSeq1[$_] eq "")
            {   $startingPositionSeq1[$_] = 1; }
            if ( $startingPositionSeq2[$_] eq "")
            {   $startingPositionSeq2[$_] = 1; }
            printOutAlignments( $alignedSeq1[$_], $alignedSeq2[$_], $alignedChar[$_], 69,
                                $startingPositionSeq1[$_]+1, $startingPositionSeq2[$_]+1 );
            print "\n";
        }
    }
}
exit;




# ----------------------------------------------------------------------------
#               Subroutin collection for Local Alignments
# ----------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# sub trace_back_local
# This subroutin traces back from the highest scored position
# that are given from the main function. If a branch is found
# it will recursively call trace_back_local
sub trace_back_local
{   my $table = $_[0];
    my $trace = $_[1];
    my $seq1Array = $_[2];
    my $seq2Array = $_[3];
    my $alignedSeq1 = $_[4];
    my $alignedSeq2 = $_[5];
    my $alignedScores = $_[6];
    my $alignNum = $_[7];
    my $currentNum = $_[8];
    my $maxRow = $_[9];
    my $maxCol = $_[10];
    my $direction = $_[11];
    my $originalMaxRow = $_[12];
    my $originalMaxCol = $_[13];
    my $startingPositionSeq1 = $_[14];
    my $startingPositionSeq2 = $_[15];

    my $i = $maxRow;
    my $j = $maxCol;
    my $branchFound = 'no';
    my $backupTraceEndPosition = $$trace[$i][$j];
       $$trace[$i][$j] = $direction;   # Temp. assign
    my $lastElementCheck = 'yes';


    while($i >= 1 && $j >= 1)
    {   if($$table[$i][$j] == 0)
        {   # No more trace back is available for the current sequence
            # Reset the original trace back and exit here
            if ($lastElementCheck eq 'yes')
            {   $$trace[$maxRow][$maxCol] = $backupTraceEndPosition;
                $lastElementCheck = 'no';
            }
            $$startingPositionSeq1[$currentNum] = $originalMaxRow - getActualSeqLength($$alignedSeq1[$currentNum]);
            $$startingPositionSeq2[$currentNum] = $originalMaxCol - getActualSeqLength($$alignedSeq2[$currentNum]);
            return();
        }elsif($$trace[$i][$j] == 0)   # From diagonal
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
        {   # Create another sequences and score values
            my $nextNum = $$alignNum + 1;
            $$alignedSeq1[$nextNum] = $$alignedSeq1[$currentNum];
            $$alignedSeq2[$nextNum] = $$alignedSeq2[$currentNum];
            $$alignedScores{$nextNum}= $$alignedScores{$currentNum};
            # Increase the total number of alignments
            $$alignNum++;
            # Continue on the diagonal part
            trace_back_local ($table, $trace, $seq1Array, $seq2Array,
                              $alignedSeq1, $alignedSeq2, $alignedScores,
                              $alignNum, $currentNum, $i, $j,  0,
                              $originalMaxRow,$originalMaxCol,
                              $startingPositionSeq1, $startingPositionSeq2  );
            # Continue on the left side part
            trace_back_local ($table, $trace, $seq1Array, $seq2Array,
                              $alignedSeq1, $alignedSeq2, $alignedScores,
                              $alignNum, $nextNum, $i, $j, 1 ,
                              $originalMaxRow,$originalMaxCol,
                              $startingPositionSeq1, $startingPositionSeq2  );
            $branchFound = 'yes'; last;
        }elsif($$trace[$i][$j] == 4)    # From either diagonal or up
        {   # Create another sequences and score values
            my $nextNum = $$alignNum + 1;
            $$alignedSeq1[$nextNum] = $$alignedSeq1[$currentNum];
            $$alignedSeq2[$nextNum] = $$alignedSeq2[$currentNum];
            $$alignedScores{$nextNum}= $$alignedScores{$currentNum};
            # Increase the total number of alignments
            $$alignNum++;
            # Continue on the diagonal part
            trace_back_local ($table, $trace, $seq1Array, $seq2Array,
                              $alignedSeq1, $alignedSeq2, $alignedScores,
                              $alignNum, $currentNum, $i, $j,  0,
                              $originalMaxRow,$originalMaxCol,
                              $startingPositionSeq1, $startingPositionSeq2  );
            # Continue on the up side part
            trace_back_local ($table, $trace, $seq1Array, $seq2Array,
                              $alignedSeq1, $alignedSeq2, $alignedScores,
                              $alignNum, $nextNum, $i, $j, 2,
                              $originalMaxRow,$originalMaxCol,
                              $startingPositionSeq1, $startingPositionSeq2  );
            $branchFound = 'yes'; last;
        }elsif($$trace[$i][$j] == 5)    # From either left or up
        {   # Create another sequences and score values
            my $nextNum = $$alignNum + 1;
            $$alignedSeq1[$nextNum] = $$alignedSeq1[$currentNum];
            $$alignedSeq2[$nextNum] = $$alignedSeq2[$currentNum];
            $$alignedScores{$nextNum}= $$alignedScores{$currentNum};
            # Increase the total number of alignments
            $$alignNum++;
            # Continue on the left side part
            trace_back_local ($table, $trace, $seq1Array, $seq2Array,
                              $alignedSeq1, $alignedSeq2, $alignedScores,
                              $alignNum, $currentNum, $i, $j, 1,
                              $originalMaxRow,$originalMaxCol,
                              $startingPositionSeq1, $startingPositionSeq2  );
            # Continue on the up side part
            trace_back_local ($table, $trace, $seq1Array, $seq2Array,
                              $alignedSeq1, $alignedSeq2, $alignedScores,
                              $alignNum, $nextNum, $i, $j, 2 ,
                              $originalMaxRow,$originalMaxCol,
                              $startingPositionSeq1, $startingPositionSeq2  );
            $branchFound = 'yes'; last;
        }elsif($$trace[$i][$j] == 6)    # From either diagonal or left or up
        {   # Create another sequences and score values
            my $nextNum1 = $$alignNum + 1;
            my $nextNum2 = $$alignNum + 2;
            $$alignedSeq1[$nextNum1] = $$alignedSeq1[$currentNum];
            $$alignedSeq2[$nextNum1] = $$alignedSeq2[$currentNum];
            $$alignedScores{$nextNum1}= $$alignedScores{$currentNum};
            $$alignedSeq1[$nextNum2] = $$alignedSeq1[$currentNum];
            $$alignedSeq2[$nextNum2] = $$alignedSeq2[$currentNum];
            $$alignedScores{$nextNum2}= $$alignedScores{$currentNum};
            # Increase the total number of alignments
            $$alignNum += 2;
            # Continue on the diagonal part
            trace_back_local ($table, $trace, $seq1Array, $seq2Array,
                              $alignedSeq1, $alignedSeq2, $alignedScores,
                              $alignNum, $currentNum, $i, $j, 0 ,
                              $originalMaxRow,$originalMaxCol,
                              $startingPositionSeq1, $startingPositionSeq2  );
            # Continue on the left side part
            trace_back_local ($table, $trace, $seq1Array, $seq2Array,
                              $alignedSeq1, $alignedSeq2, $alignedScores,
                              $alignNum, $nextNum1, $i, $j, 1 ,
                              $originalMaxRow,$originalMaxCol,
                              $startingPositionSeq1, $startingPositionSeq2  );
            # Continue on the up side part
            trace_back_local ($table, $trace, $seq1Array, $seq2Array,
                              $alignedSeq1, $alignedSeq2, $alignedScores,
                              $alignNum, $nextNum2, $i, $j, 2 ,
                              $originalMaxRow,$originalMaxCol,
                              $startingPositionSeq1, $startingPositionSeq2  );
            $branchFound = 'yes'; last;
        }
    }
    # Restore the original traceback number for the last element
    if ($lastElementCheck eq 'yes')
    {   $$trace[$maxRow][$maxCol] = $backupTraceEndPosition;
        $lastElementCheck = 'no';
    }

    # Maybe this part is not necessary.
    if($branchFound ne 'yes' )
    {   if($$table[$i][$j] == 0)
        {   $$startingPositionSeq1[$currentNum] = $originalMaxRow - getActualSeqLength($$alignedSeq1[$currentNum]);
            $$startingPositionSeq2[$currentNum] = $originalMaxCol - getActualSeqLength($$alignedSeq2[$currentNum]);
            return();
        }else
        {   while($i > 0 && ($$trace[$i][$j] != 7))   # For remaining seq1
            {   $$alignedSeq1[$currentNum] = $$seq1Array[$i-1].$$alignedSeq1[$currentNum];
                $$alignedSeq2[$currentNum] = "-".$$alignedSeq2[$currentNum];
                $$alignedScores{$currentNum} += $$table[$i][$j];
                $i--;
            }
            while($j > 0 && ($$trace[$i][$j] != 7))   # For remaining seq2
            {   $$alignedSeq1[$currentNum] = "-".$$alignedSeq1[$currentNum];
                $$alignedSeq2[$currentNum] = $$seq2Array[$j-1].$$alignedSeq2[$currentNum];
                $$alignedScores{$currentNum} += $$table[$i][$j];
                $j--;
            }
        }
    }
}

