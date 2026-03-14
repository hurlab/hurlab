#!/usr/bin/perl

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

# sub getFASTASequence
# The subroutin return sequences in Array
# Two arrays: header and sequence
sub getFASTASequence
{
    my ( $fileName ) = @_;
    my @preambleLines=();
    my @fullSeq=();

    open ( FILE, $fileName );
    while ( <FILE> )
    {
        #chomp (my $seqLine = $_ );
        my $seqLine = $_;
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
    close FILE;
    return ( \@preambleLines, \@fullSeq );
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

1;
