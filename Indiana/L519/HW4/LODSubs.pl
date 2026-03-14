#!/usr/bin/perl

require "commonsubs.pl";

# ------------------------------------------------------------------------------
#         Subroutin Collection
# ------------------------------------------------------------------------------

# sub findPercentage
sub findPercentage
{
       # Accept the transferred sequence
       my ( $tmpSeq ) = @_;

       # Initialize array for sequences
       my @preambleLines=();     # for preamble only
       my @fullSeq=();           # for full sequence only
       my $seqLineCount=0;       # for counting sequence line
       my $output='';            # for saving output contents
                                 # This is used instead of file

       # Turn on off any screen display -> silent processing
       my $displayOption = 1;    # Turn off any display

       my @tmpSeqSplit = split ( /\n/, $tmpSeq );

       # Check preamble line and combine sequence lines if splited
       foreach my $seqLine ( @tmpSeqSplit )
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
                             "Continuing percentage calculation\n";
                   }
               }elsif ( $seqCheckResult{'SEQCHECK'} eq 'PROTEIN' )
               {
                   if ( $displayOption == 0)
                   {
                       print "The sequence $preambleLines[$i] ".
                             " is a protein sequence\n".
                             "Continuing percentage calculation\n";
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



               # Calculate each char's probability
               my $totalNumOfChar =0;

               foreach ( keys %seqCheckResult )
               {
                   $totalNumOfChar += $seqCheckResult{$_};
               }

               # Display the preamble
               $output .= '>'.$preambleLines[$i]."\n";


               # ----------------------------------------------------
               #             Laplace Correction
               # Depending on the sequence types, all characters
               # will be added one time (the counts of all possible characters
               # will be added one). But this is only applied when
               # the sequence is either protein or DNA. For erroneous
               # sequence, this step will be skipped

               my $allDNAChar = 'AGCT';
               my $allProteinChar = 'ARNDCQEGHILKMFPSTWVY';

               if ( $seqCheckResult{'SEQCHECK'} eq 'DNA' )
               {
                   my @charSplit = split ( //, $allDNAChar );
                   foreach ( @charSplit )
                   {
                       if ( not defined $seqCheckResult{$_} )
                       {
                           $seqCheckResult{$_}=1;
                       }else
                       {
                           $seqCheckResult{$_}++;
                       }
                       $totalNumOfChar++;
                   }
               }elsif ( $seqCheckResult{'SEQCHECK'} eq 'PROTEIN' )
               {
                   my @charSplit = split ( //, $allProteinChar );
                   foreach ( @charSplit )
                   {
                       if ( not defined $seqCheckResult{$_} )
                       {
                           $seqCheckResult{$_}=1;
                       }else
                       {
                           $seqCheckResult{$_}++;
                       }
                       $totalNumOfChar++;
                   }
               }




               # Remove the sequence check tag from the hash
               delete $seqCheckResult{'SEQCHECK'};


               foreach ( keys %seqCheckResult )
               {
                    $output .= sprintf ( $_.': '."%.3f\n", ( $seqCheckResult{$_}/$totalNumOfChar ) );
               }

                # End of Current Sequence
                endOfCurrentSequence:
       }
    return ( $output );
}   # end of findPercentage



sub LOD2Calculate
{
        # Accept three sequences
        my ( $seq1Tmp, $seq2Tmp, $dataTmp ) = @_;

        # ------------------------------------------------------------------------------
        #         File and Option Check
        # ------------------------------------------------------------------------------
        #
        # This script accepts the first argument as a input file

        # Initialize variables
        my $output='';            # for saving output contents
                                  # This is used instead of file


        # ------------------------------------------------------------------------------
        #         Sequence Check For Consistency
        # ------------------------------------------------------------------------------

        # Get the first (in case of mutiple sequences in a file) sequence
        my ( $headerSeq1, $seq1Seq ) = getFASTASequenceFromSingleVariable ( $seq1Tmp );
        my ( $headerSeq2, $seq2Seq ) = getFASTASequenceFromSingleVariable ( $seq2Tmp );
        my ( $headerData, $dataSeq ) = getFASTASequenceFromSingleVariable ( $dataTmp );

        # Check the sequence types ( DNA, Protein, erroneous DNA, erroneous protein)
        my $seq1CheckResult = seqCheckDNAProteinONLY ( @$seq1Seq[0] );
        my $seq2CheckResult = seqCheckDNAProteinONLY ( @$seq2Seq[0] );
        my %dataCheckResult = seqCheckDNAProtein ( @$dataSeq[0] );

        # Display error message, if any errorneous sequence was found
        my $seqErrorFound ='no';
        if (( $seq1CheckResult eq 'ProteinError' ) || ( $seq1CheckResult eq 'DNAError' ))
        {
            $output = "#ERROR: Errorneous Sequence in seq1 $seq1CheckResult<BR>";
            print '<font size="3">'.$output.'</font>';
            $seqErrorFound = 'yes';
        }
        if (( $seq2CheckResult eq 'ProteinError' ) || ( $seq2CheckResult eq 'DNAError' ))
        {
            $output = "#ERROR: Errorneous Sequence in seq2 $seq2CheckResult<BR>";
            print '<font size="3">'.$output.'</font>';
            $seqErrorFound = 'yes';
        }
        if (( $dataCheckResult{SEQCHECK} eq 'ProteinError' ) ||
            ($dataCheckResult{SEQCHECK} eq 'DNAError' ))
        {
            $output = "#ERROR: Errorneous Sequence in data $dataCheckResult{SEQCHECK}<BR>";
            print '<font size="3">'.$output.'</font>';
            $seqErrorFound = 'yes';
        }

        # if a sequence error was found, terminate the script.
        if ( $seqErrorFound eq 'yes' )
        {
            return ( $output );
        }


        # If the types of sequence contents among 3 sequences
        # display error message and quit.


        if (( $seq1CheckResult ne $seq2CheckResult ) ||
            ( $seq1CheckResult ne $dataCheckResult{SEQCHECK} ) ||
            ( $seq2CheckResult ne $dataCheckResult{SEQCHECK} ))
        {
            $output = "#ERROR: Sequence Type Not Matching<BR>".
                      "Seq#1 sequence seems to be $seq1CheckResult<BR>".
                      "Seq#2 sequence seems to be $seq2CheckResult<BR>".
                      "Data  sequence seems to be $dataCheckResult{SEQCHECK}<BR>";

            print '<font size="3">'.$output.'</font><BR><BR>';
#                  "<BR>Sequence types of three input files are NOT SAME<BR>".
#                  "Sequences should be either ALL DNA or ALL PROTEIN<BR>";
            return ( $output );
        }



# ------------------------------------------------------------------------------
#         Calculate Probability for Each Sequence Input 1, 2
# ------------------------------------------------------------------------------

        my $seq1ModelContent = findPercentage ( $seq1Tmp );
        my $seq2ModelContent = findPercentage ( $seq2Tmp );

        my %s1_prob = getFirstProbFromSeq($seq1ModelContent);
        my %s2_prob = getFirstProbFromSeq($seq2ModelContent);

        my $lodSeq1=0;
        my $lodSeq2=0;
        my $LOD=0;
        my $dataCount=0;

        my $homeImageLink = '<BR><p><a href="http://biokdd.informatics.indiana.edu/~juhur/Model.html">'.
                        '<img src="http://mypage.iu.edu/~juhur/L519/HW4/home.jpg" '.
                        'width="64" height="30" border="0"></a></p>';


        # ---------------------------------------------------------------------
        #    Protein and DNA adjustment
        # ---------------------------------------------------------------------
        # Depending on the sequence type, it will print out all the
        # character's probability, even though it doesn't appear in the data

       my $allDNAChar = 'AGCT';
       my $allProteinChar = 'ARNDCQEGHILKMFPSTWVY';

       if ( $dataCheckResult{'SEQCHECK'} eq 'DNA' )
       {
           my @charSplit = split ( //, $allDNAChar );
           foreach ( @charSplit )
           {
               if ( not defined $dataCheckResult{$_} )
               {
                   $dataCheckResult{$_}=0;
               }
           }
       }elsif ( $dataCheckResult{'SEQCHECK'} eq 'PROTEIN' )
       {
           my @charSplit = split ( //, $allProteinChar );
           foreach ( @charSplit )
           {
               if ( not defined $dataCheckResult{$_} )
               {
                   $dataCheckResult{$_}=0;
               }
           }
       }

        # Remove SEQCHECK Content
        delete $dataCheckResult{SEQCHECK};


        # Calculate the P(D|Seq1)
        foreach ( keys %dataCheckResult )
        {
            $lodSeq1 += $dataCheckResult{$_}*log($s1_prob{$_});
            $lodSeq2 += $dataCheckResult{$_}*log($s2_prob{$_});
            $dataCount += $dataCheckResult{$_};
        }

        $LOD = $lodSeq1 - $lodSeq2;


# ------------------------------------------------------------------------------
#         Output Handling
# ------------------------------------------------------------------------------

        $output  = "#Calculation Succesfully Completed\n";
        $output .= "#SEQ#1: @$headerSeq1[0]\n";
        $output .= "#SEQ#2: @$headerSeq2[0]\n";
        $output .= "#DATA: @$headerData[0]\n";
        $output .= sprintf ("#LOD score of DATA is %.3f\n", $LOD );

        if ( $LOD > 0 )
        {
            $output .= "#Data sequence belongs to SEQ#1 (@$headerSeq1)\n";
        }elsif ( $LOD < 0 )
        {
            $output .= "#Data seqeunce belongs to SEQ#2 (@$headerSeq2)\n";
        }else
        {
            $output .= "SEQ#1 and SEQ#2 have same probability\n";
        }

        my $divider = "---------------------------------------------------------------".
                      "------------\n";
        $output .= "\n\n";
        $output .= $divider;
        $output .= "CHAR\tM(SEQ#1)\tM(SEQ#2)\tDATA\tlog(D|M1)\tlog(D|M2)\n";
        $output .= $divider;



        foreach ( keys %dataCheckResult )
        {
            $output .= sprintf ( "$_\t%.3f\t\t%.3f\t\t$dataCheckResult{$_}\t", $s1_prob{$_}, $s2_prob{$_} );
            $output .= sprintf ( "%.3f\t%.3f\n",  $dataCheckResult{$_}*log($s1_prob{$_}),
                                             $dataCheckResult{$_}*log($s2_prob{$_}) );
        }
        $output .= $divider;
        $output .= "TOTAL\t1.000\t\t1.000\t\t$dataCount\t";
        $output .= sprintf ( "\%.3f\t%.3f\n", $lodSeq1, $lodSeq2 );
        $output .= $divider;
        $output .= sprintf ("log(D|M1)-log(D|M2)=%.3f\n", $LOD );
        $output .= $divider;
        $output .= sprintf ( "exp(log(D|M1)-log(D|M2))=%.3e\n", exp($LOD) );
        $output .= $divider;

        return ( $output );
}   # end of LOD2Calculate



# sub errorCheckFromVar
# This subroutin checkes the types of error from LOD2 result
sub errorCheckFromVar
{
    my ( $tmpSeq ) = @_;
    my @fileContent = split ( /\n/, $tmpSeq );

    if ( $fileContent[0] =~ /^\#Calculation Succesfully Completed/ )
    {
         return ( 'Success');
    }elsif ( $fileContent[0] =~ /^\#ERROR\: Missing Option/ )
    {
         return ( 'MissingOption' );
    }elsif ( $fileContent[0] =~ /^\#ERROR\: Cannot open the file (\S+)/ )
    {
         return ( 'NoFile' );
    }elsif ( $fileContent[0] =~ /^\#ERROR\: Errorneous Sequence in (\S+) (\S+)/)
    {
         return ( 'ErrorSequence' );
    }elsif ( $fileContent[0] =~ /^\#ERROR\: Sequence Type Not Matching/ )
    {
         return ( 'SeqTypeNotMatching' );
    }
}


# sub FASTAConversion
# This subroutin checks whether the sequence has a preamble (description)
# and if it doesn't have, it will add one
sub FASTAConversion
{
    my ( $seqID , $tmpSeq ) =@_;
    my @tmpSeqSplit = split ( /\n/, $tmpSeq );
    my $preambleFound ='no';
    my $newSeq ='';

    foreach my $seqLine ( @tmpSeqSplit )
    {
        if ( $preambleFound eq 'no' )
        {
            # If it has a preamble line
            if ( $seqLine =~ /^\s*(\>.*)/ )
            {
                $preambleFound = 'yes';
                $newSeq = $1."\n";
            }else
            {
                # If it only has space and etc.
                if ( $seqLine =~ /[^\s\t\d\r]/ )
                {
                    $newSeq .= $seqLine."\n";
                }else
                {
                    # Do nothing
                }
            }
        }
        else    # if a preamble sequence has been found
        {
            $newSeq .= $seqLine."\n";
        }
    }
    # Remove the list new line character and add the preamble if needed
    chomp( $newSeq );
    if ( $preambleFound eq 'no' )
    {
        $newSeq = '>'.$seqID."\n".$newSeq;
    }

    return ( $newSeq );
}

  1;
