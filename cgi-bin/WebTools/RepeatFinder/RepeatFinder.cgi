#! /usr/bin/perl
#******************************************************************************
#
#                Repeat Finder
#
#                                         Written By Junguk HUR
#                                                juhur @ umich . edu
#
#  Last Modified : Feb 28, 2008
#  Desc:  This is the cgi script for performing alignments of
#         two protein sequences either local or global alignments
#
#******************************************************************************

require "./commonsubs.pl";
use CGI qw(:standard);

# -----------------------------------------------------------------------------
my @errorMessage			=();  
my $seq1Final				='';    
my $seq2Final				='';

my $crossImageURL			= 'http://jdrf.neurology.med.umich.edu/juhur/icons/crossImage.jpg';
my $emailImageURL			= 'http://jdrf.neurology.med.umich.edu/juhur/icons/email.jpg';
my $sequenceAlignCGIURL		= 'http://jdrf.neurology.med.umich.edu/juhur/cgi-bin/WebTools/SeqAlign/SeqAlign.cgi';
my $simpleSeqAlignCGIURL	= 'http://jdrf.neurology.med.umich.edu/juhur/cgi-bin/WebTools/SimpleSeqAlign/SimpleSeqAlign.cgi';
my $sequenceFittingCGIURL	= 'http://jdrf.neurology.med.umich.edu/juhur/cgi-bin/WebTools/SeqFitting/SeqFittingAlign.cgi';
my $repeatFinderCGIURL		= 'http://jdrf.neurology.med.umich.edu/juhur/cgi-bin/WebTools/RepeatFinder/RepeatFinder.cgi';

my $fileRandNum				= int(rand(1000000000000));
my $fittingResultFile		= "../results/fittingResult$fileRandNum.txt";
my $repeatResultFile		= "../results/repeatResult$fileRandNum.txt";
my $seq1File				= "../results/seq1$fileRandNum.txt";
my $seq2File				= "../results/seq2$fileRandNum.txt";
my $globalResultFile		= "../results/globalResults$fileRandNum.txt";
my $localResultFile			= "../results/localResults$fileRandNum.txt";
my $alignmentResultFile		= "../results/alignmentResult$fileRandNum.txt";

# -----------------------------------------------------------------------------

print header, start_html ( 'Repeat Finder' );
print "<body bgcolor=#C3EAE0>
      <h1 align=\"center\"><font face=\"Arial Black\" color=\"#9900CC\"><span style=\"background-color:rgb(153,255,204);\">REPEAT FINDER</span></font></h1>
      <HR COLOR = \"#FFFF66\" SIZE = 4>
      <font face = \"Courier New\" size = 2 >";


if (param('FIND'))   # If the submit button was pushed
{   #First step is checking sequences
    sequence_check_save();
    perform_alignment();

}else
{   if (param('sampleAlign'))
    {   print_intro();
        print_option_form_first();
        print_option_seq_sample();
        print_option_form_last();
        print_tail();
    }else
    {   print_intro();
        print_option_form_first();
        print_option_seq();
        print_option_form_last();
        print_tail();
    }
}

print "</font>";
print end_html;



sub perform_alignment
{      print "<font size=\"4\" face=\"Courier New\"><b>REPEAT Finding In Process</b></font><BR>";
       system ("perl ./repeat_finding.pl -s ./seq1 > $repeatResultFile");
       result_display("Repeat Finding","$repeatResultFile");
       print " <HR COLOR = \"#FFFF66\" SIZE = 4>";
}


sub result_display()
{   my($title,$file)=@_;
    open ( FILE, $file);
    my @fileContent=<FILE>;

    foreach(@fileContent)
    {   $_ =~ s/\r|\n//g;
        $_ =~ s/ /&nbsp/g;
        print $_."<BR>";
    }
    print "<BR>";
}

sub sequence_check_save
{   if (param('sequence1Input'))
    {   open ( SEQ1, ">$seq1File");
        print SEQ1 param('sequence1Input');
        close SEQ1;
    }
}


sub print_intro
{  print "<table border='0'>
           <tr>
               <td width='100%' height='72'>
                   <p><font size='4' face='Arial'>Hello! Welcome to Junguk's Repeat Finding Tool. Here you can find repeated patterns in your sequence. Paste any sequence and you will see what kinds of repeats and how many of them are in your sequence. This repeat finding is based on the Smith-Waterman local alignment algorithm. (Note that this repeat finder is <b>NOT</b> perfectly working now)</font></p>
               </td>
           </tr>
       </table>
       <HR COLOR = \"#FFFF66\" SIZE = 4><BR><BR>";
}

sub print_option_form_first
{   # Display Option Alignment method & Sequence input
    print  "<form action='RepeatFinder.cgi' method='POST' enctype=\"multipart/form-data\">";
    print  "<table border=\"1\" width=\"960\" cellspacing=\"0\" bordercolordark=\"white\" bordercolorlight=\"black\">";
}

sub print_option_seq
{   print "     <tr align=\"center\" valign=\"top\">
                    <th width=\"240\" height=\"230\" align=\"left\" valign=\"middle\">
                        <p>&nbsp;&nbsp;<img src=\"$crossImageURL\" width=\"17\" height=\"17\" border=\"0\">    <b><font face=\"Arial Black\">SEQUENCE</font></b></p>
                    </th>
                    <td width=\"822\" height=\"230\" align=\"left\" valign=\"baseline\" colspan=\"3\">
                        <b><font face=\"Arial Black\">&nbsp&nbspPlease enter your sequence</font></b><BR><BR>
                        &nbsp;<textarea name=\"sequence1Input\" rows=\"8\" cols=\"80\"></textarea>
                    </td>
                </tr>";
}

sub print_option_seq_sample
{   my $sampleSeq1 = "AAAGTGTAAAGTGTAAAGTGT";
    print "     <tr align=\"center\" valign=\"top\">
                    <th width=\"240\" height=\"230\" align=\"left\" valign=\"middle\">
                        <p>&nbsp;&nbsp;<img src=\"$crossImageURL\" width=\"17\" height=\"17\" border=\"0\">    <b><font face=\"Arial Black\">SEQUENCE</font></b></p>
                    </th>
                    <td width=\"822\" height=\"230\" align=\"left\" valign=\"baseline\" colspan=\"3\">
                        <b><font face=\"Arial Black\">&nbsp&nbspPlease enter your sequence</font></b><BR><BR>
                        &nbsp;<textarea name=\"sequence1Input\" rows=\"8\" cols=\"80\">$sampleSeq1</textarea>
                    </td>
                </tr>";
}

sub print_option_form_last
{   print "</table>
                <p><input type=\"submit\" name=\"FIND\" value=\"FIND\"> <input type=\"reset\" name=\"resut\" value=\"RESET\"> <input type=\"submit\" name=\"sampleAlign\" value=\"SAMPLE_SEQ\"></p>
             </form>
          ";

}

sub print_tail
{   print "<HR COLOR = \"#FFFF66\" SIZE = 4><font size=\"3\"";
    print "Last Modified : Feb. 27, 2008<br>
		   Got any comment? Send an email to me<a href=\"mailto:windyskyemail-open\@yahoo.co.kr?subject=Protein Sequence Alignments\"><img src=\"$emailImageURL\" width=\"20\" height=\"20\" border=\"0\"></a>";
    print "</font>";
}


