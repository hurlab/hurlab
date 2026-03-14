#!/usr/bin/perl
#****************************************************************************
#
#                BIOINFO800.003 Class Project - microRNA website
#
#                                                     Written By Junguk HUR
#                                       windyskyemail-umich <AT> yahoo.co.kr
#
#  Script: miRNA.cgi
#  Last Modified : 12/12/2006
#  Desc:  This cgi script will get microRNA ID or accession number and
#         will perform multiple sequence alignment by using clustalw and
#         RNA secondary structure prediction by ViennaRNA
#
#****************************************************************************

use CGI qw(:standard);
#use CGI::Debug;
use strict;

# Automatically update the server's current URL for cgi-bin
my $query = new CGI;
my $my_url = $query->self_url;
my @tmpSplit1 = split(/\/\//, $my_url);
my @tmpSplit2 = split(/\//, $tmpSplit1[1]);
my $tmpLocalURL = "http://$tmpSplit2[0]";


# Major variables
my $baseCGIDir = "/var/www/cgi-bin/juhur";
my $baesHTMLDir = "/var/www/html/juhur/miRNA";
my $cgiDir = "$baseCGIDir/miRNA";
my $miRBaseDir = "$baesHTMLDir/miRBase";
my $outDir = "$baesHTMLDir/outDir";
my $progDir = "$baesHTMLDir/progDir";
my $blastDir = "$baesHTMLDir/blastDir";
my $errMessage = '';
my $noErrStatus = 1;
my $localURL = "http://darwin.informatics.indiana.edu";
if ($tmpLocalURL ne "")
{   $localURL = $tmpLocalURL;
}
my $localCGIURL = $localURL."/cgi-bin/juhur/miRNA/miRNA.cgi";
my $localCGIURLWID = $localURL."/cgi-bin/juhur/miRNA/miRNA.cgi?ID=";
my $localCGIURLSingle = $localURL."/cgi-bin/juhur/miRNA/miRNAsingle.cgi";
my $localCGIURLSingleWID = $localURL."/cgi-bin/juhur/miRNA/miRNAsingle.cgi?ID=";
my $miRBaseSequenceURL = "http://microrna.sanger.ac.uk/cgi-bin/sequences/";
my $miRBaseSummaryBaseURL = $miRBaseSequenceURL."mirna_summary.pl?fam=";
my $miRBaseEntryURL = $miRBaseSequenceURL."mirna_entry.pl?acc=";
my $viennaRNAURL = "http://www.tbi.univie.ac.at/RNA/";
my $userQuery = '';        # User's original query (ID)
my $queryMIPF = '';        # miRBase protein family ID
my $queryType = '';

$localURL .= "/juhur";
my ($loadStatus, $loadMessage, 
    $ac2id, $id2ac, $mi2ac, $mi2id, $mi2spe, 
    $spe2ac, $spe2id, $spe2mi, $ac2mi, $ac2spe);
my ($hairpin_mi2fa, $hairpin_id2speID, $hairpin_speID2id, $hairpin_mi2fa_desc, 
    $mature_mi2fa, $mature_id2speID, $mature_speID2id, $mature_mi2fa_desc);
my ($mi2genomeLink, $mi2mimat1, $mi2mimat2, $mimat2mi, 
    $mimat2MirandaLink, $mimat2TargetscanLink);

# Initialize HTML page
#display_header();

# Parameter Check - user's query
if (defined param('ID')) 
{   if (param('ID') eq "")
    {   display_header();
        display_submit_form("! Your query is blank. Check your query and try again ...<BR><BR>");
    }else
    {   # Load miRBase family information
        ($loadStatus, $loadMessage, $ac2id, $id2ac, 
            $mi2ac, $mi2id, $mi2spe, $spe2ac, $spe2id, $spe2mi, 
            $ac2mi, $ac2spe) = load_family_info ("$miRBaseDir/miFam.dat");
        if (!$loadStatus)
        {   display_header();
            print "! System can't load microRNA family data file.<p>".
                  "! Contact the author. windyskyemail-open\@yahoo.co.kr <p>";
            close_html_document();
        }
        # Load miRBase family link information
        ($loadStatus, $loadMessage, $mi2genomeLink, $mi2mimat1, $mi2mimat2, $mimat2mi,
            $mimat2MirandaLink, $mimat2TargetscanLink) = load_family_mimat_info("$miRBaseDir/familyRet.info");
        if (!$loadStatus)
        {   display_header();
            print "! System can't load familyRet.info<p>".
                  "! Contact the author. windyskyemail-open\@yahoo.co.kr <p>";
            close_html_document();
        }

        # Load hairpin sequences
        ($hairpin_mi2fa, $hairpin_id2speID, $hairpin_speID2id, $hairpin_mi2fa_desc)  = load_mi2seq("$miRBaseDir/hairpin.fa");
        # id for mature stands for MIMAT
        ($mature_mi2fa, $mature_id2speID, $mature_speID2id, $mature_mi2fa_desc) = load_mi2seq("$miRBaseDir/mature.fa");
        $userQuery = param('ID');
        $userQuery =~ s/\s+//g;    # Remove any white space with user's query
        $queryType = user_id_check($userQuery);

#        print $queryType."<BR>";
        if (! $queryType)
        {   display_header();
            display_submit_form("! Your query \'$userQuery\' is not a recognizable microRNA ID ...<BR><BR>");
        }elsif ($queryType eq 'AC')
        {   $queryMIPF = uc($userQuery);
            if (not defined $$ac2id{$queryMIPF})
            {   display_header();
                display_submit_form("! Your query \'$queryMIPF\' did not match any microRNA Family AC ...<BR><BR>");
            }else
            {   auto_refresh_to_family($userQuery);
            }
        }elsif ($queryType eq 'ID')
        {   if (not defined $$id2ac{lc($userQuery)})
            {   display_header();
                display_submit_form("! Your query \'$userQuery\' did not match any microRNA Family ID ...<BR><BR>");
            }else
            {   auto_refresh_to_family($userQuery);
            }
        }elsif ($queryType eq 'MI')
        {   display_header();
            if (not defined $$mi2ac{uc($userQuery)})
            {   display_submit_form("! Your query \'$userQuery\' did not match any microRNA ID ...<BR><BR>");
            }else
            {   $queryMIPF = $$mi2ac{uc($userQuery)};
                continue_main_process($userQuery, $queryMIPF, $queryType);
            }
        }elsif ($queryType eq 'SPE')
        {   display_header();
            if (not defined $$spe2ac{lc($userQuery)})
            {   display_submit_form("! Your query \'$userQuery\' did not match any microRNA ID ...<BR><BR>");
            }else
            {   $queryMIPF = $$spe2ac{lc($userQuery)};
                continue_main_process($userQuery, $queryMIPF, $queryType);
            }
        }elsif ($queryType eq 'SPEMIMAT')
        {   $queryMIPF = $$mi2ac{$$mimat2mi{$$mature_speID2id{asterica_handling(lc($userQuery))}}};
            display_header();
            continue_main_process($userQuery, $queryMIPF, $queryType);
        }elsif ($queryType eq 'MIMAT')
        {   display_header();
            if (not defined $$mimat2mi{uc($userQuery)})
            {   display_submit_form("! Your query \'$userQuery\' did not match any microRNA ID ...<BR><BR>");
            }else
            {   $queryMIPF = $$mimat2mi{uc($userQuery)};
                continue_main_process($userQuery, $queryMIPF, $queryType);
            }
        }
    }
}else
{   display_header();
    display_submit_form();
    close_html_document();
}
exit;





# ---------------------------------------------------------------------------
#
#                           Subroutine collection
#
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Subroutins for main processing   (Modified : 12/08/2006)
# ---------------------------------------------------------------------------
sub continue_main_process
{   my $userQuery = shift;
    my $queryMIPF = shift;
    my $queryType = shift;
    #print $userQuery."<BR>";
    #print $queryMIPF."<BR>";
    #print $queryType."<BR>";
    # Retrieve hairpin sequences and mature sequences
    # The script 'process_microRNA.pl' will extract microRNA family sequences
    # (both hairpin and mature), perform clustalw multiple sequence alignment, 
    # and RNA folding secondary structure prediction
    #system ('perl process_microRNA.pl $queryMIPF');

    my $MIID = '';
    if ($queryType eq 'MI')
    {   $MIID = uc($userQuery);
    }elsif ($queryType eq 'SPE')
    {   $MIID = $$spe2mi{lc($userQuery)};
    }elsif ($queryType eq 'MIMAT')
    {   $MIID = $$mimat2mi{uc($userQuery)};
    }elsif ($queryType eq 'SPEMIMAT')
    {   $MIID = $$mimat2mi{$$mature_speID2id{asterica_handling(lc($userQuery))}};
    }
    my $MIMATID1 = $$mi2mimat1{$MIID};
    my $MIMATID2 = $$mi2mimat2{$MIID};

    
    # File names to be used
    my $hairpin_base_name = $MIID.'_hairpin';
    my $mature_base_name = $MIID.'_mature';
    my $hairpin_dot = $hairpin_base_name.'_dot';
    my $hairpin_rna = $hairpin_base_name.'_rna';

    # Save FASTA sequences into files
    open (HAIRPINSEQ, ">$outDir/$hairpin_base_name.fa");
    my $tmpSeq = $$hairpin_mi2fa{$MIID};
    $tmpSeq =~ s/\r|\n//g;
    print HAIRPINSEQ $tmpSeq;
    close HAIRPINSEQ;


    # ------------------------------------------------------------------------
    #    Display Result
    # ------------------------------------------------------------------------
    # Query Summary
    #print "User's original query is $userQuery <p> Converted miRBase family ID is $queryMIPF<p>";
    insert_section_split("Query Summary");
    query_summary_display($userQuery, $queryMIPF, $queryType);

    # Display hairpin and mature sequence
    insert_section_split("Stem-loop sequence(s)");
    display_single_sequence($$mi2spe{$MIID}, $MIID.' '.$$hairpin_mi2fa_desc{$MIID}, $$hairpin_mi2fa{$MIID});
    if ((defined $$mi2mimat1{$MIID}) && ($$mi2mimat1{$MIID} ne ""))
    {   insert_section_split("Mature sequence(s)");
        display_single_sequence($$mature_id2speID{$$mi2mimat1{$MIID}}, $$mi2mimat1{$MIID}.' '.$$mature_mi2fa_desc{$$mi2mimat1{$MIID}}, $$mature_mi2fa{$$mi2mimat1{$MIID}});
    }
    if ((defined $$mi2mimat2{$MIID}) && ($$mi2mimat2{$MIID} ne ""))
    {   display_single_sequence($$mi2mimat2{$MIID}, $$mature_mi2fa_desc{$$mi2mimat2{$MIID}}, $$mature_mi2fa{$$mi2mimat2{$MIID}});
    }

    # RNA secondary structure prediction - RNAfold
    if ($MIID ne "")
    {   RNAfold_process($MIID);
    }else
    {   print "$MIID is blank<BR>\n";
    }

    insert_section_split("RNA structure prediction - By RNAfold in <A href='$viennaRNAURL'>ViennaRNA package</A>");
    display_RNAfold_result($MIID);

    insert_section_split("Process completed for $userQuery");
    display_question_comment();

    close_html_document();
}



# ---------------------------------------------------------------------------
# Subroutins for displaying results   (Modified : 12/08/2006)
# ---------------------------------------------------------------------------
sub display_single_sequence
{   my $seqID = shift;
    my $seqDesc = shift;
    my $seq = shift;
    print "<pre>>$seqID $seqDesc\n";
    print "$seq\n";
    print "</pre>\n";
}

sub display_RNAfold_result
{   my $queryMIPFBaseName = shift;
    open (RNAFOLDOUT, "$outDir/$queryMIPFBaseName".'_hairpin_RNAfold.out');
    open_pre();
    start_font("Courier New", 2);
    while(<RNAFOLDOUT>)
    {   my $line = $_;
        $line =~ s/\r//g;
        $line =~ s/\n/<br>/g;
        print $line;
    }   close RNAFOLDOUT;
    close_font();
    close_pre();
    print "<P><A href='$localURL/miRNA/outDir/$queryMIPFBaseName"."_rna.pdf'>
           <img src='$localURL/miRNA/outDir/$queryMIPFBaseName"."_rna.jpg' border='1'></A>\n
           <A href='$localURL/miRNA/outDir/$queryMIPFBaseName"."_dot.pdf'>
           <img src='$localURL/miRNA/outDir/$queryMIPFBaseName"."_dot.jpg' border='1'></A></P>\n
           <P>Download: 
           <A href='$localURL/miRNA/outDir/$queryMIPFBaseName"."_rna.pdf'>RNAfold.pdf</A>
           <A href='$localURL/miRNA/outDir/$queryMIPFBaseName"."_dot.pdf'>RNAdot.pdf</A></P>\n";
}

sub query_summary_display
{   my $userQuery = shift;
    my $queryMIPF = shift;
    my $queryType = shift;
    my $queryTypeString = '';
    my $miID1 = '';
    my $miID2 = '';
    if ($queryType eq 'SPE')
    {   $miID1 = $$spe2mi{lc($userQuery)};
        $miID2 = $userQuery;
        $queryTypeString = 'member_ID';
    }elsif($queryType eq 'MI')
    {   $miID1 = $userQuery;
        $miID2 = $$mi2spe{uc($userQuery)};
        $queryTypeString = 'member_ID';
    }elsif(($queryType eq 'AC') || ($queryType eq 'ID'))
    {   $miID1 = '.';
        $miID2 = '.';
        $queryTypeString = 'family';
    }elsif ($queryType eq 'SPEMIMAT')
    {   $miID1 = $$mimat2mi{$$mature_speID2id{asterica_handling(lc($userQuery))}};
        $miID2 = $$mi2spe{$miID1};
        $queryTypeString = 'mature_seq_ID';
    }elsif ($queryType eq 'MIMAT')
    {   $miID1 = $$mimat2mi{uc($userQuery)};
        $miID2 = $$mi2spe{$miID1};
        $queryTypeString = 'mature_seq_ID';
    }

    my @ac2speIDs = split (/\|/, $$ac2spe{$queryMIPF});
    my $ac2speIDsCnt = scalar @ac2speIDs;

    print " <p>
            <table class='querySummary' id='querySummaryTable' border='2'>
            <tr class='titleRow'>
            <td align='center'>Query</td>
            <td align='center'>Type</td>
            <td align='center'>Family Accession</td>
            <td align='center'>Family ID</td>
            <td align='center'>miRBase ID1</td>
            <td align='center'>miRBase ID2</td>
            <td align='center'># of members</td>
            <td align='center'>Conserved Structure</td>
            </tr>
            <tbody>
            <tr class='even'>
            <td align='center'>$userQuery</td>
            <td align='center'>$queryTypeString</td>
            <td align='center'><a href='$miRBaseSummaryBaseURL$queryMIPF'>$queryMIPF</a></td>
            <td align='center'><a href='$miRBaseSummaryBaseURL$queryMIPF'>$$ac2id{$queryMIPF}</a></td>";
    if ($miID1 ne ".")
    {   print "<td align='center'><a href='$miRBaseEntryURL$miID1'>$miID1</a></td>
               <td align='center'><a href='$miRBaseEntryURL$miID2'>$miID2</a></td>";
    }else
    {   print "<td align='center'>$miID1</td>
               <td align='center'>$miID2</td>";
    }
    print " <td align='center'>$ac2speIDsCnt</td>
            <td align='center'><a href='$localCGIURL?ID=$userQuery'><b>Structure</b></a></td>
            </tr>
            </tbody>
            </table>
            </p>
           ";
}

sub insert_section_split
{   my $section_name = shift;
    my $linkname = shift;
    my $linkurl = shift;
    print "<HR COLOR = \"#FFFF66\" SIZE = 3></HR>
           <font face=\"Trebuchet MS\" color=\"#9900CC\" size=3>
           $section_name\n";
    if ((defined $linkname) && (defined $linkurl))
    {   print "<a href='$linkurl'>$linkname</a><br></font>\n";
    }else
    {   print "<br></font>\n";
    }
}



# ---------------------------------------------------------------------------
# Subroutins for checking types of user's query   (Modified : 12/08/2006)
# ---------------------------------------------------------------------------
sub user_id_check
{   my $query = shift;
    if ($query =~ /^MIPF\d+/i)
    {   return ('AC');
    }elsif ($query =~ /^MI\d+/i)
    {   return ('MI');
    }elsif ($query =~ /^MIMAT\d+/i)
    {   return ('MIMAT');
    }elsif (defined $$id2ac{lc($query)})
    {   return ('ID');
    }elsif (defined $$spe2mi{lc($query)})
    {   return ('SPE');
    }elsif (defined $$mature_speID2id{asterica_handling(lc($query))})
    {   return ('SPEMIMAT');
    }
}


# ---------------------------------------------------------------------------
# Subroutins for HTML display   (Modified : 12/08/2006)
# ---------------------------------------------------------------------------
sub display_header
{   print header, start_html ( 'microRNA Secondary Strucutre Prediction' );
    print "<body bgcolor=#C3EAE0>
          <h2 align=\"center\">
          <font face=\"Trebuchet MS\" color=\"#9900CC\">
          <span style=\"background-color:rgb(153,255,204);\">
          microRNA Secondary Strucutre Prediction
          </span>
          </font>
          </h2>
          <font face=\"Trebuchet MS\" size = 3>";
}

sub display_submit_form
{   print shift;
    print "<HR COLOR = \"#FFFF66\" SIZE = 3></HR>
           <form action='$localCGIURLSingle' method='GET'> 
           <p>Hello!! Please enter individual microRNA ID</p>
           <p>MicroRNA ID: <input type=text name=ID></p>
           <p><input type='submit' name='submit'></p>
           <HR COLOR = \"#FFFF66\" SIZE = 3></HR>
           <p>* <b>Acceptable microRNA IDs</b><br></p>
           &nbsp;Family Accession: MIPF0000001<br>
           &nbsp;Family ID: mir-17<br>
           &nbsp;Individual ID: MI0000071 or hsa-mir-17</p>
           <p>* <b>Family Accession/ID</b> will be automatically transferred to <b>miRNA.cgi</b> for family level information retrieval.</p>
           * URL for single member processing<br>
           &nbsp;&nbsp;ex) <a href=$localCGIURLSingleWID"."hsa-mir-17>$localCGIURLSingleWID"."hsa-mir-17</a><br><br>
           * URL for microRNA family secondary structure prediction<br>
           &nbsp;&nbsp;ex) <a href=$localCGIURLWID"."mir-17>$localCGIURLWID"."mir-17</a><br>
           &nbsp;&nbsp;form) <a href=$localCGIURL>$localCGIURL</a><br><br><br>";
    display_question_comment();
}

sub display_question_comment
{   print "<p>Question/Comment to 
           <a href='mailto:windyskyemail-bcs1\@yahoo.co.kr?subject=microRNA Secondary Stucture Prediction'>
           Junguk Hur<img src='$localURL/miRNA/icon/email.jpg' width='20' height='20' border='0'></a></p>";
}

sub auto_refresh_to_family
{   my $userQuery = shift;
    print "<html>
           <head>
           <title>Junguk Hur's Homepage</title>
           <META HTTP-EQUIV='Refresh'
           CONTENT='0;url=$localCGIURL?ID=$userQuery'>
           </head>
           <body></body></html>";

}

sub start_font
{   my $fontName = shift;
    my $fontSize = shift;
    print "<font face='$fontName' size=$fontSize>\n";
}

sub open_pre
{   print "<pre>\n";
}

sub close_pre
{   print "</pre>\n";
}

sub close_font
{   print "</font>";
}

sub close_html_document
{   print "</font>";
    print end_html;
}

# ---------------------------------------------------------------------------
# sub extract_rna_sequences (Modified : 12/08/2006)
# ---------------------------------------------------------------------------
# This reads miRBase family information file and load it into memroy.
# ---------------------------------------------------------------------------
sub load_family_info
{   open (FAMILY, shift) || return (0, "! can't load miRBase family data file ...");
    my ($AC, $ID, $MI, $SPE, 
        %AC2ID, %ID2AC, %MI2AC, %MI2ID, %MI2SPE, 
        %SPE2MI, %SPE2AC, %SPE2ID,         %AC2MI, %AC2SPE);
    while(<FAMILY>)
    {   my $line = $_;
        $line =~ s/\r|\n//g;
        if ($line =~ /^AC\s+(\S+)/)
        {   $AC = $1;
        }elsif ($line =~ /^ID\s+(\S+)/)
        {   $ID = $1;
            $AC2ID{$AC} = $ID;
            $ID2AC{lc($ID)} = $AC;
        }elsif ($line =~ /^MI\s+(\S+)\s+(\S+)/)
        {   $MI = uc($1);
            $SPE = lc($2);
            $MI2AC{$MI} = $AC;
            $MI2ID{$MI} = $ID;
            $MI2SPE{$MI} = $SPE;
            $SPE2AC{$SPE} = $AC;
            $SPE2ID{$SPE} = $ID;
            $SPE2MI{$SPE} = $MI;
            if (defined $AC2MI{$AC})
            {   $AC2MI{$AC} .= '|'.$MI;
                $AC2SPE{$AC} .= '|'.$SPE;
            }else
            {   $AC2MI{$AC} = $MI;
                $AC2SPE{$AC} = $SPE;
            }
        }
    }   close FAMILY;
    
    return (1, "! Success: Loading of miRBase family information ...",
            \%AC2ID, \%ID2AC, 
            \%MI2AC, \%MI2ID, \%MI2SPE, 
            \%SPE2AC, \%SPE2ID, \%SPE2MI, 
            \%AC2MI, \%AC2SPE);
}


sub load_family_mimat_info
{   open (FAMILY, shift) || return (0, "! can't load miRBase web retrieved family data file ...");
    my ($MI, %mi2genomeLink, %mi2mimat1, %mi2mimat2, %mimat2mi, %mimat2MirandaLink, %mimat2TargetscanLink);
    while(<FAMILY>)
    {   my $line = $_;
        $line =~ s/\r|\n//g;
        my @tmp = split(/\t/, $line);
        if ((defined $tmp[3]) && ($tmp[3] ne ""))
        {   $mi2genomeLink{$tmp[0]} = $tmp[3];
        }
        if ((defined $tmp[4]) && ($tmp[4] ne ""))
        {   $mi2mimat1{$tmp[0]} = $tmp[4];
            $mimat2mi{$tmp[4]} = $tmp[0];
        }else
        {   $mi2mimat1{$tmp[0]} = '';
        }
        if ((defined $tmp[5]) && ($tmp[5] ne ""))
        {   $mimat2MirandaLink{$tmp[4]} = $tmp[5];
        }else
        {   $mimat2MirandaLink{$tmp[4]} = '';
        }
        if ((defined $tmp[6]) && ($tmp[6] ne ""))
        {   $mimat2TargetscanLink{$tmp[4]} = $tmp[6];
        }else
        {   $mimat2TargetscanLink{$tmp[4]} = '';
        }
        if ((defined $tmp[7]) && ($tmp[7] ne ""))
        {   $mi2mimat2{$tmp[0]} = $tmp[7];
            $mimat2mi{$tmp[7]} = $tmp[0];
            if ((defined $tmp[8]) && ($tmp[8] ne ""))
            {   $mimat2MirandaLink{$tmp[7]} = $tmp[8];
            }else
            {   $mimat2MirandaLink{$tmp[7]} = '';
            }
            if ((defined $tmp[9]) && ($tmp[9] ne ""))
            {   $mimat2TargetscanLink{$tmp[7]} = $tmp[9];
            }else
            {   $mimat2TargetscanLink{$tmp[7]} = '';
            }
        }else
        {   $mi2mimat2{$tmp[0]} = '';
        }
    }   close FAMILY;
    return (1, "GOOD", \%mi2genomeLink, \%mi2mimat1, \%mi2mimat2, \%mimat2mi, 
            \%mimat2MirandaLink, \%mimat2TargetscanLink);
}



# ---------------------------------------------------------------------------
# Subroutins for loading miRNA sequences   (Modified : 12/08/2006)
# ---------------------------------------------------------------------------
sub load_mi2seq
{   my $fileName = shift;
    my ($ID, %id2seq, %id2speID, %speID2id, %id2seqDesc);
    open (SEQ, $fileName) || print "! Can't open $fileName<br><br>";
    while(<SEQ>)
    {   my $line = $_;
        $line =~ s/\r|\n//g;
        if ($line =~ /\>(\S+)\s+(\S+)\s+(\S.*)/)
        {   $ID = uc($2);
            $id2speID{$ID} = $1;
            $id2seqDesc{$ID} = $3;
            $speID2id{asterica_handling(lc($1))} = $ID;
        }else
        {   if (defined $id2seq{$ID})
            {   $id2seq{$ID} .= $line."\n";
            }else
            {   $id2seq{$ID} = $line."\n";
            }
        }
    }   close SEQ;
    return (\%id2seq, \%id2speID, \%speID2id, \%id2seqDesc);
}

sub asterica_handling
{   my $string = shift;
    $string =~ s/\*/\\\*/g;
    return ($string);
}

# ---------------------------------------------------------------------------
# Subroutins for alignment_RNAfold_process   (Modified : 12/13/2006)
# ---------------------------------------------------------------------------
sub RNAfold_process
{   my $MIID = shift;
    if ((! -e "$outDir/$MIID"."_hairpin_RNAfold.out") || (-s "$outDir/$MIID"."_hairpin_RNAfold.out" == 0))
    {   chdir($outDir);
        system ("$progDir/RNAfold -p -noLP < $outDir/$MIID"."_hairpin.fa > $outDir/$MIID"."_hairpin_RNAfold.out");
        my $dot_file = $MIID."_dot";
        my $rna_file = $MIID."_rna";
        my $fold_file = $MIID."_fold";
        system ("mv $outDir/dot.ps $outDir/$dot_file.ps");
        system ("mv $outDir/rna.ps $outDir/$rna_file.ps");
        system ("convert $outDir/$dot_file.ps $outDir/$dot_file.pdf");
        system ("convert $outDir/$dot_file.pdf $outDir/$dot_file.jpg");
        system ("convert $outDir/$rna_file.ps $outDir/$rna_file.pdf");
        system ("convert $outDir/$rna_file.pdf $outDir/$rna_file.jpg");
#        system ("mv $userQuery\* $outDir");
    }
}
