#! /usr/bin/perl -w

#******************************************************************************
#
#                L519 Home Homework #4-2
#
#                                         Written By Junguk HUR
#                                                juhur@indiana.edu
#
#  Desc:  This script will calculate the LOD score
#         for d treating s1 and s2 as models
#
#******************************************************************************

# To use this perl script in a strict manner with all possible warnings
use strict;

# To use the common subroutin collection
require "./commonsubs.pl";

# Declaration of package to be used for commandline options
use Getopt::Long;

# GetOpt configuration for bundling and ignorecase
#Getopt::Long::Configure ("bundling" , "ignore_case_always");

# Variable Init. for arguments and options
my $seq1File = '';         # Sequence 1 input as model 1
my $seq2File = '';         # Sequence 2 input as model 2
my $dataFile = '';         # Sequence for data file
my $outputFile = '';       # Output file path and name

# Getting user's argument from command line
GetOptions ( "s1=s" => \$seq1File,
             "s2=s" => \$seq2File,
             "d=s"  => \$dataFile,
             "o=s"  => \$outputFile );

# ------------------------------------------------------------------------------
#         File and Option Check
# ------------------------------------------------------------------------------
#
# This script accepts the first argument as a input file

# Filename for probability files
my $seq1ModelFile = $seq1File.'.pcount';
my $seq2ModelFile = $seq2File.'.pcount';
my $LODResultFile = $dataFile.'.LODResult';

#If output file path and name was not specified
if ( $outputFile ne "" )
{
    $LODResultFile = $outputFile;
}

#print "Result file name is $LODResultFile\n";


# This subroutin checks whether input was entered.
# If not, the script will terminate
if (( $seq1File eq "" ) || ( $seq2File eq "" ) ||
    ( $dataFile eq "" ))
{
     # print an error message and exit the program if not exist
     print "#Error: Missing Option\n".
           "Some of the proper input options has not been specified\n".
           "Sample Usage:\n\n".
           "\t\$ perl LOD2.pl -s1 seqFile1 -s2 seqFile2 -d seqFile3\n\n";
     exit;
}

# Open the files and check their existences
unless ( open ( SEQ1, $seq1File ) )
{
     fileErrorMessage ( $seq1File );        exit;
}
unless ( open ( SEQ2, $seq2File ) )
{
     fileErrorMessage ( $seq2File );        exit;
}
unless ( open ( DATA, $dataFile ) )
{
     fileErrorMessage ( $dataFile );        exit;
}
close SEQ1; close SEQ2; close DATA;



# ------------------------------------------------------------------------------
#         Sequence Check For Consistency
# ------------------------------------------------------------------------------

# Get the first (in case of mutiple sequences in a file) sequence
my ( $headerSeq1, $seq1Seq ) = getFASTASequence ( $seq1File );
my ( $headerSeq2, $seq2Seq ) = getFASTASequence ( $seq2File );
my ( $headerData, $dataSeq ) = getFASTASequence ( $dataFile );

# Check the sequence types ( DNA, Protein, erroneous DNA, erroneous protein)
my $seq1CheckResult = seqCheckDNAProteinONLY ( @$seq1Seq[0] );
my $seq2CheckResult = seqCheckDNAProteinONLY ( @$seq2Seq[0] );
my %dataCheckResult = seqCheckDNAProtein ( @$dataSeq[0] );

# Display error message, if any errorneous sequence was found
my $seqErrorFound ='no';
if (( $seq1CheckResult eq 'ProteinError' ) || ( $seq1CheckResult eq 'DNAError' ))
{
    print "#ERROR: Errorneous Sequence in seq1 $seq1CheckResult\n";
    $seqErrorFound = 'yes';
}
if (( $seq2CheckResult eq 'ProteinError' ) || ( $seq2CheckResult eq 'DNAError' ))
{
    print "#ERROR: Errorneous Sequence in seq2 $seq2CheckResult\n";
    $seqErrorFound = 'yes';
}
if (( $dataCheckResult{SEQCHECK} eq 'ProteinError' ) ||
    ($dataCheckResult{SEQCHECK} eq 'DNAError' ))
{
    print "#ERROR: Errorneous Sequence in data $dataCheckResult{SEQCHECK}\n";
    $seqErrorFound = 'yes';
}

# if a sequence error was found, terminate the script.
if ( $seqErrorFound eq 'yes' )
{
    exit;
}


# If the types of sequence contents among 3 sequences
# display error message and quit.
if (( $seq1CheckResult ne $seq2CheckResult ) ||
    ( $seq1CheckResult ne $dataCheckResult{SEQCHECK} ) ||
    ( $seq2CheckResult ne $dataCheckResult{SEQCHECK} ))
{
    print "#ERROR: Sequence Type Not Matching\n".
          "Seq#1 sequence seems to be $seq1CheckResult<BR>".
          "Seq#2 sequence seems to be $seq2CheckResult<BR>".
          "Data  sequence seems to be $dataCheckResult{SEQCHECK}<BR>";
    exit;
}


# ------------------------------------------------------------------------------
#         Calculate Probability for Each Sequence Input 1, 2
# ------------------------------------------------------------------------------

system ( "perl ./find_percent.pl ".$seq1File.' -d' );   #    -d option for quiet
system ( "perl ./find_percent.pl ".$seq2File.' -d' );   #    No display

my %s1_prob = getFirstProb($seq1ModelFile);
my %s2_prob = getFirstProb($seq2ModelFile);

my $lodSeq1=0;
my $lodSeq2=0;
my $LOD=0;
my $dataCount=0;


# Check the model sequences all probability of all characters from data seq.

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


print "#Calculation Succesfully Completed\n";
print "#SEQ#1: $seq1File\n";
print "#SEQ#2: $seq2File\n";
print "#DATA: $dataFile\n";
printf ("#LOD score of DATA is %.4f\n", $LOD );

if ( $LOD > 0 )
{
    print "#Data sequence belongs to SEQ#1 (@$headerSeq1)\n";
}elsif ( $LOD < 0 )
{
    print "#Data seqeunce belongs to SEQ#2 (@$headerSeq2)\n";
}else
{
    print "SEQ#1 and SEQ#2 have same probability\n";
}

# Save the result into a result file
open ( RESULT , ">$LODResultFile" );

print RESULT "#Calculation Succesfully Completed\n";
print RESULT "#SEQ#1: $seq1File\n";
print RESULT "#SEQ#2: $seq2File\n";
print RESULT "#DATA: $dataFile\n";
printf RESULT ("#LOD score of DATA is %.3f\n", $LOD );

if ( $LOD > 0 )
{
    print RESULT "#Data sequence belongs to SEQ#1 (@$headerSeq1)\n";
}elsif ( $LOD < 0 )
{
    print RESULT "#Data seqeunce belongs to SEQ#2 (@$headerSeq2)\n";
}else
{
    print RESULT "#SEQ#1 and SEQ#2 have same probability\n";
}
my $divider = "---------------------------------------------------------------".
              "------------\n";
print RESULT "\n\n";
print RESULT $divider;
print RESULT "CHAR\tM(SEQ#1)\tM(SEQ#2)\tDATA\tlog(D|M1)\tlog(D|M2)\n";
print RESULT $divider;

foreach ( keys %dataCheckResult )
{
    printf RESULT ( "$_\t%.3f\t\t%.3f\t\t$dataCheckResult{$_}\t", $s1_prob{$_}, $s2_prob{$_} );
    printf RESULT ( "%.3f\t%.3f\n",  $dataCheckResult{$_}*log($s1_prob{$_}),
                                     $dataCheckResult{$_}*log($s2_prob{$_}) );
}
print RESULT $divider;
print RESULT "TOTAL\t1.000\t\t1.000\t\t$dataCount\t";
printf RESULT ( "\%.3f\t%.3f\n", $lodSeq1, $lodSeq2 );
print RESULT $divider;
printf RESULT ("log(D|M1)-log(D|M2)=%.3f\n", $LOD );
print RESULT $divider;
printf RESULT ( "exp(log(D|M1)-log(D|M2))=%.3e\n", exp($LOD) );
print RESULT $divider;
