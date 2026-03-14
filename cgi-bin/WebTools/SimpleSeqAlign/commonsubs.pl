#!/usr/bin/perl

#******************************************************************************
#
#  Junguk's common subroutin collections
#
#  Version 1.2
#  Last Modified Nov.15, 2004
#
# Please use the most up-to-date version.
#
#******************************************************************************

# ------------------------------------------------------------------------------
#         Subroutin Collection
# ------------------------------------------------------------------------------

# sub fileErrorMessage
# This subroutin displays an error message for non-existing file
sub fileErrorMessage
{
      my ( $fileName ) = @_;
      print "#Error: Cannot open the file $fileName".
            "\nPlease check the file name and run again. Program aborted.\n";
}


# sub displayERROR
# display an error logo(?)
sub displayERROR
{
     print "************************************************************",
           "**********\n\t\t\tERROR Encountered\n**********",
           "************************************************************\n";
}

# sub seqCheckDNAProtein
# This subroutin strictly chech the input sequence for DNA and protein
# It will count the chars in the sequence and determine whether
# it's a DNA or protein sequence, and even whether it contains contaminants.
sub seqCheckDNAProtein
{
    my ( $tmpSeq ) = @_;
    $tmpSeq = uc ( $tmpSeq );

    my %charCount = ();
    my @seqSplit = split ( //, $tmpSeq );

    my $nonDNAChar=0;
    my $nonAAChar =0;

    foreach ( @seqSplit )
    {
        if ( $_ =~ /[^AGCT]/ )
        {
            $nonDNAChar++;
        }
        if ( $_ =~ /[^ARNDCQEGHILKMFPSTWVY]/ )
        {
            $nonAAChar++;
        }
        $charCount{$_}++;
    }

    if ( $nonDNAChar == 0 )
    {
        $charCount{'SEQCHECK'} = 'DNA';
        return ( %charCount );
    }elsif ( $nonAAChar == 0 )
    {
        $charCount{'SEQCHECK'} = 'PROTEIN';
        return ( %charCount );
    }elsif ( $nonAAChar > 0 )
    {
        $charCount{'SEQCHECK'} = 'ProteinError';
        return ( %charCount );
    }elsif ( $nonDNAChar > 0 )
    {
        $charCount{'SEQCHECK'} = 'DNAError';
        return ( %charCount );
    }
}

# sub seqCheckDNAProteinONLY
# Same as seqCheckDNAProtein but this subroutin returns only the
# SEQCHECK result
sub seqCheckDNAProteinONLY
{
    my ( $tmpSeq ) = @_;
    $tmpSeq = uc ( $tmpSeq );

    my %charCount = ();
    my @seqSplit = split ( //, $tmpSeq );

    my $nonDNAChar=0;
    my $nonAAChar =0;

    foreach ( @seqSplit )
    {
        if ( $_ =~ /[^AGCT]/ )
        {
            $nonDNAChar++;
        }
        if ( $_ =~ /[^ARNDCQEGHILKMFPSTWVY]/ )
        {
            $nonAAChar++;
        }
        $charCount{$_}++;
    }

    if ( $nonDNAChar == 0 )
    {
        return ('DNA' );
    }elsif ( $nonAAChar == 0 )
    {
        return ( 'PROTEIN' );
    }elsif ( $nonAAChar > 0 )
    {
        return ( 'ProteinError' );
    }elsif ( $nonDNAChar > 0 )
    {
        return ( 'DNAError' );
    }
}


# --- For 2nd version of LOD2
# sub getFASTASequenceFromSingleVariable
# The subroutin return sequences in Array
# Two arrays: header and sequence
# No file is involved in this process.
sub getFASTASequenceFromSingleVariable
{
    my ( $tmpSeq ) = @_;
    my @preambleLines=();
    my @fullSeq=();

    my @tmpSeqSplit = split ( /\n/, $tmpSeq );

    foreach my $seqLine ( @tmpSeqSplit )
    {
        # Remove any possible newline character
        $seqLine =~ s/[\r|\n]//g;

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

    # Return arrays of preamble and fullSeq
    return ( \@preambleLines, \@fullSeq );
}



# sub getFirstProb
# This will read a model file and return it.
# In case there are multiple models, just return the first one
sub getFirstProb
{
     my ( $fileName ) = @_;
     my %tmpProb = ();
     my $seqCount=0;

     open ( FILE, $fileName );
     while ( <FILE> )
     {
         chomp ( my $line = $_ );
         if ( $line =~ /\>/ )
         {
             if ( $seqCount != 0 )
             {
                 last;
             }else
             {
                 $seqCount++;
             }
         }else
         {
             if ( $line =~ /^(\w)\: (\d\.\d+)/ )
             {
                 $tmpProb{$1} = $2;
             }
         }
     }     # end of while

     return ( %tmpProb );
}


# --- For 2nd version of LOD2
# sub getFirstProbFromSeq
# This will read a model file and return it.
# In case there are multiple models, just return the first one
sub getFirstProbFromSeq
{
     my ( $tmpSeq ) = @_;
     my %tmpProb = ();
     my $seqCount=0;

     my @tmpSeqSplit = split ( /\n/, $tmpSeq );

     foreach my $line ( @tmpSeqSplit )
     {
         if ( $line =~ /\>/ )
         {
             if ( $seqCount != 0 )
             {
                 last;
             }else
             {
                 $seqCount++;
             }
         }else
         {
             if ( $line =~ /^(\w)\: (\d\.\d+)/ )
             {
                 $tmpProb{$1} = $2;
             }
         }
     }     # end of while

     return ( %tmpProb );
}

# ------------------------------------------------------------------------------
#   New Subroutins Created for HW5 of L519
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# sub open_score_matrix
# This subroutin opens a score matrix file and returns as a hash of hash
sub open_score_matrix
{   my ($scoreMatrixFile) = @_;
    unless ( open (MATFILE, $scoreMatrixFile) )
    {   print "#Error2: Cannot open the matrix file\n".
              "Please check your path and file name\n";
    }

    my @second=();
    my %matScore=();

    while (<MATFILE>)
    {   chomp(my $line=$_);
        if ( $line !~ /^\#/ )
        {   if ( $line !~ /\d/ )    # No number means the second character line
            {   @second = split (/\s+/, $line);
            }else
            {   my @tmpScore = split(/\s+/, $line);
                # Assign score to each cell
                for( my $i=1; $i <= $#second; $i++ )
                {   $matScore{$tmpScore[0]}{$second[$i]} = $tmpScore[$i];
                }
            }
        }
    }
    return %matScore;
}

# ------------------------------------------------------------------------------
# sub open_matrix_header
# The subroutin returns the header parts of combined matrixes.
# This is not applicable to single matrix
sub open_matrix_header
{   my ($matrixFile) = @_;
    unless ( open (MATFILE, $matrixFile) )
    {   return();
    }
    my $matrixHeader='';
    while (<MATFILE>)
    {   my $line=$_;
        if ( $line =~ /^\#(\#.*)/ )
        {   $matrixHeader .= $1."\n";
        }
    }
    return $matrixHeader;
}

# ------------------------------------------------------------------------------
# sub getFASTASequence
# The subroutin reads and returns sequences in two arrays
# Two arrays: header and sequence
# Version : 2.0
sub getFASTASequence
{   my ($fileName, $tmpHeader ) = @_;
    my @preambleLines=();
    my @fullSeq=();

    unless ( open ( FILE, $fileName ))
    {   print "#Error3: Cannot open the sequence file\n".
              "Please check the file \'$fileName\'\n";
        exit;
    }

    while ( <FILE> )
    {   my $seqLine = $_;
        $seqLine =~ s/[\r|\n]//g;
        if ( $seqLine eq "" )
        {}elsif( $seqLine =~ /^\>(.*)/ )
        {   push @preambleLines, $1;
            push @fullSeq, '';
        }else     # if it is a sequence line
        {   my $tmpSeqLine = uc ($seqLine);
            # remove any blank, tab, number
            $tmpSeqLine =~ s/[\s|\t|\d]//g;
            # combine seq lines
            if ( $#fullSeq == -1 )
            {  push @preambleLines, $tmpHeader;
               push @fullSeq, $tmpSeqLine;
            }else
            {  $fullSeq[$#fullSeq] .= $tmpSeqLine;
            }
        }
    }
    close FILE;
    return ( \@preambleLines, \@fullSeq );
}

# ------------------------------------------------------------------------------
# sub initialize_tables
# This subroutin initialize two tables; scoring table & traceback table
# Depending on whether the alignment is for local or global
# Version 2.0, Modified on Nov. 15, 2004
# Update: to accomodate the "fitting x into y"
sub initialize_tables
{   my $table = $_[0];
    my $trace = $_[1];
    my $rowNum = $_[2];
    my $columnNum = $_[3];
    my $gapOpen = $_[4];
    my $gapExt = $_[5];
    my $direction = $_[6];
    my $alignMethod = $_[7];

    if($alignMethod eq 'local')
    {   for(my $i = 0; $i <= $rowNum; $i++)
        {   for(my $j=0; $j <= $columnNum; $j++)
            {   if($i == 0 && $j == 0)
                {   $$table[$i][$j] = 0;
                    $$trace[$i][$j] = 7;
                }elsif($i == 0 && $j != 0)
                {   $$table[$i][$j] = 0;
                    $$trace[$i][$j] = 1;
                }elsif($j == 0 && $i != 0)
                {   $$table[$i][$j] = 0;
                    $$trace[$i][$j] = 2;
                }else
                {   $$table[$i][$j] = 0;
                    $$trace[$i][$j] = 0;
                }
            }
        }
    }elsif($alignMethod eq 'global')
    {   for(my $i = 0; $i <= $rowNum; $i++)
        {   for(my $j = 0; $j <= $columnNum; $j++)
            {   if($i == 0 && $j == 0)
                {   $$table[0][0] = 0;
                    $$trace[0][0] = 0;
                }elsif($i == 0 && $j != 0 )
                {   $$table[$i][$j] = $gapOpen + ($j-1) * $gapExt;
                    $$trace[$i][$j] = 1;   # Assign 1 to direction (left)
                }elsif($j == 0 && $i != 0 )
                {   $$table[$i][$j] = $gapOpen + ($i-1) * $gapExt;
                    $$trace[$i][$j] = 2;   # Assign 2 to direction (up)
                }else
                {   $$table[$i][$j] = 0;
                    $$trace[$i][$j] = 0;   # Assign 0 to direction for default
                }
            }
        }
    }elsif($alignMethod eq 'fitting')
    {   for(my $i = 0; $i <= $rowNum; $i++)
        {   for(my $j = 0; $j <= $columnNum; $j++)
            {   if($i == 0 && $j == 0)
                {   $$table[0][0] = 0;
                    $$trace[0][0] = 7;
                }elsif($i == 0 && $j != 0 )
                {   $$table[$i][$j] = 0;
                    $$trace[$i][$j] = 7;   # Assign 1 to direction (left)
                }elsif($j == 0 && $i != 0 )
                {   $$table[$i][$j] = $gapOpen + ($i-1) * $gapExt;
                    $$trace[$i][$j] = 2;   # Assign 2 to direction (up)
                }else
                {   $$table[$i][$j] = 0;
                    $$trace[$i][$j] = 0;   # Assign 0 to direction for default
                }
            }
        }
    }
}


# ------------------------------------------------------------------------------
# sub align_sequences
# This subroutin aligns two sequences based on the substitution score matrix
sub align_sequences
{   my $table = $_[0];
    my $trace = $_[1];
    my $seq1Array = $_[2];
    my $seq2Array = $_[3];
    my $gapOpen = $_[4];
    my $gapExt = $_[5];
    my $direction = $_[6];
    my $alignMethod = $_[7];
    my $matrix = $_[8];
    my $maxRow = $_[9];
    my $maxCol = $_[10];
    my $maxScore = $_[11];

    my $lowerGapPenalty =0;
    if ($gapOpen <= $gapExt)
    {   $lowerGapPenalty = $gapExt;
    }else
    {   $lowerGapPenalty = $gapOpen;
    }
    my $diagonal = 0;
    my $up = 0;
    my $left = 0;

    for(my $i=1; $i <= $#$seq1Array+1; $i++)
    {   for(my $j=1; $j <= $#$seq2Array+1; $j++)
        {   # Calculate score from diagonal
            $diagonal = $$table[$i-1][$j-1] +
                        $$matrix{$$seq1Array[$i-1]}{$$seq2Array[$j-1]};
            # Calculate score from left (gap)
            if( $$trace[$i][$j-1] == 1 )
            {   $left = $gapExt + $$table[$i][$j-1];
            }elsif ( $$trace[$i][$j-1] == 3 ||
                     $$trace[$i][$j-1] == 5 || $$trace[$i][$j-1] == 6 )
            {   $left = $lowerGapPenalty + $$table[$i][$j-1];
            }else
            {   $left = $gapOpen + $$table[$i][$j-1];
            }
            # Calculate score from up (gap)
            if( $$trace[$i-1][$j] == 2 )
            {   $up = $gapExt + $$table[$i-1][$j];
            }elsif ( $$trace[$i-1][$j] == 4 ||
                     $$trace[$i-1][$j] == 5 || $$trace[$i-1][$j] == 6 )
            {   $up = $lowerGapPenalty + $$table[$i-1][$j];
            }else
            {   $up = $gapOpen + $$table[$i-1][$j];
            }
            # Assign the max score and trace
            ($$table[$i][$j], $$trace[$i][$j]) = matMax($diagonal, $left, $up);
            # Modify the table and trace for 'local' alignment
            if ( $alignMethod eq 'local' )
            {   if ($$table[$i][$j] <= 0)
                {   $$table[$i][$j] = 0;
                    $$trace[$i][$j] = 7;
                }else
                {   if ($$maxScore < $$table[$i][$j])
                    {   $$maxScore = $$table[$i][$j];
                        @$maxRow = (); $$maxRow[0]=$i;
                        @$maxCol = (); $$maxCol[0]=$j;
                    }elsif($$maxScore == $$table[$i][$j])
                    {   push(@$maxRow, $i);
                        push(@$maxCol, $j);
                    }
                }
            }
        }
    }
}

# ------------------------------------------------------------------------------
# sub matMax
# This subroutin selects the maximum score from three direction
# and return its direction with the maximum score
sub matMax
{   my $diagonal = $_[0];
    my $left = $_[1];
    my $up = $_[2];
    my $maxScore = $diagonal;
    my $maxTrace = 0;

    if ($maxScore < $left)
    {   $maxScore = $left;   }
    if ($maxScore < $up)
    {   $maxScore = $up;   }

    if ($maxScore == $diagonal)
    {   if ($maxScore == $left)
        {   if ($maxScore == $up)
            {   $maxTrace = 6;
            }else
            {   $maxTrace = 3;
            }
        }else
        {   if ($maxScore == $up)
            {   $maxTrace = 4;
            }else
            {   $maxTrace = 0;
            }
        }
    }else
    {   if ($maxScore == $left)
        {   if ($maxScore == $up)
            {   $maxTrace = 5;
            }else
            {   $maxTrace = 1;
            }
        }else
        {   if ($maxScore == $up)
            {   $maxTrace = 2;
            }
        }
    }
    return ($maxScore, $maxTrace);
}

# ------------------------------------------------------------------------------
# sub get_aligned_char
# This subroutin produces a alignment comparison between two sequencs
sub get_aligned_char
{   my ($alignedSeq1, $alignedSeq2)=@_;
    my @seq1Split = split (//,$alignedSeq1);
    my @seq2Split = split (//,$alignedSeq2);
    my $alignedChar = '';
    my $percentIdentity =0;
    my $totalAlignment =0;
    my $identicalMatch =0;

    for(my $i=0; $i<=$#seq1Split; $i++)
    {   if($seq1Split[$i] eq $seq2Split[$i])
        {   $alignedChar .= '|';
            $totalAlignment++;
            $identicalMatch++;
        }elsif(($seq1Split[$i] eq '-')||($seq2Split[$i] eq '-'))
        {   $alignedChar .= ' ';
        }else
        {   $alignedChar .= '*';
            $totalAlignment++;
        }
    }

    if ( $totalAlignment == 0 )
    {
    }else
    {   $percentIdentity = sprintf("%.1f",($identicalMatch/$totalAlignment)*100);
    }

    return ($percentIdentity,$alignedChar);
}

# ------------------------------------------------------------------------------
# sub printOutAlignments
# This subroutin displays aligned sequnces in nice format.
sub printOutAlignments
{   my ($alignedSeq1, $alignedSeq2, $alignedChar, $width,
        $seq1Starting, $seq2Starting )=@_;
    my $seq1Header = 'seq1: ';
    my $seq2Header = 'seq2: ';
    my $charHeader = '      ';
    my $actualSeq1Length = getActualSeqLength($alignedSeq1);
    my $actualSeq2Length = getActualSeqLength($alignedSeq2);
    my $longestSeqLength = simpleMax(($actualSeq1Length + length($seq1Starting)),
                                     ($actualSeq2Length + length($seq2Starting)));
    my $subLength1=0; my $subLength2=0;
    my $headerLength = length($seq1Header)+length($longestSeqLength);

    while(substr($alignedSeq1,0,$width-$headerLength) ne "")
    {   print $seq1Header;
        for (my $i=1; $i <= ($headerLength - length($seq1Starting) -length($seq1Header)); $i++)
        {   print " ";}
        print $seq1Starting.' '.substr($alignedSeq1,0,$width-$headerLength)."\n";
        $seq1Starting += getActualSeqLength(substr($alignedSeq1,0,$width-$headerLength));
        substr($alignedSeq1,0,$width-$headerLength)='';

        print $charHeader;
        for (my $i=1; $i <= length($longestSeqLength); $i++)
        {   print " ";}
        print ' '.substr($alignedChar,0,$width-$headerLength)."\n";
        substr($alignedChar,0,$width-$headerLength)='';

        print $seq2Header;
        for (my $i=1; $i <= ($headerLength - length($seq2Starting) -length($seq2Header)); $i++)
        {   print " ";}
        print $seq2Starting.' '.substr($alignedSeq2,0,$width-$headerLength)."\n\n";
        $seq2Starting += getActualSeqLength(substr($alignedSeq2,0,$width-$headerLength));
        substr($alignedSeq2,0,$width-$headerLength)='';
    }
}

# ------------------------------------------------------------------------------
# sub FASTAConversion
# This subroutin checks whether the sequence has a preamble (description)
# and if it doesn't have, it will add one
# WARNING: This will only return the first sequence from the first '>'
sub FASTAConversion
{   my ( $seqID , $tmpSeq ) =@_;
    $tmpSeq =~ s/\r//g;
    my @tmpSeqSplit = split ( /\n/, $tmpSeq );
    my $preambleFound ='no';
    my $newSeq ='';

    foreach my $seqLine ( @tmpSeqSplit )
    {   if ( $preambleFound eq 'no' )
        {   # If it has a preamble line
            if ( $seqLine =~ /^\s*(\>.*)/ )
            {   $preambleFound = 'yes';
                $newSeq = $1."\n";
            }else
            {   # If it only has space and etc.
                if ( $seqLine =~ /[^\s\t\d\r]/ )
                {   $newSeq .= $seqLine."\n";
                }else
                {   # Do nothing
                }
            }
        }
        else    # if a preamble sequence has been found
        {   $newSeq .= $seqLine."\n";
        }
    }
    # Remove the list new line character and add the preamble if needed
    chomp( $newSeq );
    if ( $preambleFound eq 'no' )
    {   $newSeq = '>'.$seqID."\n".$newSeq;
    }
    return ( $newSeq );
}

# ------------------------------------------------------------------------------
# sub seqCheckProteinONLY
# This subroutin check only if the sequence is protein or not
sub seqCheckProteinONLY
{   my ( $tmpSeq ) = @_;
    $tmpSeq = uc ( $tmpSeq );

    if ( $tmpSeq =~ /[^ARNDCQEGHILKMFPSTWVY]/ )
    {   return('NotPROTEIN');
    }else
    {   return('PROTEIN');
    }
}

# ------------------------------------------------------------------------------
# sub getActualSeqLength
# This subroutin calculates the actual sequence length
# excluding the gaps. This is especially useful for local alignments
sub getActualSeqLength
{   my ($tmpSeq)= @_;
    my $seqLength= 0;
    @tmpSplit=split(//,$tmpSeq);
    foreach(@tmpSplit)
    {   if($_ ne '-')
        {   $seqLength++;
        }
    }
    return($seqLength);
}

# ------------------------------------------------------------------------------
# sub simpleMax
# This subroutin selects the greater number between two
sub simpleMax
{   my ($first, $second) = @_;
    if ($first >= $second)
    {   return($first);
    }else
    {   return($second);
    }
}


# ------------------------------------------------------------------------------
#
#         Subroutins for MidTerm
#
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# sub align_sequences_matchMismatch
# This subroutin aligns two sequences based on the substitution score matrix
sub align_sequences_matchMismatch
{   my $table = $_[0];
    my $trace = $_[1];
    my $seq1Array = $_[2];
    my $seq2Array = $_[3];
    my $gapOpen = $_[4];
    my $gapExt = $_[5];
    my $direction = $_[6];
    my $alignMethod = $_[7];
    my $maxRow = $_[8];
    my $maxCol = $_[9];
    my $maxScore = $_[10];
    my $matchScore = $_[11];
    my $misMatchScore = $_[12];

    my $lowerGapPenalty =$gapOpen;
    if ($gapOpen <= $gapExt)
    {   $lowerGapPenalty = $gapExt;
    }else
    {   $lowerGapPenalty = $gapOpen;
    }
    my $diagonal = 0;
    my $up = 0;
    my $left = 0;

    for(my $i=1; $i <= $#$seq1Array+1; $i++)
    {   for(my $j=1; $j <= $#$seq2Array+1; $j++)
        {   # Calculate score from diagonal
            if ($$seq1Array[$i-1] eq $$seq2Array[$j-1])
            {   $diagonal = $matchScore + $$table[$i-1][$j-1];
            }else
            {   $diagonal = $misMatchScore + $$table[$i-1][$j-1];
            }
            # Calculate score from left (gap)
            if( $$trace[$i][$j-1] == 1 )
            {   $left = $gapExt + $$table[$i][$j-1];
            }elsif ( $$trace[$i][$j-1] == 3 ||
                     $$trace[$i][$j-1] == 5 || $$trace[$i][$j-1] == 6 )
            {   $left = $lowerGapPenalty + $$table[$i][$j-1];
            }else
            {   $left = $gapOpen + $$table[$i][$j-1];
            }
            # Calculate score from up (gap)
            if( $$trace[$i-1][$j] == 2 )
            {   $up = $gapExt + $$table[$i-1][$j];
            }elsif ( $$trace[$i-1][$j] == 4 ||
                     $$trace[$i-1][$j] == 5 || $$trace[$i-1][$j] == 6 )
            {   $up = $lowerGapPenalty + $$table[$i-1][$j];
            }else
            {   $up = $gapOpen + $$table[$i-1][$j];
            }
            # Assign the max score and trace
            ($$table[$i][$j], $$trace[$i][$j]) = matMax($diagonal, $left, $up);
            # Modify the table and trace for 'local' alignment
            if ( $alignMethod eq 'local' )
            {   if ($$table[$i][$j] <= 0)
                {   $$table[$i][$j] = 0;
                    $$trace[$i][$j] = 7;
                }else
                {   if ($$maxScore < $$table[$i][$j])
                    {   $$maxScore = $$table[$i][$j];
                        @$maxRow = (); $$maxRow[0]=$i;
                        @$maxCol = (); $$maxCol[0]=$j;
                    }elsif($$maxScore == $$table[$i][$j])
                    {   push(@$maxRow, $i);
                        push(@$maxCol, $j);
                    }
                }
            }
        }
    }
}

# ------------------------------------------------------------------------------
# sub printOutRepeat
# This subroutin displays repeated sequnces in nice format.
sub printOutRepeat
{   my ($alignedSeq1, $alignedSeq2, $width,
        $seq1Starting, $seq2Starting )=@_;
    my $seq1Header = 'SEQ: ';
    my $seq2Header = 'RPT: ';
    my $actualSeq1Length = getActualSeqLength($alignedSeq1);
    my $actualSeq2Length = getActualSeqLength($alignedSeq2);
    my $longestSeqLength = simpleMax(($actualSeq1Length + length($seq1Starting)),
                                     ($actualSeq2Length + length($seq2Starting)));
    my $subLength1=0; my $subLength2=0;
    my $headerLength = length($seq1Header)+length($longestSeqLength);

    while(substr($alignedSeq1,0,$width-$headerLength) ne "")
    {   print $seq1Header;
        for (my $i=1; $i <= ($headerLength - length($seq1Starting) -length($seq1Header)); $i++)
        {   print " ";}
        print $seq1Starting.' '.substr($alignedSeq1,0,$width-$headerLength)."\n";
        $seq1Starting += getActualSeqLength(substr($alignedSeq1,0,$width-$headerLength));
        substr($alignedSeq1,0,$width-$headerLength)='';

        print $seq2Header;
        for (my $i=1; $i <= ($headerLength - length($seq2Starting) -length($seq2Header)); $i++)
        {   print " ";}
        print $seq2Starting.' '.substr($alignedSeq2,0,$width-$headerLength)."\n\n";
        $seq2Starting += getActualSeqLength(substr($alignedSeq2,0,$width-$headerLength));
        substr($alignedSeq2,0,$width-$headerLength)='';
    }
}






1;
