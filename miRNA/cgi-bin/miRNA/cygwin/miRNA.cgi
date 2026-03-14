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
my $cgiDir = "/var/www/cgi-bin/miRNA";
my $miRBaseDir = "/var/www/htdocs/miRNA/miRBase";
my $outDir = "/var/www/htdocs/miRNA/outDir";
my $progDir = "/var/www/htdocs/miRNA/progDir";
my $errMessage = '';
my $noErrStatus = 1;
my $localURL = "http://127.0.0.1";
if ($tmpLocalURL ne "")
{   $localURL = $tmpLocalURL;
}
my $webOutDir = "/miRNA/outDir";
my $localCGIURL = $localURL."/cgi-bin/miRNA/miRNA.cgi";
my $localCGIURLWID = $localURL."/cgi-bin/miRNA/miRNA.cgi?ID=";
my $localCGIURLSingle = $localURL."/cgi-bin/miRNA/miRNAsingle.cgi";
my $localCGIURLSingleWID = $localURL."/cgi-bin/miRNA/miRNAsingle.cgi?ID=";
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
my ($hairpin_mi2fa, $hairpin_id2speID, $hairpin_speID2id, $hairpin_mi2fa_desc, 
    $mature_mi2fa, $mature_id2speID, $mature_speID2id, $mature_mi2fa_desc);
my ($mi2genomeLink, $mi2mimat1, $mi2mimat2, $mimat2mi, 
    $mimat2MirandaLink, $mimat2TargetscanLink);
# Initialize HTML page
display_header();

# Parameter Check - user's query
if (defined param('ID')) 
{   if (param('ID') eq "")
    {   display_submit_form("! Your query is blank. Check your query and try again ...<BR><BR>");
    }else
    {   # Load miRBase family information
        ($loadStatus, $loadMessage, $ac2id, $id2ac, 
            $mi2ac, $mi2id, $mi2spe, $spe2ac, $spe2id, $spe2mi, 
            $ac2mi, $ac2spe) = load_family_info ("$miRBaseDir/miFam.dat");
        if (!$loadStatus)
        {   print "! System can't load microRNA family data file.<p>".
                  "! Contact the author. windyskyemail-open\@yahoo.co.kr <p>";
            last;
        }
        # Load miRBase family link information
        ($loadStatus, $loadMessage, $mi2genomeLink, $mi2mimat1, $mi2mimat2, $mimat2mi,
            $mimat2MirandaLink, $mimat2TargetscanLink) = load_family_mimat_info("$miRBaseDir/familyRet.info");
        if (!$loadStatus)
        {   print "! System can't load familyRet.info<p>".
                  "! Contact the author. windyskyemail-open\@yahoo.co.kr <p>";
            last;
        }

        # Load hairpin sequences
        ($hairpin_mi2fa, $hairpin_id2speID, $hairpin_speID2id, $hairpin_mi2fa_desc)  = load_mi2seq("$miRBaseDir/hairpin.fa");
        # id for mature stands for MIMAT
        ($mature_mi2fa, $mature_id2speID, $mature_speID2id, $mature_mi2fa_desc) = load_mi2seq("$miRBaseDir/mature.fa");
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
            {   continue_main_process($userQuery, $queryMIPF, $queryType);
            }
        }elsif ($queryType eq 'ID')
        {   if (not defined $$id2ac{lc($userQuery)})
            {   display_submit_form("! Your query \'$userQuery\' did not match any microRNA Family ID ...<BR><BR>");
            }else
            {   $queryMIPF = $$id2ac{lc($userQuery)};
                continue_main_process($userQuery, $queryMIPF, $queryType);
            }
        }elsif ($queryType eq 'MI')
        {   if (not defined $$mi2ac{uc($userQuery)})
            {   display_submit_form("! Your query \'$userQuery\' did not match any microRNA ID ...<BR><BR>");
            }else
            {   $queryMIPF = $$mi2ac{uc($userQuery)};
                continue_main_process($userQuery, $queryMIPF, $queryType);
            }
        }elsif ($queryType eq 'SPE')
        {   if (not defined $$spe2ac{lc($userQuery)})
            {   display_submit_form("! Your query \'$userQuery\' did not match any microRNA ID ...<BR><BR>");
            }else
            {   $queryMIPF = $$spe2ac{lc($userQuery)};
                continue_main_process($userQuery, $queryMIPF, $queryType);
            }
        }elsif ($queryType eq 'SPEMIMAT')
        {   $queryMIPF = $$mi2ac{$$mimat2mi{$$mature_speID2id{asterica_handling(lc($userQuery))}}};
            continue_main_process($userQuery, $queryMIPF, $queryType);
        }elsif ($queryType eq 'MIMAT')
        {   if (not defined $$mimat2mi{uc($userQuery)})
            {   display_submit_form("! Your query \'$userQuery\' did not match any microRNA ID ...<BR><BR>");
            }else
            {   $queryMIPF = $$mimat2mi{uc($userQuery)};
                continue_main_process($userQuery, $queryMIPF, $queryType);
            }
        }
    }
}else
{   display_submit_form();
}


# Finish the current HTML
print "</font>";
print end_html;
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

   
    # File names to be used
    my $hairpin_base_name = $queryMIPF.'_hairpin';
    my $mature_base_name = $queryMIPF.'_mature';
    my $hairpin_alidot = $hairpin_base_name.'_alidot';
    my $mature_alidot = $mature_base_name.'_alidot';
    my $hairpin_alirna = $hairpin_base_name.'_alirna';
    my $mature_alirna = $mature_base_name.'_alirna';
    my $hairpin_alifold_out = $hairpin_base_name.'_alifold.out';
    my $mature_alifold_out = $mature_base_name.'_alifold.out';

    # Save FASTA sequences into files
    my @ac2miIDs = split (/\|/, $$ac2mi{$queryMIPF});
    my %mimatProcessed = ();
    open (HAIRPINSEQ, ">$outDir/$hairpin_base_name.fa");
    open (MATURESEQ, ">$outDir/$mature_base_name.fa");  
    foreach my $tmpID (@ac2miIDs)
    {   my $tmpIDLC = uc($tmpID);
        #print $tmpIDLC ."<br>";
        if (defined $$hairpin_mi2fa{$tmpIDLC})
        {   print HAIRPINSEQ ">$$hairpin_id2speID{$tmpIDLC} $tmpID $$hairpin_mi2fa_desc{$tmpIDLC}\n".
                             $$hairpin_mi2fa{$tmpIDLC}."\n";
        }
        if ((defined $$mi2mimat1{$tmpIDLC}) && ($$mi2mimat1{$tmpIDLC} ne ""))
        {   if (defined $$mature_mi2fa{$$mi2mimat1{$tmpIDLC}})
            {   if (not defined $mimatProcessed{$$mi2mimat1{$tmpIDLC}})
                {   print MATURESEQ ">$$mature_id2speID{$$mi2mimat1{$tmpIDLC}} $$mi2mimat1{$tmpIDLC} $$mature_mi2fa_desc{$$mi2mimat1{$tmpIDLC}}\n".
                                     $$mature_mi2fa{$$mi2mimat1{$tmpIDLC}}."\n";
                    $mimatProcessed{$$mi2mimat1{$tmpIDLC}} = 1;
                }
            }
        }
        if ((defined $$mi2mimat2{$tmpIDLC}) && ($$mi2mimat2{$tmpIDLC} ne ""))
        {   if (defined $$mature_mi2fa{$$mi2mimat2{$tmpIDLC}})
            {   if (not defined $mimatProcessed{$$mi2mimat2{$tmpIDLC}})
                {   print MATURESEQ ">$$mature_id2speID{$$mi2mimat2{$tmpIDLC}} $$mi2mimat2{$tmpIDLC} $$mature_mi2fa_desc{$$mi2mimat2{$tmpIDLC}}\n".
                                     $$mature_mi2fa{$$mi2mimat2{$tmpIDLC}}."\n";
                    $mimatProcessed{$$mi2mimat1{$tmpIDLC}} = 1;
                }
            }
        }
    }   close HAIRPINSEQ;   close MATURESEQ;



    # ------------------------------------------------------------------------
    #    Display Result
    # ------------------------------------------------------------------------
    # Query Summary
    #print "User's original query is $userQuery <p> Converted miRBase family ID is $queryMIPF<p>";
    insert_section_split("Query Summary");
    query_summary_display($userQuery, $queryMIPF, $queryType);

    # Family members info display
    insert_section_split("microRNA family : $$ac2id{$queryMIPF} [$queryMIPF]",
                         "miRBase", $miRBaseSummaryBaseURL.$queryMIPF);
    retrieve_family_page($queryMIPF);
    
    # Multiple sequence alignment and RNA structure prediction
    insert_section_split("microRNA mature sequence alignment");
    alignment_only_process($mature_base_name);
    display_alignment($mature_base_name);

    insert_section_split("microRNA stem-loop sequence alignment");
    alignment_RNAalifold_process($hairpin_base_name);
    display_alignment($hairpin_base_name);

    # RNA secondary structure prediction - RNAalifold
    insert_section_split("Conserved Secondary Structure Prediction - By RNAalifold in <A href='$viennaRNAURL'>ViennaRNA package</A>");
    display_RNAalifold_result($hairpin_base_name);

    insert_section_split("Process completed for $userQuery");
    display_question_comment();
}



# ---------------------------------------------------------------------------
# Subroutins for alignment_RNAalifold_process   (Modified : 12/08/2006)
# ---------------------------------------------------------------------------
sub alignment_RNAalifold_process
{   my $queryMIPFBaseName = shift;
    if ((! -e "$outDir/$queryMIPFBaseName.aln") || (-s "$outDir/$queryMIPFBaseName.aln" == 0))
    {   system ("$progDir/clustalw -infile=$outDir/$queryMIPFBaseName.fa -outfile=$outDir/$queryMIPFBaseName.aln > $outDir/$queryMIPFBaseName"."_clustalw.out");
    }
    if ((! -e "$outDir/$queryMIPFBaseName"."_RNAalifold.out") || (-s "$outDir/$queryMIPFBaseName"."_RNAalifold.out" == 0))
    {   chdir($outDir);
        system ("$progDir/RNAalifold -p -noLP $outDir/$queryMIPFBaseName.aln > $outDir/$queryMIPFBaseName"."_RNAalifold.out");
        my $alidot_file = $queryMIPFBaseName."_alidot";
        my $alirna_file = $queryMIPFBaseName."_alirna";
        my $alifold_file = $queryMIPFBaseName."_alifold";
        system ("mv $outDir/alidot.ps $outDir/$alidot_file.ps");
        system ("mv $outDir/alirna.ps $outDir/$alirna_file.ps");
        system ("mv $outDir/alifold.out $outDir/$alifold_file.out");
        system ("convert $outDir/$alidot_file.ps $outDir/$alidot_file.pdf");
        system ("convert $outDir/$alidot_file.pdf $outDir/$alidot_file.jpg");
        system ("convert $outDir/$alirna_file.ps $outDir/$alirna_file.pdf");
        system ("convert $outDir/$alirna_file.pdf $outDir/$alirna_file.jpg");
        system ("perl $progDir/colorrna.pl $outDir/$alirna_file.ps $outDir/$alidot_file.ps > $outDir/$queryMIPFBaseName".'_colorrna.ps');
        system ("convert $outDir/$queryMIPFBaseName".'_colorrna.ps'." $outDir/$queryMIPFBaseName".'_colorrna.pdf');
        system ("convert $outDir/$queryMIPFBaseName".'_colorrna.pdf'." $outDir/$queryMIPFBaseName".'_colorrna.jpg');
        system ("perl $progDir/coloraln.pl -s $outDir/$alirna_file.ps $outDir/$queryMIPFBaseName.aln > $outDir/$queryMIPFBaseName"."_coloraln.ps");
        system ("convert $outDir/$queryMIPFBaseName".'_coloraln.ps'." $outDir/$queryMIPFBaseName".'_coloraln.pdf');
        system ("convert $outDir/$queryMIPFBaseName".'_coloraln.pdf'." $outDir/$queryMIPFBaseName".'_coloraln.jpg');
    }
}

sub alignment_only_process
{   my $queryMIPFBaseName = shift;
    system ("$progDir/clustalw -infile=$outDir/$queryMIPFBaseName.fa -outfile=$outDir/$queryMIPFBaseName.aln > $outDir/$queryMIPFBaseName"."_clustalw.out");
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
    if (! -e "$outDir/$queryMIPF".'_familyinfo.out')
    {   my $ua = LWP::UserAgent->new;
        $ua->timeout(30);
        my $result = $ua->get($miRBaseURL);
        my @lineContent = split(/\n/, $$result{'_content'});
        my $lineCnt = scalar @lineContent;
        my $printTag = 0;
        my $curID = '';
        my $MIRANDString = "<a href='http://microrna.sanger.ac.uk/cgi-bin/targets/v4/hit_list.pl?mirna_id=";
        my $TARGETSCANString = "<a href='http://www.targetscan.org/cgi-bin/targetscan/targetscan.cgi?mir_nc=";

        open (OUT, ">$outDir/$queryMIPF".'_familyinfo.out');
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
                    {   print OUT "<td align='center'>Genome</td>\n";
                        print OUT "<td align='center'>MIRANDA1</td>\n";
                        print OUT "<td align='center'>TARGETSCAN1</td>\n";
                        print OUT "<td align='center'>MIRANDA2</td>\n";
                        print OUT "<td align='center'>TARGETSCAN2</td>\n";
                        print OUT "<td align='center'>Structure</td>\n";
                    }else
                    {   my $tmpMIID = $$spe2mi{$curID};
                        if ((defined $$mi2genomeLink{$tmpMIID}) && ($$mi2genomeLink{$tmpMIID} ne ""))
                        {   print OUT "<td align='center'><a href='$$mi2genomeLink{$tmpMIID}'>Coordinate</a></td>\n";
                        }else
                        {   print OUT "<td align='center'>&nbsp;</td>\n";
                        }

                        my $tmpMIMAT1 = $$mi2mimat1{$tmpMIID};
                        my $tmpMIMAT2 = $$mi2mimat2{$tmpMIID};
                        if ((defined $$mimat2MirandaLink{$tmpMIMAT1}) && ($$mimat2MirandaLink{$tmpMIMAT1} ne ""))
                        {   print OUT "<td align='center'><a href='$$mimat2MirandaLink{$tmpMIMAT1}'>$$mature_id2speID{$tmpMIMAT1}</a></td>\n";
                        }else
                        {   print OUT "<td align='center'>&nbsp;</td>\n";
                        }
                        if ((defined $$mimat2TargetscanLink{$tmpMIMAT1}) && ($$mimat2TargetscanLink{$tmpMIMAT1} ne ""))
                        {   print OUT "<td align='center'><a href='$$mimat2TargetscanLink{$tmpMIMAT1}'>$$mature_id2speID{$tmpMIMAT1}</a></td>\n";
                        }else
                        {   print OUT "<td align='center'>&nbsp;</td>\n";
                        }
                        if ((defined $$mimat2MirandaLink{$tmpMIMAT2}) && ($$mimat2MirandaLink{$tmpMIMAT2} ne ""))
                        {   print OUT "<td align='center'><a href='$$mimat2MirandaLink{$tmpMIMAT2}'>$$mature_id2speID{$tmpMIMAT2}</a></td>\n";
                        }else
                        {   print OUT "<td align='center'>&nbsp;</td>\n";
                        }
                        if ((defined $$mimat2TargetscanLink{$tmpMIMAT2}) && ($$mimat2TargetscanLink{$tmpMIMAT2} ne ""))
                        {   print OUT "<td align='center'><a href='$$mimat2TargetscanLink{$tmpMIMAT2}'>$$mature_id2speID{$tmpMIMAT2}</a></td>\n";
                        }else
                        {   print OUT "<td align='center'>&nbsp;</td>\n";
                        }                        
#                        print OUT "<td align='center'>$MIRANDString$curID'>$curID</a></td>\n";
#                        print OUT "<td align='center'>$TARGETSCANString$$ac2id{$queryMIPF}'>$queryMIPF</a></td>\n";
                        print OUT "<td align='center'><a href=$localCGIURLSingleWID$curID>$curID</a></td>\n";
                        $curID = "";
                    }
                }
                print OUT $lineContent[$i]."\n";
            }
        }   close OUT;
    }
    open (FILE, "$outDir/$queryMIPF".'_familyinfo.out');
    print "<P>\n";
    while(<FILE>)
    {   my $line = $_;
        print $line;
    }   close FILE;
    print "</P>\n";
}


sub display_RNAalifold_result
{   my $queryMIPFBaseName = shift;
    # Display colorful alignment first
    open (ALIGN, "$outDir/$queryMIPFBaseName".'_RNAalifold.out');
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
    print "<P><A href='$localURL$webOutDir/$queryMIPFBaseName"."_colorrna.pdf'>
           <img src='$localURL$webOutDir/$queryMIPFBaseName"."_colorrna.jpg' border='1'></A>\n
           <A href='$localURL$webOutDir/$queryMIPFBaseName"."_alidot.pdf'>
           <img src='$localURL$webOutDir/$queryMIPFBaseName"."_alidot.jpg' border='1'></A></P>\n
           <P>Download: 
           <A href='$localURL$webOutDir/$queryMIPFBaseName"."_RNAalifold.out'>TEXT</A>
           <A href='$localURL$webOutDir/$queryMIPFBaseName"."_alifold.out'>DETAIL</A>
           <A href='$localURL$webOutDir/$queryMIPFBaseName"."_colorrna.pdf'>AliRNA.pdf</A>
           <A href='$localURL$webOutDir/$queryMIPFBaseName"."_alidot.pdf'>Alidot.pdf</A></P>\n";
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
    open (ALIGN, "$outDir/$queryMIPFBaseName".'.aln');
    open_pre();
    start_font("Courier New", 2);
    while(<ALIGN>)
    {   my $line = $_;
        if ($line !~ /\S/)
        {   print "<br>\n";
        }

        $line =~ s/\r//g;
        $line =~ s/\n/<br>/g;
        print $line;
    }   close ALIGN;
    close_font();
    close_pre();
    if (-e "$outDir/$queryMIPFBaseName"."_coloraln.pdf")
    {   print "<A href='$localURL$webOutDir/$queryMIPFBaseName"."_coloraln.pdf'>
               <img src='$localURL$webOutDir/$queryMIPFBaseName"."_coloraln.jpg' border='1'></A>";
    }
    print "<P>Download: <A href='$localURL$webOutDir/$queryMIPFBaseName.aln'>CLUSTALW</A>\n";
    print "<A href='$localURL$webOutDir/$queryMIPFBaseName.fa'>FASTA</A>\n";
    if (-e "$outDir/$queryMIPFBaseName"."_coloraln.pdf")
    {   print "<A href='$localURL$webOutDir/$queryMIPFBaseName"."_coloraln.pdf'>PDF</A></P>\n";
    }else
    {   print "</P>\n";
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
{   print header, start_html ( 'microRNA Family Secondary Strucutre Prediction' );
    print "<body bgcolor=#C3EAE0>
          <h2 align=\"center\">
          <font face=\"Trebuchet MS\" color=\"#9900CC\">
          <span style=\"background-color:rgb(153,255,204);\">
          microRNA Family Secondary Strucutre Prediction
          </span>
          </font>
          </h2>
          <font face=\"Trebuchet MS\" size = 3>";
}

sub display_submit_form
{   print shift;
    print "<HR COLOR = \"#FFFF66\" SIZE = 3></HR>
           <form action='$localCGIURL' method='GET'> 
           <p>Hello!! Please enter any form of microRNA ID</p>
           <p>MicroRNA ID: <input type=text name=ID></p>
           <p><input type='submit' name='submit'></p>
           <HR COLOR = \"#FFFF66\" SIZE = 3></HR>
           <p>* <b>Acceptable microRNA IDs</b><br></p>
           &nbsp;Family Accession: MIPF0000001<br>
           &nbsp;Family ID: mir-17<br>
           &nbsp;Individual ID: MI0000071 or hsa-mir-17</p>
           * URL for family processing<br>
           &nbsp;&nbsp;ex) <a href=$localCGIURL?ID=mir-17>$localCGIURL?ID=mir-17</a><br><br>
           * URL for individual microRNA secondary structure prediction<br>
           &nbsp;&nbsp;ex) <a href=$localCGIURLSingle?ID=hsa-mir-17>$localCGIURLSingle?ID=hsa-mir-17</a><br>
           &nbsp;&nbsp;form) <a href=$localCGIURLSingle>$localCGIURLSingle</a><br><br><br>";
    display_question_comment();
}

sub display_question_comment
{   print "<p>Question/Comment to 
           <a href='mailto:windyskyemail-bcs1\@yahoo.co.kr?subject=microRNA Secondary Stucture Prediction'>
           Junguk Hur<img src='$localURL/icon/email.jpg' width='20' height='20' border='0'></a></p>";
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