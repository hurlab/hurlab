#!/usr/bin/perl
#****************************************************************************
#
#                BIOINFO800.003 Class Project - microRNA website
#
#                                                     Written By Junguk HUR
#                                       windyskyemail-umich <AT> yahoo.co.kr
#
#  Script: miRNAsingle.cgi
#  Last Modified : 12/11/2006
#  Desc:  This cgi script will get microRNA ID or accession number
#         and predict RNA secondary structure by RNAfold of ViennaPackage.
#         If family ID is given, the it will be automatically 
#         transferred to miRNA.cgi which extract all family information
#         , which include multiple sequence alignment and 
#         conserved RNA secondary structure prediction. 
#
#****************************************************************************

use CGI qw(:standard);
use CGI::Debug;
use strict;

# Major variables
my $miRBaseDir = "./miRBase/";
my $outDir = "../htdocs/outDir/";
my $progDir = "./progDir/";
my $errMessage = '';
my $noErrStatus = 1;
my $localURL = "http://127.0.0.1/";
my $localCGIURL = $localURL."cgi-bin/miRNA.cgi";
my $localCGIURLWID = $localCGIURL."?ID=";
my $localCGIURLsingle = $localURL."cgi-bin/miRNAsingle.cgi";
my $localCGIURLSingleWID = $localURL."cgi-bin/miRNAsingle.cgi?ID=";
my $miRBaseSequenceURL = "http://microrna.sanger.ac.uk/cgi-bin/sequences/";
my $miRBaseSummaryBaseURL = $miRBaseSequenceURL."mirna_summary.pl?fam=";
my $miRBaseEntryURL = $miRBaseSequenceURL."mirna_entry.pl?acc=";
my $viennaRNAURL = "http://www.tbi.univie.ac.at/RNA/";
my $userQuery = '';        # User's original query (ID)
my $queryMIPF = '';        # miRBase protein family ID
my $queryType = '';
my ($loadStatus, $loadMessage, 
    $ac2id, $id2ac, $mi2ac, $mi2id, $mi2spe, 
    $spe2ac, $spe2id, $spe2mi, $ac2mi, $ac2spe);
my ($hairpin_mi2fa, $hairpin_id2miID, $hairpin_mi2fa_desc, 
    $mature_mi2fa, $mature_id2miID, $mature_mi2fa_desc);


# Parameter Check - user's query
if (defined param('ID')) 
{   if (param('ID') eq "")
    {   display_submit_form("! Your query is blank. Check your query and try again ...<BR><BR>");
    }else
    {   # Load miRBase family information
        ($loadStatus, $loadMessage, $ac2id, $id2ac, 
            $mi2ac, $mi2id, $mi2spe, $spe2ac, $spe2id, $spe2mi, 
            $ac2mi, $ac2spe) = load_family_info ("./miRBase/miFam.dat");
        if (!$loadStatus)
        {   print "! System can't load microRNA family data file.<p>".
                  "! Contact the author. windyskyemail-open\@yahoo.co.kr <p>";
            close_html_document();
            exit;
        }

        $userQuery = param('ID');
        $userQuery =~ s/\s+//g;    # Remove any white space with user's query
        $queryType = user_id_check($userQuery);

        if (! $queryType)
        {   display_submit_form("! Your query \'$userQuery\' is not a recognizable microRNA ID ...<BR><BR>");
        }elsif ($queryType eq 'AC')
        {   $queryMIPF = uc($userQuery);
            if (not defined $$ac2id{$queryMIPF})
            {   display_submit_form("! Your query \'$queryMIPF\' did not match any microRNA Family AC ...<BR><BR>");
            }else
            {   auto_refresh_to_family($userQuery);
            }
        }elsif ($queryType eq 'ID')
        {   if (not defined $$id2ac{lc($userQuery)})
            {   display_submit_form("! Your query \'$userQuery\' did not match any microRNA Family ID ...<BR><BR>");
            }else
            {   auto_refresh_to_family($userQuery);
            }
        }elsif ($queryType eq 'MI')
        {   if (not defined $$mi2ac{uc($userQuery)})
            {   display_submit_form("! Your query \'$userQuery\' did not match any microRNA ID ...<BR><BR>");
            }else
            {   continue_main_process(uc($userQuery), $queryType);
            }
        }elsif ($queryType eq 'SPE')
        {   if (not defined $$spe2ac{lc($userQuery)})
            {   display_submit_form("! Your query \'$userQuery\' did not match any microRNA ID ...<BR><BR>");
            }else
            {   continue_main_process(lc($userQuery), $queryType);
            }
        }
    }
}else
{   display_header();
    display_submit_form();
    close_html_document();
}

exit;
# Finish the current HTML



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
    my $queryType = shift;
    my $speID = '';
    my $queryMIPF = '';
    if ($queryType eq 'MI')
    {   $speID = $$mi2spe{uc($userQuery)};
        $queryMIPF = $$mi2ac{uc($userQuery)}
    }else
    {   $speID = $userQuery;
        $queryMIPF = $$spe2ac{$speID};
    }

    # Retrieve hairpin sequences and mature sequences
    # The script 'process_microRNA.pl' will extract microRNA family sequences
    # (both hairpin and mature), perform clustalw multiple sequence alignment, 
    # and RNA folding secondary structure prediction
    #system ('perl process_microRNA.pl $queryMIPF');

    # Load hairpin sequences
    ($hairpin_mi2fa, $hairpin_id2miID, $hairpin_mi2fa_desc)  = load_mi2seq("miRBase/hairpin.fa");
    ($mature_mi2fa, $mature_id2miID, $mature_mi2fa_desc) = load_mi2seq("miRBase/mature.fa");
    
    # Initialize HTML page
    display_header();

    # File names to be used
    my $hairpin_base_name = $userQuery.'_hairpin';
    my $mature_base_name = $userQuery.'_mature';
    my $hairpin_dot = $hairpin_base_name.'_dot';
    my $mature_dot = $mature_base_name.'_dot';
    my $hairpin_rna = $hairpin_base_name.'_rna';
    my $mature_rna = $mature_base_name.'_rna';

    # Save FASTA sequences into files
    open (HAIRPINSEQ, ">$outDir$hairpin_base_name.fa");
    open (MATURESEQ, ">$outDir$mature_base_name.fa");
    my $tmpSeq = $$hairpin_mi2fa{$speID};
    $tmpSeq =~ s/\r|\n//g;
    print HAIRPINSEQ $tmpSeq;
    $tmpSeq = $$mature_mi2fa{$speID};
    $tmpSeq =~ s/\r|\n//g;
    print MATURESEQ $tmpSeq;
    close HAIRPINSEQ;   close MATURESEQ;


    # ------------------------------------------------------------------------
    #    Display Result
    # ------------------------------------------------------------------------
    # Query Summary
    #print "User's original query is $userQuery <p> Converted miRBase family ID is $queryMIPF<p>";
    insert_section_split("Query Summary");
    query_summary_display($userQuery, $queryMIPF, $queryType);

    # Display hairpin and mature sequence
    insert_section_split("Stem-loop and mature sequences");
    display_single_sequence($speID, $$hairpin_mi2fa_desc{$speID}, $$hairpin_mi2fa{$speID});
    display_single_sequence($speID, $$mature_mi2fa_desc{$speID}, $$mature_mi2fa{$speID});

    # RNA secondary structure prediction - RNAfold
    if ($speID ne "")
    {   RNAfold_process($speID);
    }else
    {   print "$speID is blank<BR>\n";
    }

    insert_section_split("RNA structure prediction - By RNAfold in <A href='$viennaRNAURL'>ViennaRNA package</A>");
    display_RNAfold_result($userQuery);
    
    # Family members info display
#    insert_section_split("microRNA family : $$ac2id{$queryMIPF} [$queryMIPF]",
#                         "miRBase", $miRBaseSummaryBaseURL.$queryMIPF);
#    retrieve_family_page($queryMIPF);
#    
#    # Multiple sequence alignment and RNA structure prediction
#    insert_section_split("microRNA mature sequence alignment");
#    alignment_only_process($mature_base_name);
#    display_alignment($mature_base_name);
#
#    insert_section_split("microRNA stem-loop sequence alignment");
#    alignment_RNAalifold_process($hairpin_base_name);
#    display_alignment($hairpin_base_name);
#
#    # RNA secondary structure prediction - RNAalifold
#    insert_section_split("Conserved Secondary Structure Prediction - ViennaRNA RNAalifold");
#    display_RNAalifold_result($hairpin_base_name);
}

sub display_single_sequence
{   my $seqID = shift;
    my $seqDesc = shift;
    my $seq = shift;
    print "<pre>>$seqID $seqDesc\n";
    print "$seq\n";
    print "</pre>\n";
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
        $queryTypeString = 'member';
    }elsif($queryType eq 'MI')
    {   $miID1 = $userQuery;
        $miID2 = $$mi2spe{uc($userQuery)};
        $queryTypeString = 'member';
    }elsif(($queryType eq 'AC') || ($queryType eq 'ID'))
    {   $miID1 = '.';
        $miID2 = '.';
        $queryTypeString = 'family';
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
            <td align='center'>$queryMIPF</td>
            <td align='center'>$$ac2id{$queryMIPF}</td>
            <td align='center'><a href='$miRBaseEntryURL$miID1'>$miID1</a></td>
            <td align='center'><a href='$miRBaseEntryURL$miID2'>$miID2</a></td>";
    
    print " <td align='center'>$ac2speIDsCnt</td>
            <td align='center'><a href='$localCGIURL?ID=$userQuery'><b>Structure</b></a></td>
            </tr>
            </tbody>
            </table>
            </p>
           ";
}


sub retrieve_family_page
{   my $queryMIPF = shift;
    #use LWP::Simple;
    use LWP::UserAgent;
    my $miRBaseURL = $miRBaseSummaryBaseURL.$queryMIPF;
    if (! -e $outDir.$queryMIPF.'_familyinfo.out')
    {   my $ua = LWP::UserAgent->new;
        $ua->timeout(30);
        my $result = $ua->get($miRBaseURL);
        my @lineContent = split(/\n/, $$result{'_content'});
        my $lineCnt = scalar @lineContent;
        my $printTag = 0;
        my $curID = '';
        my $MIRANDString = "<a href='http://microrna.sanger.ac.uk/cgi-bin/targets/v4/hit_list.pl?mirna_id=";
        my $TARGETSCANString = "<a href='http://www.targetscan.org/cgi-bin/targetscan/targetscan.cgi?mir_nc=";

        open (OUT, ">".$outDir.$queryMIPF.'_familyinfo.out');
        for (my $i=0; $i < $lineCnt; $i++)
        {   #$lineContent[$i] =~ s/\r|\n//g;
            if ($lineContent[$i] =~ /<table class=\"resultTable\"/)
            {   $printTag = 1;
                substr($lineContent[$i], -1, 1) = "border='3'>\n";
            }elsif ($lineContent[$i] =~ /<\/table>/)
            {   $printTag = 0;
                print OUT $lineContent[$i]."\n";
            }

            if ($printTag)
            {   if ($lineContent[$i] =~ /^<td/)
                {   substr($lineContent[$i], 0, 3) = "<td align='center'";
                    if ($lineContent[$i] =~ /\"><\/td>$/)
                    {   $lineContent[$i] = $`.'">&nbsp;</td>';
                    }
                }
                if ($lineContent[$i] =~ /mirna_entry.pl/)
                {   $lineContent[$i] = $`.$miRBaseSequenceURL.$&.$'."\n";
                }
                if (($lineContent[$i] =~ />Fetch</) ||
                    ($lineContent[$i] =~ /<input type=\"checkbox\"/) ||
                    ($lineContent[$i] =~ /label>/))
                {   next;
                }

                # Get ID
                if ($lineContent[$i] =~ /$miRBaseSequenceURL\S+\"\>(\S+)<\/a><\/td>/)
                {   if ($curID eq "")
                    {   $curID = $1;
                    }
                }

                if ($lineContent[$i] =~ /<\/tr>/)
                {   if ($curID eq "")
                    {   print OUT "<td align='center'>MIRANDA</td>\n";
                        print OUT "<td align='center'>TARGETSCAN</td>\n";
                        print OUT "<td align='center'>Structure</td>\n";
                    }else
                    {   print OUT "<td align='center'>$MIRANDString$curID'>$curID</a></td>\n";
                        print OUT "<td align='center'>$TARGETSCANString$$ac2id{$queryMIPF}'>$queryMIPF</a></td>\n";
                        print OUT "<td align='center'><a href=$localCGIURLSingleWID$curID>$curID</a></td>\n";
                        $curID = "";
                    }
                }
                print OUT $lineContent[$i]."\n";
            }
        }   close OUT;
        

    }
    #print "<p><a href=$miRBaseSequenceURL"."mirna_summary.pl?fam=$queryMIPF>HELLO</a></p>";
    open (FILE, $outDir.$queryMIPF.'_familyinfo.out');
    print "<P>\n";
    while(<FILE>)
    {   my $line = $_;
        print $line;
    }   close FILE;
    print "</P>\n";
}


sub display_RNAfold_result
{   my $queryMIPFBaseName = shift;
    # Display colorful alignment first
    open (ALIGN, $outDir.$queryMIPFBaseName.'_hairpin_RNAfold.out');
    open_pre();
    start_font("Courier New", 2);
    while(<ALIGN>)
    {   my $line = $_;
        $line =~ s/\r//g;
        $line =~ s/\n/<br>/g;
        print $line;
    }   close ALIGN;
    close_font();
    close_pre();
    print "<P><A href='$localURL/outDir/$queryMIPFBaseName"."_rna.pdf'>
           <img src='$localURL/outDir/$queryMIPFBaseName"."_rna.jpg' border='1'></A>\n
           <A href='$localURL/outDir/$queryMIPFBaseName"."_dot.pdf'>
           <img src='$localURL/outDir/$queryMIPFBaseName"."_dot.jpg' border='1'></A></P>\n
           <P>Download: 
           <A href='$localURL/outDir/$queryMIPFBaseName"."_rna.pdf'>RNAfold.pdf</A>
           <A href='$localURL/outDir/$queryMIPFBaseName"."_dot.pdf'>RNAdot.pdf</A></P>\n";
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

sub display_alignment
{   my $queryMIPFBaseName = shift;
    open (ALIGN, $outDir.$queryMIPFBaseName.'.aln');
    open_pre();
    start_font("Courier New", 2);
    while(<ALIGN>)
    {   my $line = $_;
        $line =~ s/\r//g;
        $line =~ s/\n/<br>/g;
        print $line;
    }   close ALIGN;
    close_font();
    close_pre();
    if (-e "$outDir/$queryMIPFBaseName"."_coloraln.pdf")
    {   print "<A href='$localURL/outDir/$queryMIPFBaseName"."_coloraln.pdf'>
               <img src='$localURL/outDir/$queryMIPFBaseName"."_coloraln.jpg' border='1'></A>";
    }
    print "<P>Download: <A href='$localURL/outDir/$queryMIPFBaseName.aln'>TEXT</A>\n";
    if (-e "$outDir/$queryMIPFBaseName"."_coloraln.pdf")
    {   print "<A href='$localURL/outDir/$queryMIPFBaseName"."_coloraln.pdf'>PDF</A></P>\n";
    }else
    {   print "</P>\n";
    }
}


# ---------------------------------------------------------------------------
# Subroutins for alignment_RNAalifold_process   (Modified : 12/08/2006)
# ---------------------------------------------------------------------------
sub RNAfold_process
{   my $userQuery = shift;
    if ((! -e "$outDir/$userQuery"."_hairpin_RNAfold.out") || (-s "$outDir/$userQuery"."_hairpin_RNAfold.out" == 0))
    {   system ("$progDir/RNAfold -p -noLP < $outDir/$userQuery"."_hairpin.fa > $outDir/$userQuery"."_hairpin_RNAfold.out");
        my $dot_file = $userQuery."_dot";
        my $rna_file = $userQuery."_rna";
        my $fold_file = $userQuery."_fold";
        system ("mv dot.ps $dot_file.ps");
        system ("mv rna.ps $rna_file.ps");
        system ("convert $dot_file.ps $dot_file.pdf");
        system ("convert $dot_file.pdf $dot_file.jpg");
        system ("convert $rna_file.ps $rna_file.pdf");
        system ("convert $rna_file.pdf $rna_file.jpg");
        system ("mv $userQuery\* $outDir");
    }
}





# ---------------------------------------------------------------------------
# Subroutins for checking types of user's query   (Modified : 12/08/2006)
# ---------------------------------------------------------------------------
sub user_id_check
{   my $query = shift;
    if ($query =~ /^MIPF\d+/i)
    {   return ('AC');
    }elsif ($query =~ /^\w{3}-\d+/i)
    {   return ('ID');
    }elsif ($query =~ /^MI\d+/i)
    {   return ('MI');
    }elsif ($query =~ /^\w{3,4}\-\w{3}/i)
    {   return ('SPE');
    }else
    {   return (0);
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
           <form action='$localCGIURLsingle' method='GET'> 
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
           &nbsp;&nbsp;form) <a href=$localCGIURL>$localCGIURL</a><br><br><br>
           Question/Comment to 
           <a href='mailto:windyskyemail-bcs1\@yahoo.co.kr?subject=microRNA Secondary Stucture Prediction'>
           Junguk Hur<img src='$localURL/icon/email.jpg' width='20' height='20' border='0'></a>";
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
{   open (FAMILY, $miRBaseDir."miFam.dat") || return (0, "! can't load miRBase family data file ...");
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
            $ID2AC{$ID} = $AC;
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

# ---------------------------------------------------------------------------
# Subroutins for loading miRNA sequences   (Modified : 12/08/2006)
# ---------------------------------------------------------------------------
sub load_mi2seq
{   my $fileName = shift;
    my ($ID, %id2seq, %id2miID, %id2seqDesc);
    open (SEQ, $fileName) || print "! Can't open $fileName<br><br>";
    while(<SEQ>)
    {   my $line = $_;
        $line =~ s/\r|\n//g;
        if ($line =~ /\>(\S+)\s+(\S+)\s+(\S.*)/)
        {   $ID = lc($1);
            $id2miID{$ID} = $2;
            $id2seqDesc{$ID} = $3;
        }else
        {   if (defined $id2seq{$ID})
            {   $id2seq{$ID} .= $line."\n";
            }else
            {   $id2seq{$ID} = $line."\n";
            }
        }
    }   close SEQ;
    return (\%id2seq, \%id2miID, \%id2seqDesc);
}