#! /usr/bin/perl -w
#******************************************************************************
#
#                Sequence Fitting Alignment
#
#                                         Written By Junguk HUR
#                                                 juhur @ umich.edu
#
#  Last Modified : Feb 28, 2008
#  Desc:  This is the cgi script for performing alignments of
#         fitting a shorter sequence into a longer sequence
#
#******************************************************************************

require "./commonsubs.pl";
use CGI qw(:standard);
use strict;

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
print header, start_html ( 'Sequences Fitting Alignment Tool' );
print "<body bgcolor=#C3EAE0>
       <h1 align=\"center\"><font face=\"Arial Black\" color=\"#9900CC\"><span style=\"background-color:rgb(153,255,204);\">Sequence Fitting Alignment Webtool</span></font></h1>
       <HR COLOR = \"#FFFF66\" SIZE = 4></HR>
       <font face = \"Courier New\" size = 2 >";

if (param('alignNow'))   # If the submit button was pushed
{   #First step is checking sequences
    sequence_check_save();
    #Alignment method selection check
	#alignment_method_check();
    #Gap penalty check
    gap_penalty_check();
    #Maximum display number check
    max_align_check();
    #Email Option Check
    email_check();

	if (scalar @errorMessage > 0)
    {   print_intro();
        error_display();
        print_option_form_first();
        print_option_seq();
        print_option_form_last();
        print_tail();
    }else
    {   perform_alignment();
    }
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
{   my $globalAlignResult = '';
    my $localAlignResult = '';
    my $match = param('match');
    my $misMatch = param('misMatch');
    my $gapOpen = param('gapOpen');
    my $gapExt = param('gapExt');
    my $maxNum = param('maxAlign');

    if (param('alignNow'))
    {  print "<font size=\"4\" face=\"Courier New\"><blink><b>Fitting Sequences In Process</blink></b></font><BR>";
       system ("perl ./seq_fitting.pl -s1 ./seq1 -s2 ./seq2 ".
               "-i $match -m $misMatch -g $gapOpen -e $gapExt -n $maxNum > $fittingResultFile");
       result_display("Fitting Sequence Alignment Result","$fittingResultFile");
       print " <HR COLOR = \"#FFFF66\" SIZE = 4>";
    }
    copy_result_files();
    print "<font size=\"4\" face=\"Courier New\"><blink><b>All Alignment Progresses Completed</blink></b></font><BR>
           <font size=\"3\" face=\"Courier New\"><b>RESULT FILES</b>&nbsp;&nbsp;<font size=\"2\">(Please right click and save them)</font><BR>&nbsp;&nbsp;&nbsp;
           <a href=\"$fittingResultFile\"><b>FITTING</b></a>&nbsp;&nbsp;&nbsp;";
    send_result_email();
}


sub copy_result_files
{	# This is to be used when the system does not allow new files to be created.
	#open ( FITTING, "./fittingResult.txt");
	#open ( RESULT, ">/var/www/html/juhur/I590_Math/HW4/fittingResult.txt");
	#while (<FITTING>)
	#{   my $line=$_;
	#    $line =~ s/\n/\r\n/g;
	#    print RESULT $line;
	#}
	#close FITTING;
	#close RESULT;
}


sub email_check
{   my $emailCheck = param('emailCheck');
    my $emailAddress = param('resultByEmail');
    if ($emailCheck eq 'sendToEmail')
    {   if ($emailAddress =~ /\@/)
        {   #It seems to be fine
        }else
        {   push (@errorMessage, "Your email address seems to be in wrong format");
        }
    }
}


sub send_result_email
{   my $emailCheck = param('emailCheck');
    my $emailAddress = param('resultByEmail');
    if ($emailCheck eq 'sendToEmail')
    {   if ($emailAddress =~ /\@/)
        {   # Probably correct form
            system ( "mail -s \"Alignment Result\" -b ".'windyskyemail-open@yahoo.co.kr'." \"$emailAddress\" < $fittingResultFile");
            print "<BR>The result was also successfully send to \"$emailAddress\"";
        }else
        {   print "<BR>Email could not be sent. Your email address seems to be wrong.<BR>";
        }
    }
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


sub gap_penalty_check
{   if (!param('gapOpen'))
    {   push(@errorMessage,"The gap opening penalty has not been specified");
    }elsif (param('gapOpen') =~ /[^\-\d\.]/ )
    {   push(@errorMessage,"The gap opening penalty is not a numeric value");
    }
    if (!param('gapExt'))
    {   push(@errorMessage,"The gap extension penalty has not been specified");
    }elsif (param('gapExt') =~ /[^\-\d\.]/ )
    {   push(@errorMessage,"The gap extension penalty is not a numeric value");
    }
}


sub max_align_check
{   if (!param('maxAlign'))
    {   push(@errorMessage,"The maximum number of alignments has not been specified");
    }elsif (param('maxAlign') =~ /[^\-\d\.]/ )
    {   push(@errorMessage,"The maximum number of alignments is not a numeric value");
    }
}


sub alignment_method_check
{   if (!param('global') && !param('local'))
    {   push(@errorMessage,"No alignment method was selected");
    }
}


sub sequence_check_save
{   my $sequenceErrorFound='no';
    if (param('seq1File') ne "")
    {   my $file = param('seq1File');
        my $file1Sequence ='';
        foreach my $line (<$file>)
        {   $line =~ s/\r//g;
            $file1Sequence .= $line;
        }
        $seq1Final = FASTAConversion("seq1",$file1Sequence);
    }elsif (param('sequence1Input') ne "")
    {   $seq1Final = FASTAConversion("seq1",param('sequence1Input'));
    }else
    {   push (@errorMessage, "The first sequence was not entered properly");
        $sequenceErrorFound='yes';
    }
    if (param('seq2File') ne "")
    {   my $file = param('seq2File');
        my $file2Sequence ='';
        foreach my $line (<$file>)
        {   $line =~ s/\r//g;
            $file2Sequence .= $line;
        }
        $seq2Final = FASTAConversion("seq2",$file2Sequence);
    }elsif (param('sequence2Input') ne "")
    {   $seq2Final = FASTAConversion("seq2",param('sequence2Input'));
    }else
    {   push (@errorMessage, "The second sequence was not entered properly");
        $sequenceErrorFound='yes';
    }
    if ($sequenceErrorFound ne 'yes')
    {
        if (length($seq1Final) <= length($seq2Final))
        {   open (SEQ1, ">$seq1File"); print SEQ1 $seq1Final; close SEQ1;
            open (SEQ2, ">$seq2File"); print SEQ2 $seq2Final; close SEQ2;
        }else
        {   open (SEQ1, ">$seq2File"); print SEQ1 $seq1Final; close SEQ1;
            open (SEQ2, ">$seq1File"); print SEQ2 $seq2Final; close SEQ2;
        }



#        my ($seqHeader1, $sequence1)  = getFASTASequence("./seq1","seq1");
#        my ($seqHeader2, $sequence2)  = getFASTASequence("./seq2","seq2");
#
#        Do NOT check the seq for protein or not
#        if (seqCheckProteinONLY(@$sequence1[0]) ne "PROTEIN")
#        {   push (@errorMessage, "The first sequence DOES NOT seem to be a protein sequence");
#        }
#        if (seqCheckProteinONLY(@$sequence2[0]) ne "PROTEIN")
#        {   push (@errorMessage, "The second sequence DOES NOT seem to be a protein sequence");
#        }
    }

}


sub print_intro
{  print "<table border='0'>
           <tr>
               <td width='100%' height='72'>
                   <p><font size='4' face='Arial'>Hello! Welcome to Junguk's Sequence <b>Fitting</b> Alignment Webtool. Here you can fit a shorter sequence into a longer sequence using the Needleman-wunsch global alignment algorithm. The scoring scheme used here is a <b>simple match/mismatch/gap</b> system. If you want to do global and local sequence alignment, please visit either of the followings: 
						<a href=\"$sequenceAlignCGIURL\"><b>Protein Sequence Aligment Webtool.</b></a> (using subsitution scoring matrixes) or 
						<a href=\"$simpleSeqAlignCGIURL\"><b>Simple Sequence Alignment Webtool.</b></a> (using a simple match/mismatch/gap scoring scheme).</font></p>
               </td>
           </tr>
       </table>
       <HR COLOR = \"#FFFF66\" SIZE = 4><BR><BR>";
}


sub print_option_form_first
{   # Display Option Alignment method & Sequence input
    print  "<form action='SeqFittingAlign.cgi' method='POST' enctype=\"multipart/form-data\">";
    print  "<table border=\"1\" width=\"960\" cellspacing=\"0\" bordercolordark=\"white\" bordercolorlight=\"black\">";
}


sub print_option_seq
{   print "     <tr align=\"center\" valign=\"top\">
                    <th width=\"240\" height=\"230\" align=\"left\" valign=\"middle\">
                        <p>&nbsp;&nbsp;<img src=\"$crossImageURL\" width=\"17\" height=\"17\" border=\"0\">    <b><font face=\"Arial Black\">SEQUENCES</font></b></p>
                        <p align=\"left\">&nbsp;&nbsp;&nbsp;Paste sequences <br> &nbsp;&nbsp;&nbsp;or upload&nbsp;files.<br>&nbsp;&nbsp;&nbsp;(Files have a <br> &nbsp;&nbsp;&nbsp;&nbsp;higher&nbsp;priority)</p>
                    </th>
                    <td width=\"822\" height=\"230\" align=\"left\" valign=\"baseline\" colspan=\"3\">
                        <b><font face=\"Arial Black\">&nbsp;Sequence#1</font></b><BR>
                        &nbsp;<textarea name=\"sequence1Input\" rows=\"5\" cols=\"49\"></textarea> &nbsp;or <input type=\"file\" name=\"seq1File\" size=\"20\">
                            <b><font face=\"Arial Black\">&nbsp;Sequence#2</font></b><BR>
                        &nbsp;<textarea name=\"sequence2Input\" rows=\"5\" cols=\"49\"></textarea> &nbsp;or <input type=\"file\" name=\"seq2File\" size=\"20\">
                    </td>
                </tr>";
}


sub print_option_seq_sample
{   my $sampleSeq1 = "ATGCAGCATGCAGC";
    my $sampleSeq2 = "ATGCAGTCAGCTTGTAGTCATGCAGC";

    print "     <tr align=\"center\" valign=\"top\">
                    <th width=\"240\" height=\"230\" align=\"left\" valign=\"middle\">
                        <p>&nbsp;&nbsp;<img src=\"$crossImageURL\" width=\"17\" height=\"17\" border=\"0\">    <b><font face=\"Arial Black\">SEQUENCES</font></b></p>
                        <p align=\"left\">&nbsp;&nbsp;&nbsp;Paste sequences <br> &nbsp;&nbsp;&nbsp;or upload&nbsp;files.<br>&nbsp;&nbsp;&nbsp;(Files have a <br> &nbsp;&nbsp;&nbsp;&nbsp;higher&nbsp;priority)</p>
                    </th>
                    <td width=\"822\" height=\"230\" align=\"left\" valign=\"baseline\" colspan=\"3\">
                        <b><font face=\"Arial Black\">&nbsp;Sequence#1</font></b><BR>
                        &nbsp;<textarea name=\"sequence1Input\" rows=\"5\" cols=\"49\">$sampleSeq1</textarea> &nbsp;or <input type=\"file\" name=\"seq1File\" size=\"20\">
                            <b><font face=\"Arial Black\">&nbsp;Sequence#2</font></b><BR>
                        &nbsp;<textarea name=\"sequence2Input\" rows=\"5\" cols=\"49\">$sampleSeq2</textarea> &nbsp;or <input type=\"file\" name=\"seq2File\" size=\"20\">
                    </td>
                </tr>";
}


sub print_option_form_last
{   print "<tr align=\"center\" valign=\"top\">
                    <th width=\"240\" height=\"40\" align=\"left\" valign=\"middle\">
                        <p>&nbsp;<img src=\"$crossImageURL\" width=\"17\" height=\"17\" border=\"0\">    <b><font face=\"Arial Black\">SCORES</font></b></p>
                    </th>
                    <td width=\"822\" height=\"40\" align=\"left\" valign=\"middle\" colspan=\"3\">
                            <font face=\"Arial\"><b>&nbsp;&nbsp;Match Score &nbsp;&nbsp;: <input type=\"text\" name=\"match\" value=\"1\" size=\"3\"></b></font>
                            <font face=\"Arial\"><b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Mismatch Penalty : <input type=\"text\" name=\"misMatch\" value=\"-1\" size=\"3\"></b></font>
                    </td>
                </tr>
                <tr align=\"center\" valign=\"top\">
                    <th width=\"240\" height=\"40\" align=\"left\" valign=\"middle\">
                        <p>&nbsp;<img src=\"$crossImageURL\" width=\"17\" height=\"17\" border=\"0\">    <b><font face=\"Arial Black\">GAP PENANTY</font></b></p>
                    </th>
                    <td width=\"822\" height=\"40\" align=\"left\" valign=\"middle\" colspan=\"3\">
                            <font face=\"Arial\"><b>&nbsp;&nbsp;Gap Opening Penalty &nbsp;&nbsp;: <input type=\"text\" name=\"gapOpen\" value=\"-2\" size=\"3\"></b></font>
                            <font face=\"Arial\"><b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Gap Extension Penalty : <input type=\"text\" name=\"gapExt\" value=\"-2\" size=\"3\"></b></font>
                    </td>
                </tr>
                <tr align=\"center\" valign=\"top\">
                    <th width=\"240\" height=\"50\" align=\"left\" valign=\"middle\">

                        <p><font face=\"Arial Black\"><b>&nbsp;</b></font><img src=\"$crossImageURL\" width=\"17\" height=\"17\" border=\"0\">  <b><font face=\"Arial Black\"> NUM OF MAXIMUM &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ALIGNMENTS</font></b></p>
                    </th>
                    <td width=\"822\" height=\"50\" align=\"left\" valign=\"middle\" colspan=\"3\">
                            <p><font face=\"Arial\"><b>&nbsp;&nbsp;Maximum&nbsp;number&nbsp;of&nbsp;alignments&nbsp;to&nbsp;display,&nbsp;if&nbsp;more than one&nbsp;:</b></font>&nbsp;<font face=\"Arial\"><b><input type=\"text\" name=\"maxAlign\" value=\"3\" size=\"3\"> </b></font></p>
                    </td>
                </tr>
                <tr align=\"center\" valign=\"top\">
                    <th width=\"240\" height=\"40\" align=\"left\" valign=\"middle\">
                        <p>&nbsp;<img src=\"$crossImageURL\" width=\"17\" height=\"17\" border=\"0\">   <b><font face=\"Arial Black\">Result via Email</font></b></p>
                    </th>
                    <td width=\"822\" height=\"40\" align=\"left\" valign=\"middle\" colspan=\"3\">
                            <p><font face=\"Courier New\">&nbsp;</font><font face=\"Arial\"><b><input type=\"checkbox\" name=\"emailCheck\" value=\"sendToEmail\"> Send&nbsp;the&nbsp;result&nbsp;to&nbsp;the&nbsp;following&nbsp;email&nbsp;address&nbsp;&nbsp;:&nbsp;&nbsp;</b></font><font face=\"Arial\"><b><input type=\"text\" name=\"resultByEmail\" size=\"45\"> </b></font></p>
                    </td>
                </tr>
            </table>
                <p><input type=\"submit\" name=\"alignNow\" value=\"ALIGN\"> <input type=\"reset\" name=\"resut\" value=\"RESET\"> <input type=\"submit\" name=\"sampleAlign\" value=\"SAMPLE_SEQ\"></p>
             </form>
          ";

}


sub print_tail
{   print "<HR COLOR = \"#FFFF66\" SIZE = 4><font size=\"3\"
          <p>Last Modified : Feb.&nbsp;27, 2007<br> 
          <br></A>Got any comment? Send an email to me<a href=\"mailto:windyskyemail-open\@yahoo.co.kr?subject=Protein Sequence Alignments\"><img src=\"$emailImageURL\" width=\"20\" height=\"20\" border=\"0\"></a></p>
          </font>";
}


sub print_weight_option
{   my ($default)=@_;
    print "<option selected value=\"".$default."\">".$default."</option>";
    for (my $i=10; $i >= 0; $i--)
    {   if ($default ne $i)
        {   print "<option value=\"$i\">$i</option>";
        }
    }
}


sub error_display
{   print "<font size=\"3\" face=\"Arial\" color=\"red\">";
    foreach ( @errorMessage)
    {   print $_."<BR>";
    }
    print "</font>";
}

