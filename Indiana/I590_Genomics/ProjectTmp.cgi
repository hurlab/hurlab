#! /usr/bin/perl
#******************************************************************************
#
#                I590 Genomics - Final Project Topic Selection
#
#                                         Written By Junguk HUR
#                                                juhur AT indiana.edu
#
#  Last Modified : Mar. 26, 2005
#  Version : 1.0
#******************************************************************************

use CGI qw(:standard);
my $CurrentDate = `date`;

print header, start_html ( 'I590 Genomics Topic Selection' );
print "<body bgcolor=#C3EAE0>
      <h1 align=\"center\"><font face=\"Arial Black\" color=\"#9900CC\"><span style=\"background-color:rgb(153,255,204);\">I590 Genomics - Project Topic Selection</span></font></h1>
      <HR COLOR = \"#FFFF66\" SIZE = 4></HR>
      <font face = \"Courier New\" size = 4>
      <strong> Server Time : ",$CurrentDate,"</strong></font>
      <HR COLOR = \"#FFFF66\" SIZE = 4></HR>
      <font face = \"Courier New\" size = 2>
      ";

my %topicNum = ( 'Cancer' => 0,
                 'Expression System' => 1,
                 'Map Based Cloning' => 2,
                 'Cell Cycle' => 3 )  ;
my %passwd=();
open ( PASS, "./Keys/passwd.txt" );
while ( <PASS> )
{   chomp ( $line = $_);
    my @tmpSplit = split (/\t/, $line);
    if ( $tmpSplit[1] ne "" )
    {   $passwd{$tmpSplit[0]}=$tmpSplit[1];
    }
}
close PASS;


open ( TOPIC, "./Keys/result.txt");
my @topics=();
my @winStudent=();
my @winTime=();

while (<TOPIC>)
{   chomp($line=$_);
    $line =~ s/\r|\n//g;
    my @tmpSplit = split (/\t/,$line);
    push @topics, $tmpSplit[0];
    push @winStudent, $tmpSplit[1];
    push @winTime, $tmpSplit[2];
}
close TOPIC;

my @topicList = ( 'Cancer', 'Expression System', 'Map Based Cloning', 'Cell Cycle' )  ;
my @students = ( 'Amit', 'Divya', 'Jim', 'Keval', 'Narmada' );

if ( param('evaluate'))
{
    if ( not defined param('passwd') )
    {   print '<font size = 4><b><BR><BR>PASSWORD is required. Go back and try again</b><BR><BR></font>';
        exit;
    }elsif ( not defined param('student'))
    {   print '<font size = 4><b><BR><BR>You must identify yourself. Go back and try again</b><BR><BR></font>';
        exit;
    }else
    {   if (param('topic') eq "")
        {   print '<font size = 4><b><BR><BR>You must select a topic. Go back and try again</b><BR><BR></font>';
            exit;
        }
        elsif ( $passwd{(param('student'))} ne param('passwd') )
        {    print '<font size = 4><b><BR><BR>Your password is invalid. Go back and try again<b><BR><BR></font>';
             exit;
        }else
        {      print "<font size=\"4\"><BR><BR>
                      Student Name : ",param('student'),"<BR>
                      Topic : ",param('topic'),"<BR>
                      Time : ",$CurrentDate,"<BR><BR>";
               #print $CurrentDate;
               save_evaluation();
               exit;
        }
    }
}else
{
   print_form();
}

  print "</font>";
  print end_html;

  exit;




sub save_evaluation
{   my $changeCheck = 'no';
    my $prevSel = 5;
    for (my $i=0; $i< 4; $i++)
    {   if ($winStudent[$i] eq param('student'))
        {   $changeCheck = 'yes';
            $prevSel = $i;
            $winStudent[$i] = 'None';
            $winTime[$i] = '';
            last;
        }
    }

    my $otherExistCheck = 'no';
    for(my $i=0; $i < $#students; $i++)
    {   if ($winStudent[$topicNum{param('topic')}] eq $students[$i])
        {   $otherExistCheck = 'yes';
            print "<font size=\"4\"><BR><BR><b>The topic you selected is not available. Please go back and choose another topic.</b><BR></font>";
            exit;
        }
    }

    open ( SAVE , ">./Keys/result.txt" );
    for (my $i=0; $i< 4; $i++)
    {   if ($i == $topicNum{param('topic')})
        {   print SAVE $topics[$i],"\t",
                       param('student'),"\t",$CurrentDate;
        }else
        {   print SAVE $topics[$i],"\t",
                       $winStudent[$i],"\t",$winTime[$i],"\n";
        }
    }
    close SAVE;
    print "<font size=\"4\"><BR><BR><b>Your selection has been saved. Click <a href=\"http://biokdd.informatics.indiana.edu/cgi-bin/juhur/I590_Genomics/Project.cgi\"><b>HERE</b></a>",
          " to confirm your selection has been secured.</b><BR></font>";

    open ( SAVE, "./Keys/result.txt");
    open ( RESULT, ">>/home2/juhur/public_html/I590_Genomics/Keys/result.txt");
    my @content=<SAVE>;
    print RESULT @content;
    close SAVE;
    close RESULT;
}

sub print_form
{



    print '<font size="4">';
    print "<p><strong>Welcome to I590 project topic selection page. Here you can check the available topics for the final project. ",
          "You may change your topic as long as the new topic is not occupied by others. Click <a href=\"http://biokdd.informatics.indiana.edu/~juhur/I590_Genomics/Project.pdf\"><b>HERE</b></a>",
          " for project description and further instruction.</strong></p>";
    print '</font>';

    current_status();

    print '<BR>';
    print "<form action='http://biokdd.informatics.indiana.edu/cgi-bin/juhur/I590_Genomics/Project.cgi' method='POST'>";


    print '<font size="4">';
    print "<p><strong>Select your topic and make sure you enter the correct password</strong></p>";
    print '</font>';
    print  "<table border=\"1\" width=\"500\">
            <tr>
                <td width=\"296\">
                    <p align=\"center\"><strong>Topic</strong></p>
                </td>
                <td width=\"188\">
                    <select name=\"topic\"><option value=\"\"></option>";
                foreach ( @topicList )
                {   print "<option value=\"".$_."\">".$_.'</option>';
                }
                print "     </td>
            </tr>
            <tr>
                <td width=\"296\">
                    <p align=\"center\"><strong>Name</strong></p>
                </td>
                <td width=\"188\">
                    <select name=\"student\"><option value=\"\"></option>";
                foreach ( @students )
                {   print "<option value=\"".$_."\">".$_.'</option>';
                }
                print "     </td>
            </tr>
            <tr>
                <td width=\"296\">
                    <p align=\"center\"><strong>Password</strong></p>
                </td>
                <td width=\"188\">
                    <input type=\"text\" name=\"passwd\">
                </td>
            </tr>
            </table><BR>";

#    print  "<input type=\"reset\">&nbsp;<input type=\"submit\" name=\"evaluate\" value=\"Submit\"></form>";

    print '<HR COLOR = "#FFFF66" SIZE = 4><BR>';
    print '<font size=3>Last Modified : Mar. 28, 2005<BR>'.
          '<A href="http://www.informatics.indiana.edu/hatang/I590.html"><b>I590 Course Homepage</b></a></font>';
}


sub current_status
{   print '<HR COLOR = \"#FFFF66\" SIZE = 4></HR>';
    print  " <table border=\"1\">
                <tr>
                    <td width=\"296\">
                        <p align=\"center\"><strong>Topic</strong></p>
                    </td>
                    <td width=\"296\">
                        <p align=\"center\"><strong>Student</strong></p>
                    </td>
                    <td width=\"350\">
                        <p align=\"center\"><strong>Timestamp</strong></p>
                    </td>
                </tr>";

    for(my $i=0; $i<= 3; $i++)
    {   print  "<tr>
                    <td align=\"center\" width=\"296\">$topics[$i]&nbsp;</td>
                    <td align=\"center\" width=\"296\">$winStudent[$i]&nbsp;</td>
                    <td align=\"center\" width=\"350\">$winTime[$i]&nbsp;</td>
                </tr>";
    }
    print     " </table> ";
    print '<HR COLOR = \"#FFFF66\" SIZE = 4></HR>';
}
