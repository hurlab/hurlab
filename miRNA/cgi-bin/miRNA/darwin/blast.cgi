#!/usr/bin/perl
#****************************************************************************
#
#                BIOINFO800.003 Class Project - microRNA website
#
#                                                     Written By Junguk HUR
#                                       windyskyemail-umich <AT> yahoo.co.kr
#
#  Script: blast.cgi
#  Last Modified : 12/12/2006
#  Desc:  This cgi script will perform BLAST search of user's sequence
#         against get microRNA ID or accession number and
#         will perform multiple sequence alignment by using clustalw and
#         RNA secondary structure prediction by ViennaRNA
#
#****************************************************************************

use CGI qw(:standard);
#use CGI::Debug;
use strict;
use LWP::UserAgent;

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
my $webOutDir = "/miRNA/outDir";
my $localCGIURL = $localURL."/cgi-bin/juhur/miRNA/miRNA.cgi";
my $localCGIURLWID = $localURL."/cgi-bin/juhur/miRNA/miRNA.cgi?ID=";
my $localCGIURLSingle = $localURL."/cgi-bin/juhur/miRNA/miRNAsingle.cgi";
my $localCGIURLSingleWID = $localURL."/cgi-bin/juhur/miRNA/miRNAsingle.cgi?ID=";
my $miRBaseSequenceURL = "http://microrna.sanger.ac.uk/cgi-bin/sequences/";
my $miRBaseSummaryBaseURL = $miRBaseSequenceURL."mirna_summary.pl?fam=";
my $miRBaseEntryURL = $miRBaseSequenceURL."mirna_entry.pl?acc=";
my $viennaRNAURL = "http://www.tbi.univie.ac.at/RNA/";
my $localCGISingleURL = $localURL."/cgi-bin/juhur/miRNA/miRNAsingle.cgi?ID=";
my $localBLASTCGIURL = $localURL."/cgi-bin/juhur/miRNA/blast.cgi";
my $viennaRNAURL = "http://www.tbi.univie.ac.at/RNA/";
my $ncbiBLASTURL = "http://www.ncbi.nlm.nih.gov/blast/Blast.cgi?";
$localURL .= "/juhur";
my $userQuery = '';        # User's original query (ID)
my $queryMIPF = '';        # miRBase protein family ID
my $queryType = '';
my $querySeq = '';
my $queryDB = '';

# Parameter Check - user's query
if (defined param('seq')) 
{   if (param('seq') eq "")
    {   # Initialize HTML page
        display_header();
        display_sequence_submit_form("<b>! Your query sequence is blank. Check your query and try again ...<BR><BR></b>");
    }else
    {   # Load miRBase family information
        if ((defined param('db')) && (lc(param('db')) eq 'nr'))
        {   # Use NCBI's BLAST search page
            # Submit the user's sequence 
            $querySeq = param('seq');
            $querySeq =~ s/\s+//g;

            my $ncbiBLASTputURL = $ncbiBLASTURL."CMD=put&DATABASE=nr&PROGRAM=blastn&QUERY=$querySeq";
            my ($BLASTStatus, $RID) = get_blast_RID($ncbiBLASTputURL);
#            $BLASTStatus = 0;
            if ($BLASTStatus)
            {   display_header();
                my $ncbiBLASTgetURL = $ncbiBLASTURL."CMD=get&ALIGNMENT_TYPE=Pairwise&SHOW_LINKOUT=yes".
                                  "&FORMAT_TYPE=HTML&DESCRIPTIONS=200&ALIGNMENTS=200&FORMAT_OBJECT=Alignment".
                                  "&RID=$RID";
                #print $ncbiBLASTgetURL;
                #autoload_blast_output($ncbiBLASTgetURL);
                print "<p>Click the following link for result.</p>\n".
                      "<p>RID: <a href='$ncbiBLASTgetURL'>$RID</a></p>\n";
            }else
            {   display_header();
                print "NCBI BLAST Search has failed.";
            }
        }elsif ((defined param('db')) && (lc(param('db')) eq 'mirna'))
        {   # Use local blastall program against miRNA
            display_header();
            $querySeq = param('seq');
            $querySeq =~ s/\s+//g;

            insert_section_split("BLAST Search against microRNA stem-loop sequences");
            print "<font size='2'>Links will open structure prediction page and miRBase page.<BR></font>";
            perform_blastall_mirna($querySeq);
            display_file_content("$outDir/UserQueryBLASTOut.html");
        }else
        {   display_header();
            display_sequence_submit_form("<b>! No target database has been specified.<br><br>Please select either nr or mirna<BR><BR></b>")
        }
    }
}else
{   display_header();
    display_sequence_submit_form();
}


# Finish the current HTML
close_html_document();











# ---------------------------------------------------------------------------
#
#                           Subroutine collection
#
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Subroutins for main processing   (Modified : 12/08/2006)
# ---------------------------------------------------------------------------
sub perform_blastall_mirna
{   my $querySeq = shift;
    if (length $querySeq > 0)
    {   open ( TMP, ">$blastDir/tmpQuerySeq.txt");
        print TMP $querySeq;
        close TMP;
    }else
    {   return ();
    }

    chdir($blastDir);
    my $blastallOutput = `$progDir/blastall -p blastn -i tmpQuerySeq.txt -d mirna -o tmpBLASTout.html -T T`;
    open (BLASTOUT, "$blastDir/tmpBLASTout.html");
    open (NEWOUT, ">$blastDir/tmpNEWBLASTout.html");

    while(<BLASTOUT>)
    {   my $line = $_;
        if ($line =~ /^(\S+)\s+(MI\d+)/)
        {   my $speID = $1;
            my $miID = $2;
            #print NEWOUT "<font color='red'><span style='background-color:yellow;'><a href='$miRBaseEntryURL$speID'>$speID</a></span></font> ".
            #             "<font color='yellow'><span style='background-color:black;'>$miID</span></font>".$';
            print NEWOUT "<a href='$localCGIURLSingleWID$miID'>$speID</a> ".
                         "<a href='$miRBaseEntryURL$miID'>$miID</a>".$';
        }elsif ($line =~ /^><a name = (\d+)><\/a>(\S+)\s+(MI\d+)/)
        {   my $posID = $1;
            my $speID = $2;
            my $miID = $3;
            #print NEWOUT "><a name = $posID></a><font color='red'><span style='background-color:yellow;'>$speID</span></font> ".
            #             "<font color='yellow'><span style='background-color:black;'>$miID</span></font>".$';
            print NEWOUT "><a name = $posID></a><a href='$localCGIURLSingleWID$miID'>$speID</a> ".
                         "<a href='$miRBaseEntryURL$miID'>$miID</a>".$';
        }else
        {   print NEWOUT $line;
        }
    }   close BLASTOUT;
    system("mv $blastDir/tmpNEWBLASTout.html $outDir/UserQueryBLASTOut.html");
}



sub display_file_content
{   my $queryMIPFBaseName = shift;
    open (FILE, $queryMIPFBaseName);
    open_pre();
    start_font("Courier New", 3);
    while(<FILE>)
    {   my $line = $_;
        if ($line !~ /\S/)
        {   print "<br>\n";
        }

        $line =~ s/\r//g;
        $line =~ s/\n/<br>/g;
        print $line;
    }   close FILE;
    close_font();
    close_pre();
}




sub display_sequence_submit_form
{   print shift;
    print "<HR COLOR = \"#FFFF66\" SIZE = 3></HR>
           <form action='$localBLASTCGIURL' method='GET'> 
           <p>Hello!! Please enter any form of microRNA ID</p>
           <p>microRNA sequence: <input type=text name=seq></p>
           <p>Target database: <select name='db' size='1'>
              <option selected value='mirna'>mirna</option>
              <option value='nr'>NCBI nr</option></p>
           <p><br><br><input type='submit' name='submit'></p>
           <HR COLOR = \"#FFFF66\" SIZE = 3></HR>
           <p>* <b>Databases</b><br><br>
                mirna: microRNA stem-loop sequences from miRBase<br>
                NCBI nr: Nucletide sequences at NCBI GenBank<br></p>
           <p>* URL for direct access<br>
           &nbsp;&nbsp;ex) <a href='$localBLASTCGIURL?seq=CGGGGUGAGGUAGUAGGUUGUGUGGUUUCAGGGCAGUGA&db=mirna&'>$localBLASTCGIURL?seq=CGGGGUGAGGUAGUAGGUUGUGUGGUUUCAGGGCAGUGA&db=mirna&</a><br><br></p>
           Question/Comment to 
           <a href='mailto:windyskyemail-bcs1\@yahoo.co.kr?subject=microRNA Secondary Stucture Prediction'>
           Junguk Hur<img src='$localURL/miRNA/icon/email.jpg' width='20' height='20' border='0'></a>";
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
# Subroutins for HTML display   (Modified : 12/08/2006)
# ---------------------------------------------------------------------------
sub display_header
{   print header, start_html ( 'microRNA BLAST Search' );
    print "<body bgcolor=#C3EAE0>
          <h2 align=\"center\">
          <font face=\"Trebuchet MS\" color=\"#9900CC\">
          <span style=\"background-color:rgb(153,255,204);\">
          microRNA BLAST Search
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
           &nbsp;&nbsp;form) <a href=$localCGIURLSingle>$localCGIURLSingle</a><br><br><br>
           Question/Comment to 
           <a href='mailto:windyskyemail-bcs1\@yahoo.co.kr?subject=microRNA Secondary Stucture Prediction'>
           Junguk Hur<img src='$localURL/miRNA/icon/email.jpg' width='20' height='20' border='0'></a>";
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


sub get_blast_RID
{   my $tmpURL = shift;
    my $ua = LWP::UserAgent->new;
    $ua->timeout(30);
    my $result = $ua->get($tmpURL);
    if ($result->is_success)
    {   my @lineContent = split(/\n/, $result->content);
        for (my $j=0; $j <= $#lineContent; $j++)
        {   if ($lineContent[$j] =~ /The request ID is <input name=.* value=\"(\S+)\"><p><\/p>/)
            {   my $RID = $1;
                return (1, $RID);
            }
        } 
        return (0, "");
    }else
    {   display_header();
        print "Failure";
        close_html_document();
        exit;
    }
}



sub autoload_blast_output
{   my $URL = shift;
    print "<html>\n".
          "<head>\n".
          "<title>BLAST Result Page<\/title>\n".
          "<META HTTP-EQUIV='Refresh'\n".
          "CONTENT='0;url=$URL'>\n".
          "<\/head>\n".
          "<body>\n".
          "<\/body>\n".
          "<\/html>";
    exit;
}