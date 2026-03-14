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
my $match = 1;            # Score for match
my $misMatch = 0;         # Score for mismatch
my $gapOpen = 0;         # Default gap opening penalty
my $gapExt = 0;           # Default gap extension penalty
my $numberOfAlignment = 3; # Maximum number of alignments

# Getting user's argument from command line
GetOptions ( "s=s" => \$seq1File );

# For repeat finding, seq2 should be same as seq1
$seq2File = $seq1File;

# ----------------------------------------------------------------------------
#                         Local Alignment
# ----------------------------------------------------------------------------
if($seq1File eq "")
{   print "#Error1: Sequence file is missing\n".
          "ex) repeat_finding.pl -s <SEQ>\n";
    exit;
}else
{   # open matrix file, two sequence files
    my ($seqHeader1, $sequence1) = getFASTASequence($seq1File, 'seq1');   # These are arrays
    my ($seqHeader2, $sequence2) = getFASTASequence($seq2File, 'seq2');   # These are arrays
    my $seqErrorExit = 'no';

    # No need to check the sequences and Read the sequences into arrays
    my @seq1Array = split ( //, $$sequence1[0] );
    my @seq2Array = split ( //, $$sequence2[0] );

    # Gap Extension penalty assign
    $gapOpen = 0 - ($#seq1Array+2);
    $gapExt = $gapOpen;
    $misMatch = $gapOpen;

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
    align_sequences_matchMismatch ( \@table, \@trace, \@seq1Array, \@seq2Array,
          $gapOpen, $gapExt, \@direction, 'local', \@maxRow, \@maxCol, \$maxScore,
          $match, $misMatch);

    # Find any repeat
    my %repeatStarting=();  my %repeatEnding=(); my %repeatLength=();
    find_repeat(\@table,\@seq1Array,\%repeatStarting,
                \%repeatEnding, \%repeatLength);

    my @sorted_keys = sort{$repeatLength{$a} <=> $repeatLength{$b}} keys(%repeatLength);
    my $repeatCount = scalar @sorted_keys;
    my $repeatNum = 1;


    print "# Repeat Finding Succesfully Completed\n";
    print "# Seq     : $$sequence1[0]\n";
    print "# Length  : ".length($$sequence1[0])."\n\n";


    foreach (@sorted_keys)
    {   my $repeatLength = $repeatLength{$_};
        my $finalRepeatRegion='';
        my $coverage=0;
        my @repeatedRegion =();
        my @startingSplit = split(/\;/,$repeatStarting{$_});
        my @endingSplit = split(/\;/,$repeatEnding{$_});
        my $tmpSeq = $$sequence1[0];
        my $checkingStart=0;
        my $occurrenceCount=0;

        while ((length($repeatLength)+length($finalRepeatRegion)) <= length($$sequence1[0]))
        {  if (substr($tmpSeq,$checkingStart,$repeatLength) eq $_)
           {   $finalRepeatRegion .= $_;
               $checkingStart += $repeatLength;
               $occurrenceCount++;
               $coverage += $repeatLength;
           }else
           {   $finalRepeatRegion .= '-';
               $checkingStart++;
           }
        }
        $coverage = ($coverage /($#seq1Array+1))*100;

        if ($occurrenceCount >1)
        {  print ">>Repeat#$repeatNum: $_\n";
           print ">Occurrence:".($occurrenceCount)." Coverage:".
                 sprintf("%.1f",$coverage)."\%\n";
           printOutRepeat($$sequence1[0],$finalRepeatRegion,69,1,1);
        }
        $repeatNum++;
    }
}
exit;




# ----------------------------------------------------------------------------
#               Subroutin collection for Local Alignments
# ----------------------------------------------------------------------------

sub find_repeat
{   my $table = $_[0];
    my $seq1Array = $_[1];
    my $repeatStarting = $_[2];
    my $repeatEnding = $_[3];
    my $repeatLength = $_[4];
    my $lastColumn = $#$seq1Array+1;

    for(my $i=1; $i<=$#$seq1Array+1; $i++)
    {   for(my $j=$lastColumn; $j>=$i+1; $j--)
        {   if(($$table[$i][$j] != 0) && ($$table[$i-1][$j-1] == 0))
            {   repeat_enlongation($table,$lastColumn,$repeatStarting,$repeatEnding,
                                   $repeatLength, $i, $j, $seq1Array);
            }
        }
    }
}

sub repeat_enlongation
{   my $table=$_[0];
    my $lastColumn=$_[1];
    my $repeatStarting=$_[2];
    my $repeatEnding=$_[3];
    my $repeatLength=$_[4];
    my $i=$_[5];     my $j=$_[6];
    my $seq1Array=$_[7];
    my $tmpStartRow=$i;
    my $tmpStartCol=$j;
    my $tmpEndRow=0;   my $tmpEndCol=0;
    my $tmpLength=0;   my $tmpRepeat='';

    while(($i <= $lastColumn) && ($j <= $lastColumn) && ($$table[$i+1][$j+1] != 0) )
    {   $i++; $j++;
    }
    $tmpEndRow = $i;   $tmpEndCol=$j;

    for(my $k=$tmpStartRow; $k<=$tmpEndRow ; $k++)
    {   $tmpRepeat .= $$seq1Array[$k-1];
    }
    $tmpLength = $tmpEndRow - $tmpStartRow + 1;
    if ($tmpLength >= 1 )
    {   if (defined $$repeatStarting{$tmpRepeat})
        {       my @startingSplit = split(/\;/,$$repeatStarting{$tmpRepeat});
                my @endingSplit = split(/\;/,$$repeatEnding{$tmpRepeat});
                my $duplicateCheckCol = 'no';
                my $duplicateCheckRow = 'no';
                for (my $k=0; $k <= $#startingSplit; $k++ )
                {   if (($startingSplit[$k] eq $tmpStartRow) && ($endingSplit[$k] eq $tmpEndRow))
                    {   # If it was found before, skip this
                        $duplicateCheckRow='yes';
                        last;
                    }
                }
                for (my $k=0; $k <= $#startingSplit; $k++ )
                {   if (($startingSplit[$k] eq $tmpStartCol) && ($endingSplit[$k] eq $tmpEndCol))
                    {   # If it was found before, skip this
                        $duplicateCheckCol='yes';
                        last;
                    }
                }

                if (( $duplicateCheckCol eq 'no' ) && ( $duplicateCheckRow eq 'no' ))
                {   $$repeatStarting{$tmpRepeat} .= $tmpStartRow.';';
                    $$repeatEnding{$tmpRepeat} .= $tmpEndRow.';';
                    $$repeatStarting{$tmpRepeat} .= $tmpStartCol.';';
                    $$repeatEnding{$tmpRepeat} .= $tmpEndCol.';';
                }elsif (( $duplicateCheckCol eq 'yes' ) && ( $duplicateCheckRow eq 'no' ))
                {   $$repeatStarting{$tmpRepeat} .= $tmpStartRow.';';
                    $$repeatEnding{$tmpRepeat} .= $tmpStartRow.';';
                }elsif (( $duplicateCheckCol eq 'no' ) && ( $duplicateCheckRow eq 'yes' ))
                {   $$repeatStarting{$tmpRepeat} .= $tmpStartCol.';';
                    $$repeatEnding{$tmpRepeat} .= $tmpEndCol.';';
                }
        }else #No repeat was found previoulsy
        {   my @repeatArray = keys %$repeatStarting;
            if((scalar @repeatArray) == 0 )
            {   $$repeatStarting{$tmpRepeat} = $tmpStartRow.';';
                $$repeatEnding{$tmpRepeat} = $tmpEndRow.';';
                $$repeatStarting{$tmpRepeat} .= $tmpStartCol.';';
                $$repeatEnding{$tmpRepeat} .= $tmpEndCol.';';
                $$repeatLength{$tmpRepeat} = $tmpLength;
            }else
            {   if(partial_repeat($tmpRepeat,$repeatStarting,$repeatEnding,
                                  $tmpStartRow, $tmpEndRow,
                                  $tmpStartCol, $tmpEndCol, \@repeatArray) eq 'partial')
                {   #Partial means a duplicate repeat but partial
                }else
                {   $$repeatStarting{$tmpRepeat} = $tmpStartRow.';';
                    $$repeatEnding{$tmpRepeat} = $tmpEndRow.';';
                    $$repeatStarting{$tmpRepeat} .= $tmpStartCol.';';
                    $$repeatEnding{$tmpRepeat} .= $tmpEndCol.';';
                    $$repeatLength{$tmpRepeat} = $tmpLength;
                }
            }
        }
    }
}

sub partial_repeat
{   my $tmpRepeatOriginal = $_[0];
    my $repeatStarting = $_[1];
    my $repeatEnding = $_[2];
    my $originaltmpStartRow = $_[3];
    my $originaltmpEndRow = $_[4];
    my $originaltmpStartCol = $_[5];
    my $originaltmpEndCol = $_[6];
    my $repeatArray = $_[7];
    my $repeatOccur = 0;

    my $completeDuplicateFound ='no';
    for(my $i=0; $i <= $#$repeatArray; $i++)
    {   my $tmpStartRow = $originaltmpStartRow;
        my $tmpStartCol = $originaltmpStartCol;

        #while(substr($repeatArray[$i],0,$repeatLength) eq $tmpRepeat)
        my $repeatLength = length(@$repeatArray[$i]);
        my $tmpRepeat = $tmpRepeatOriginal;

        while(substr($tmpRepeat,0,$repeatLength) eq @$repeatArray[$i])
        {   $repeatOccur++;
            if ($repeatOccur >= 1)   #If repeated more than once
            {   my @startingSplit = split(/\;/,$$repeatStarting{@$repeatArray[$i]});
                my @endingSplit = split(/\;/,$$repeatEnding{@$repeatArray[$i]});
                my $duplicateCheckCol = 'no';
                my $duplicateCheckRow = 'no';
                for (my $k=0; $k <= $#startingSplit; $k++ )
                {   if (($startingSplit[$k] eq $tmpStartRow) && ($endingSplit[$k] eq ($tmpStartRow+$repeatLength-1)))
                    {   # If it was found before, skip this
                        $duplicateCheckRow='yes';
                        last;
                    }
                }
                for (my $k=0; $k <= $#startingSplit; $k++ )
                {   if (($startingSplit[$k] eq $tmpStartCol) && ($endingSplit[$k] eq ($tmpStartCol+$repeatLength-1)))
                    {   # If it was found before, skip this
                        $duplicateCheckCol='yes';
                        last;
                    }
                }

                if (( $duplicateCheckCol eq 'no' ) && ( $duplicateCheckRow eq 'no' ))
                {   $$repeatStarting{@$repeatArray[$i]} .= $tmpStartRow.';';
                    $$repeatEnding{@$repeatArray[$i]} .= ($tmpStartRow+$repeatLength-1).';';
                    $$repeatStarting{@$repeatArray[$i]} .= $tmpStartCol.';';
                    $$repeatEnding{@$repeatArray[$i]} .= ($tmpStartCol+$repeatLength-1).';';
                }elsif (( $duplicateCheckCol eq 'yes' ) && ( $duplicateCheckRow eq 'no' ))
                {   $$repeatStarting{@$repeatArray[$i]} .= $tmpStartRow.';';
                    $$repeatEnding{@$repeatArray[$i]} .= ($tmpStartRow+$repeatLength-1).';';
                }elsif (( $duplicateCheckCol eq 'no' ) && ( $duplicateCheckRow eq 'yes' ))
                {   $$repeatStarting{@$repeatArray[$i]} .= $tmpStartCol.';';
                    $$repeatEnding{@$repeatArray[$i]} .= ($tmpStartCol+$repeatLength-1).';';
                }
            }
            $tmpStartRow += $repeatLength-1;
            $tmpStartCol += $repeatLength-1;
            substr($tmpRepeat,0,$repeatLength) ='';
        }
        if ($tmpRepeat eq "")
        {   $completeDuplicateFound ='yes';
            last;
        }
    }
    if ($completeDuplicateFound eq 'yes')
    {   return('partial');
    }else
    {   return('new');
    }
}
