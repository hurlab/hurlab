#! /usr/bin/perl
#******************************************************************************
#
#                L519 Home Homework #4-3
#
#                                         Written By Junguk HUR
#                                                juhur@indiana.edu
#
#  Last Modified : Oct. 21, 2004
#  Desc:  This is the cgi script for calculating LOD scores
#         of user's input sequences from web-interface.
#
#******************************************************************************

require "LODSubs.pl";

use CGI qw(:standard);

print header, start_html ( 'LOD Score Calculator' );
#print body_html("<bgcolor="#7A9FF7" text="black" link="blue" vlink="purple" alink="red">");
print "<body bgcolor=#00CCFF>";
print h1({-align=>"center"}, 'LOD Calculator for Sequence Models');
print '<HR COLOR = "#FFFF66" SIZE = 4>';
print "<font face = \"Courier New\" size = 2 >";

if ( param('sample'))
{
    &print_form_sample();
}elsif ( param('submit'))
{
    if ( (param('seq1')) && (param('seq2')) && (param('data')) )
    {
         &print_output();
    }else
    {
         &print_form();
    }
}else{
    &print_form();
}


print "</font>";
print end_html;

sub print_intro
{
    print '<font size="3"';
    print "<BR>Hello! Welcome to Junguk's LOD Calculator.";
    print "Here you can check to which sequence model(Ms1, Ms2) ";
    print "your data sequence(d) more likely belongs. ";
    print "Calculation of LOD score of a sequence is based upon the following expression<BR>";
    print "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
    print "<i>exp</i>(<i>L </i>( <i>D&nbsp;| M<sub>s1</sub> </i>)";
    print " -&nbsp;<i>L </i>( <i>D</i>&nbsp;| <i>M</i><sub>s2</sub>))<BR>";
    print "If the log odds ratio is greater than 0, it means the data sequence ";
    print "is more like to the sequence Model#1. If it is less than 0, the data ";
    print "sequence is more like to the sequence Model#2. If it's exactly o, ";
    print "the data sequence is eqally likely from both models. <BR><BR>";
    print "Please enter three sequences (FASTA format is also accepted)&nbsp;";
    print "SEQ#1 (MODEL1), SEQ#2 (MODEL2), DATA (To be analyzed).<BR>";
    print "Both protein and nucleotide sequences are allowed ";
    print "Click 'SampleSet' button for sample sequence inputs.<BR><BR>";
    print '</font>';
    print '<HR COLOR = "#FFFF66" SIZE = 4>';
}


sub print_form
{
    print_intro();

    if ((not defined param('seq1')) && (not defined param('seq2')) &&
        (not defined param('data')) )
    {
        # If none of the three sequences, Do nothing and just continue
    }else
    {
        # If some of the three sequences are not entered
        print '<font color="red"><b>!!! Please, enter all the three sequences before submission !!!</b></font><BR>';
    }

    print "<form action='http://biokdd.informatics.indiana.edu/cgi-bin/juhur/L519/HW4/Model.cgi' method='POST'>";
    print "<b>SEQ#1 MODEL</b><BR>";
#    print "<textarea style='width: 600px; height :100px; background-color:#6F71AF; color=#FFFFFF' name='seq1' rows=5 cols=70></textarea><br>";
    print "<textarea name='seq1' rows=5 cols=80>";

    # This is used to show the previously entered sequence.
    if ( not defined param('seq1'))
    {
        print "</textarea><br>";
    }else
    {
        print param('seq1')."</textarea><br>";
    }
    print "<BR><b>SEQ#2 MODEL</b><BR>";
    print "<textarea name='seq2' rows=5 cols=80>";
    if ( not defined param('seq2'))
    {
        print "</textarea><br>";
    }else
    {
        print param('seq2')."</textarea><br>";
    }
    print "<BR><b>DATA Sequence</b><BR>";
    print "<textarea name='data' rows=5 cols=80>";
    if ( not defined param('data'))
    {
        print "</textarea><br>";
    }else
    {
        print param('data')."</textarea><br>";
    }
    print "<input type='submit' name='submit' value='Submit Query'> ";
    print "<input type='reset' name='reset'> ";
    print "<input type='submit' name='sample' value='SampleSet'>";
    print param('sample');



# Additional Information Printout

print '<BR><BR>Detailed Description : <a href="http://biokdd.informatics.indiana.edu/~juhur/L519/HW4/README.txt">README.txt</a><BR>'.
      'Class: <a href="http://biokdd.informatics.indiana.edu/~juhur/L519/L519.html">L519 Bioinformatics : Theory and Application</a><BR>'.
      'Last Modified : Oct. 20, 2004<BR>'.
      'Got any comment? Send an email to me<a href="mailto:windyskyemail-open@yahoo.co.kr?subject=An email from LOD Calculator Webpage"><img src="http://biokdd.informatics.indiana.edu/~juhur/icons/email.jpg" width="20" height="20" border="0"></a>';

}

sub print_form_sample{

    my $sampleSeq1 = ">Seq1\nGAAGCTTCTTTTACAATTGCTGATAGAATTTATGGATCCACTTTTTTC".
                     "ATAGCAACAGGATTTCATGGAATTCATGTAATAATTGGAACTTTATTTCTATTAA".
                     "TTTGCTATATTCGACATTTAAATAATCACTTTTCTAAAAATCATCACTTTGGATT".
                     "TGAAGCTGCAGCTTGATATTGACATTTTGTAGATGTAGTATGATTATTTCTTTAC".
                     "ATTTCTATTTATTGATGAGGAAATTAATTATTTATATAATATATATAGTATATTT";
    my $sampleSeq2 = ">Seq2\nTAAGTTATTATTTAGTTAATACTTTTAACAATATTATTAAGGTATTTA".
                     "AAAAATACTATTATAGTATTTAACATAGTTAAATACCTTCCTTAATACTGTTAAA".
                     "TTATATTCAATCAATACATATATAATATTATTAAAATACTTGATAAGTATTATTT".
                     "AGATATTAGACAAATACTAATTTTATATTGCTTTAATACTTAATAAATACTACTT".
                     "ATGTATTAAGTAAATATTACTGTAATACTAATAACAATATTATTACAATATGCTA";
    my $sampleData = ">data\nATGGGAGGTTTTGCCAGTTTTGTTAAGCTTACCCTTGAAGATAATTTT".
                     "GTTACCCGTGTAGAGGATGATGGAAGAGGGATACCTGTTGATATCCATCCTAAGA".
                     "CTAATCGTTCTACAGTTGAAACAGTTTTTACAGTTCTACACGCTGGCGGTAAATT".
                     "TGATAACGATAGCTATAAAGTGTCAGGTGGTTTACACGGTGTTGGTGCATCAGTT".
                     "GTTAATGCGCTTAGTTCTTCTTTTAAAGTTTGAGTTTTTCGTCAAAATAAAAAGT";

    print_intro();
    print "<form action='http://biokdd.informatics.indiana.edu/cgi-bin/juhur/L519/HW4/Model.cgi' method='POST'>";
    print "<b>SEQ#1 MODEL</b><BR>";
    print "<textarea name='seq1' rows=5 cols=80>$sampleSeq1</textarea><br>";
    print "<BR><b>SEQ#2 MODEL</b><BR>";
    print "<textarea name='seq2' rows=5 cols=80>$sampleSeq2</textarea><br>";
    print "<BR><b>DATA Sequence</b><BR>";
    print "<textarea name='data' rows=5 cols=80>$sampleData</textarea><br>";
    print "<BR>";
    print "<input type='submit' name='submit' value='Submit Query'> ";

print '<BR><BR>Detailed Description : <a href="http://biokdd.informatics.indiana.edu/~juhur/L519/HW4/README.txt">README.txt</a><BR>'.
      'Class: <a href="http://biokdd.informatics.indiana.edu/~juhur/L519/L519.html">L519 Bioinformatics : Theory and Application</a><BR>'.
      'Last Modified : Oct. 20, 2004<BR>'.
      'Got any comment? Send an email to me<a href="mailto:windyskyemail-open@yahoo.co.kr?subject=An email from LOD Calculator Webpage"><img src="http://biokdd.informatics.indiana.edu/~juhur/icons/email.jpg" width="20" height="20" border="0"></a>';


}


sub print_output{

    # Get a FASTA formatted sequence
    # If the input sequences don't have a preamble line,
    # FASTAConversion will add one for further computation


    my $homeImageLink = '<BR><p><a href="http://biokdd.informatics.indiana.edu/cgi-bin/juhur/L519/HW4/Model.cgi'.
                        '<img src="http://mypage.iu.edu/~juhur/L519/HW4/home.jpg" '.
                        'width="64" height="30" border="0"></a></p>';


    my $seq1 = FASTAConversion( 'seq1', param('seq1'));
    my $seq2 = FASTAConversion( 'seq2', param('seq2'));
    my $data = FASTAConversion( 'data', param('data'));

     # Use LOD2Calcuate to calculate LOD scores
     my $LOD2Output = LOD2Calculate ( $seq1, $seq2, $data );

     # Find any error message from LOD calculation
     my $errorType = errorCheckFromVar ( $LOD2Output  );

    # Error Handling
    if ( $errorType eq 'MissingOption' )
    {
        print '<font size="3">'.
              "Error#1. Internal error happened.<BR>".
              "Missing Option for LOD2.pl<BR>".
              "Please contact the admin with your sequences<BR>".
              '</font><BR>'.$homeImageLink;
        exit;

    }elsif ( $errorType eq 'NoFile' )
    {
       print '<font size="3">'.
             "Error#2. Internal error happened.<BR>".
             "Temporary files are missing<BR>".
             "Please contact the admin with your sequences<BR>".
              '</font><BR>'.$homeImageLink;
       exit;
    }elsif ( $errorType eq 'ErrorSequence' )
    {
       print '<font size="3">'.
             "Error#3. Errorneous Sequences Found.<BR>".
             "Please check your sequences<BR>".
             "They should be either proteins or nucleotides<BR>".
              '</font><BR>'.$homeImageLink;
       exit;
    }elsif ( $errorType eq 'SeqTypeNotMatching' )
    {
       print '<font size="3">'.
             "Error#4. Sequence Types are Not Matching.<BR>".
             "Please check your sequences<BR>".
             "They should be either ALL PROTEINs or ALL DNAs<BR>".
              '</font><BR>'.$homeImageLink;
       exit;
    }elsif ( $errorType eq 'Success' )
    {
       print '<font size="3">'.
             "<B>CONGRATULATION!!!</B><BR>".
             "All calculation succesfully completed<BR>".
             "Details are as following<BR><BR>".
              '</font>';
    }else
    {
        print '<font size="3">'.
              "Error#5. NO Calculation<BR>".
              "No calculation was computed.<BR>".
              "Please check your sequences".
              '</font><BR>'.$homeImageLink;
        exit;
    }



    # ------------------------------------------------------------
    #                Result File Content Display
    # ------------------------------------------------------------

    my @LODOutPutSplit = split ( /\n/, $LOD2Output);
    foreach my $line ( @LODOutPutSplit )
    {
        $line =~ s/\r//g;

        # If the line is divider
        if ( $line =~ /^\-\-\-\-\-/ )
        {
            print $line."<BR>";
        }elsif  ( $line eq "" )
        {
            print $line."<BR><BR>";
        }elsif ($line =~ /^\#/ )
        {
            if ( $line =~ /^(#Data sequence belongs to )(\S+\s+\S+)/ )
            {
                print '<font size="3">'.$1.'</font>'.
                      '<font size="4"><b>'.$2.'</b></font><BR>';
            }else
            {
                print '<font size="3">'.$line.'</font>'."<BR>";
            }

        }
        # If the line contains information
        elsif ( $line =~ /^[^\-]/ )
        {
            my $columnFound=0;  # For adjusting the column length
            print '<TABLE WIDTH="600">';
            print '<TR>';

            my @tmpSplit = split ( /\s/, $line );
            for ( my $column=0; $column <= $#tmpSplit; $column++ )
            {
                if ( $tmpSplit[$column] ne "" )
                {
                    if ( $columnFound < 4 )
                    {
                        print '<TD WIDTH="10%">';
                    }else
                    {
                        print '<TD WIDTH="20%">';
                    }
                    print $tmpSplit[$column].'</TD>';
                    $columnFound++;
                }
            }
            print '</TR>';
            print '</TABLE>';
        }
    }   # end of foreach my $line ( @LODOutPutSplit )

    print "<BR>".$homeImageLink;

}





