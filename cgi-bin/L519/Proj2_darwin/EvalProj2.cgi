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

use CGI qw(:standard);
my $CurrentDate = `date`;

print header, start_html ( 'L519 Class Mini Project#2 Evaluation Form' );
#print body_html("<bgcolor="#7A9FF7" text="black" link="blue" vlink="purple" alink="red">");
print "<body bgcolor=\"#C3EAE0\" text=\"black\" link=\"blue\" vlink=\"purple\" alink=\"red\">";
print h1({-align=>"center"}, 'L519 Class Mini Project#2 Evaluation Form');
print '<HR COLOR = "#FFFF66" SIZE = 4>';
#print "<font face = \"Verdana\" size = 2 >";


my $passwd='';
my %password=();
open ( PASS, "./passwd.txt" );
while ( <PASS> )
{   chomp ( my $line = $_);
    $line =~ s/\r|\n//g;
    my @tmpSplit = split (/\t/, $line);
    $password{$tmpSplit[0]}=$tmpSplit[2];
}
close PASS;

my @class=();
open ( CLASS, "./fullMembers.txt") || die "Can't open class member\n";
while (<CLASS>)
{   chomp ($line=$_);
    $line =~ s/\r|\n//g;
    my @tmpSplit = split (/\t/, $line);
    push @class, $tmpSplit[0];
}
close CLASS;



if ( param('evaluate'))
{
    if ( not defined param('passwd') )
    {   print '<BR><BR>Please enter your password and try again<BR><BR>';
        exit;
    }else
    {   if ( ( param('yourid') eq "" ) || ( param('student') eq "" ) )
        {
             print "<BR>Please make sure you select both identity fields.<BR><BR>".
                   "Your name and the group you are evaluating.<BR>";
        }elsif ( param('passwd') ne $password{param('yourid')} )
        {
             print '<BR><BR>Your password is invalid.<BR><BR>';
             exit;
        }else
        {      print "Completed<BR>";
               print $CurrentDate;
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
{
    open ( SAVE , ">>./result.txt" );
    print SAVE "-------------------------------------------------------------\n";
    print SAVE "#Date\t".$CurrentDate;
    print SAVE "#Evaluator\t".param("yourid")."\n";
    print SAVE "#Presenter\t".param('student')."\n";
    print SAVE "#OveralQuality\t".param('OveralQuality')."\n";
    print SAVE "#YouLikeMost\t".param('YouLikeMost')."\n";
    print SAVE "#Suggestion\t".param('Suggestion')."\n";
    close SAVE;

    print "Following information has been stored. Thank you<BR><BR>";
    print  "#Date\t".$CurrentDate."<BR>";
    print  "#Evaluator\t".param("yourid")."<BR>";
    print  "#Presenter\t".param('student')."<BR>";
    print  "#OveralQuality\t".param('OveralQuality')."<BR>";
    print  "#YouLikeMost\t".param('YouLikeMost')."<BR>";
    print  "#Suggestion\t".param('Suggestion')."<BR>";
}









sub print_form
{
print "<form action=\"http://darwin.informatics.indiana.edu/cgi-bin/col/courses/L519/Eval/Proj2/EvalProj2.cgi\" method=\"POST\" enctype=\"multipart/form-data\"><TABLE width=\"826\" border=\"1\">
 <font size=\"4\" face=\"Comic Sans MS\">
 <p>This page is for evaluation of L519 group projects \#2 .<BR></p>
 <p>Please try each group's webpage before evaluation<BR><BR>
 Group1 \: <a href=\"http://mypage.iu.edu/~agutu/Ligase.htm\">http://mypage.iu.edu/~agutu/Ligase.htm</a><BR>
 Group2 \: <a href=\"http://biokdd.informatics.indiana.edu/~sboyle/project2.html\">http://biokdd.informatics.indiana.edu/~sboyle/project2.html</a><BR>
 Group3 \: <a href=\"http://biokdd.informatics.indiana.edu/~vvemulap/\">http://biokdd.informatics.indiana.edu/~vvemulap/</a><BR>
 Group4 \: <a href=\"http://mypage.iu.edu/~weic/\">http://mypage.iu.edu/~weic/</a><BR>
 Gropu5 \: <a href=\"http://biokdd.informatics.indiana.edu/cgi-bin/hgopalak/gene_family.cgi\">http://biokdd.informatics.indiana.edu/cgi-bin/hgopalak/gene_family.cgi</a><BR>
 Gropu6 \: <a href=\"http://biokdd.informatics.indiana.edu/cgi-bin/huiwang/L519/HW3.cgi\">http://biokdd.informatics.indiana.edu/cgi-bin/huiwang/L519/HW3.cgi</a><BR>
 </p>
 <p>Each group will have a 5-minute introduction to its homepage including<BR>
 &nbsp;&nbsp;1. How they obtained the data<BR>
 &nbsp;&nbsp;2. How many entries they have<BR>
 &nbsp;&nbsp;3. Any special features<BR><BR>
 </p>
 </font>
 <TBODY>
    <TR>
        <td width=\"816\" height=\"40\" colspan=\"2\" bgcolor=\"#00FFCC\">
            <STRONG><font size=\"4\" face=\"Comic Sans MS\">Identify yourself &nbsp;&nbsp;: &nbsp;</font></STRONG><font size=\"4\" face=\"Comic Sans MS\">
                 <select name=\"yourid\"><option value=\"\"></option>";

foreach (@class)
{   print '<option value='.$_.'>'.$_.'</option>';
}


print "     </select>
        </td>
    </tr>
    <TR>
        <TD width=\"816\" height=\"40\" colspan=\"2\" valign=\"middle\" bgcolor=\"#00FFCC\">
            <STRONG><font size=\"4\" face=\"Comic Sans MS\">PASSWORD &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: &nbsp;</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"><input type=\"password\" name=\"passwd\"></font>
        </TD>
    </tr>
    <TR>
        <td width=\"816\" height=\"34\" colspan=\"2\" bgcolor=\"#00FFCC\">
            <STRONG><font size=\"4\" face=\"Comic Sans MS\">Evaluating which GROUP &nbsp;&nbsp;&nbsp;: &nbsp;</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"><select name=\"student\"><option value=\"\"></option>";

for (my $i=1; $i <= 6; $i++)
{   print '<option value=Group_'.$i.'>Group_'.$i.'</option>';
}

print "</select></td>
    </tr>
    <TR>
        <td width=\"816\" bgcolor=\"#CCFF66\" height=\"10\" colspan=\"2\">&nbsp;</td>
    </tr>
            <TR>
                <TD width=\"353\" bgcolor=\"#CCFF66\" align=\"center\"><STRONG><font size=\"4\" face=\"Comic Sans MS\">Overal Quality</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"></font></TD>
                <TD width=\"457\" align=\"center\" valign=\"middle\" bgcolor=\"#CCFF66\"><font size=\"4\" face=\"Comic Sans MS\"><SELECT name=OveralQuality>
                      <option value=\"10\" default> 10</option><option value=\"1\">1</option><option value=\"2\">2</option><option value=\"3\">3</option><option value=\"4\">4</option><option value=\"5\">5</option><option value=\"6\">6</option><option value=\"7\">7</option><option value=\"8\">8</option><option value=\"9\">9</option><option value=\"10\">10</option></select> (BEST 10&nbsp;&nbsp;&nbsp;&nbsp;1 WORST)</td>  </tr>
                <TD width=\"353\" bgcolor=\"#FFFF99\" height=\"50\" align=\"center\">
                    <P><STRONG><font size=\"4\" face=\"Comic Sans MS\">What did you like most?</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"></font></P>
                </TD>
                <TD width=\"457\" bgcolor=\"#FFFF99\" height=\"50\"><font size=\"4\" face=\"Comic Sans MS\"><TEXTAREA name=YouLikeMost rows=\"6\" cols=\"57\"></TEXTAREA>
           </font>
                </td>
                </tr>
                <TR>
                    <TD width=\"353\" bgcolor=\"#FFFF99\" height=\"50\" align=\"center\">
                        <P><STRONG><font size=\"4\" face=\"Comic Sans MS\">Suggestion: </font></STRONG><font size=\"4\" face=\"Comic Sans MS\"></font></P>
                    </TD>
                    <TD width=\"457\" bgcolor=\"#FFFF99\" height=\"50\"><font size=\"4\" face=\"Comic Sans MS\"><TEXTAREA name=Suggestion rows=\"6\" cols=\"57\"></TEXTAREA></font>
                    </td></TR>
   </TBODY>
</TABLE>
   <BR>
      <input type=\"reset\">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type=\"submit\" name=\"evaluate\" value=\"Evaluate\"></form>
      <HR COLOR = \"#FFFF66\" SIZE = \"4\">";
print 'Last Modified : October 27, 2005<BR>'.
      'Got any comment? Send an email to me<a href="mailto:windyskyemail-open@yahoo.co.kr?subject=L519FALL 2005 Evluation Homepage"><img src="email.jpg" width="20" height="20" border="0"></a>';



}


