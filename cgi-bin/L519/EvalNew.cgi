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
#my $CurrentDate = `date`;


print "Come on\n\n";

print header, start_html ( 'L519 Class Mini Project Evaluation Form' );
#print body_html("<bgcolor="#7A9FF7" text="black" link="blue" vlink="purple" alink="red">");
print "<body bgcolor=\"#C3EAE0\" text=\"black\" link=\"blue\" vlink=\"purple\" alink=\"red\">";
print h1({-align=>"center"}, 'L519 Class Mini Project Evaluation Form');
print '<HR COLOR = "#FFFF66" SIZE = 4>';
#print "<font face = \"Verdana\" size = 2 >";


my $passwd='';
open ( PASS, "./passwd.txt" );
while ( <PASS> )
{   chomp ( $pass = $_);
    if ( $pass ne "" )
    {   $passwd = lc ( $pass );
    }
}
close PASS;

if ( param('evaluate'))
{
    if ( not defined param('passwd') )
    {   print '<BR><BR>Please enter the password and try again<BR><BR>';
        exit;
    }else
    {   if ( lc(param('passwd')) ne $passwd )
        {    print '<BR><BR>Your password is invalid.<BR><BR>';
             exit;
        }elsif ( ( param('yourid') eq "" ) || ( param('student') eq "" ) )
        {
             print "<BR>Please make sure you select both identity fields.<BR><BR>".
                   "Your name and the person you are evaluating.<BR>";
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
    print SAVE "#EffectiveOrganization\t".param('EffectiveOrganization')."\n";
    print SAVE "#AudiovisualAids\t".param('AudiovisualAids')."\n";
    print SAVE "#ClarityPresentation\t".param('ClarityPresentation')."\n";
    print SAVE "#EffectiveExplanation\t".param('EffectiveExplanation')."\n";
    print SAVE "#HelpfulResponse\t".param('HelpfulResponse')."\n";
    print SAVE "#Mastery\t".param('Mastery')."\n";
    print SAVE "#YouLikeMost\t".param('YouLikeMost')."\n";
    print SAVE "#Suggestion\t".param('Suggestion')."\n";
    print SAVE "#Question\t".param('Question')."\n";

    print "Following information has been stored. Thank you<BR><BR>";
    print  "#Date\t".$CurrentDate."<BR>";
    print  "#Evaluator\t".param("yourid")."<BR>";
    print  "#Presenter\t".param('student')."<BR>";
    print  "#OveralQuality\t".param('OveralQuality')."<BR>";
    print  "#EffectiveOrganization\t".param('EffectiveOrganization')."<BR>";
    print  "#AudiovisualAids\t".param('AudiovisualAids')."<BR>";
    print  "#ClarityPresentation\t".param('ClarityPresentation')."<BR>";
    print  "#EffectiveExplanation\t".param('EffectiveExplanation')."<BR>";
    print  "#HelpfulResponse\t".param('HelpfulResponse')."<BR>";
    print  "#Mastery\t".param('Mastery')."<BR>";
    print  "#YouLikeMost\t".param('YouLikeMost')."<BR>";
    print  "#Suggestion\t".param('Suggestion')."<BR>";
    print  "#Question\t".param('Question')."\n";
}









sub print_form
{
print "<form action=\"http://biokdd.informatics.indiana.edu/cgi-bin/juhur/L519FALL2005/Eval.cgi\" method=\"POST\" enctype=\"multipart/form-data\"><TABLE width=\"826\" border=\"1\">
 <TBODY>
    <TR>
        <TD width=\"816\" height=\"40\" colspan=\"2\" valign=\"middle\" bgcolor=\"#00FFCC\">
            <STRONG><font size=\"4\" face=\"Comic Sans MS\">PASSWORD &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: &nbsp;</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"><input type=\"password\" name=\"passwd\"></font>
        </TD>
    </tr>
    <TR>
        <td width=\"816\" height=\"40\" colspan=\"2\" bgcolor=\"#00FFCC\">
            <STRONG><font size=\"4\" face=\"Comic Sans MS\">Identify yourself &nbsp;&nbsp;: &nbsp;</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"><select name=\"yourid\"><option value=\"\"></option><option value=\"Gary Grumbling\">Gary Grumbling</option><option value=\"Jeffrey Mower\">Jeffrey Mower</option><option value=\"Kranthi Varala\">Kranthi Varala</option><option value=\"Yogita Mantri\">Yogita Mantri</option><option value=\"Sumit Middha\">Sumit Middha</option><option value=\"Vasanth Singan\">Vasanth Singan</option><option value=\"Lalitha Viswanath\">Lalitha Viswanath</option><option value=\"Hardik Sheth\">Hardik Sheth</option><option value=\"Gayathri Athreya\">Gayathri Athreya</option><option value=\"Anita Dalwani\">Anita Dalwani</option><option value=\"Rupali Patwardhan\">Rupali Patwardhan</option><option value=\"Divya Rao\">Divya Rao</option><option value=\"Kiran Annaiah\">Kiran Annaiah</option><option value=\"Natalya Muzinich\">Natalya Muzinich</option><option value=\"Di Ren\">Di Ren</option><option value=\"Stuart Young\">Stuart Young</option><option value=\"Troy Campbell\">Troy Campbell</option><option value=\"Murali Mohan\">Murali Mohan</option><option value=\"Haixu Tang\">Haixu Tang</option><option value=\"Sun Kim\">Sun Kim</option><option value=\"Mehmet Dalkilic\">Mehmet Dalkilic</option><option value=\"Gary Wiggins\">Gary Wiggins</option><option value=\"Junguk Hur\">Junguk Hur</option> </select>  </td>
    </tr>
    <TR>
        <td width=\"816\" height=\"34\" colspan=\"2\" bgcolor=\"#00FFCC\">
            <STRONG><font size=\"4\" face=\"Comic Sans MS\">Evaluating WHO &nbsp;&nbsp;&nbsp;: &nbsp;</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"><select name=\"student\"><option value=\"\"></option><option value=\"Gary Grumbling\">Gary Grumbling</option><option value=\"Jeffrey Mower\">Jeffrey Mower</option><option value=\"Kranthi Varala\">Kranthi Varala</option><option value=\"Yogita Mantri\">Yogita Mantri</option><option value=\"Sumit Middha\">Sumit Middha</option><option value=\"Vasanth Singan\">Vasanth Singan</option><option value=\"Lalitha Viswanath\">Lalitha Viswanath</option><option value=\"Hardik Sheth\">Hardik Sheth</option><option value=\"Gayathri Athreya\">Gayathri Athreya</option><option value=\"Anita Dalwani\">Anita Dalwani</option><option value=\"Rupali Patwardhan\">Rupali Patwardhan</option><option value=\"Divya Rao\">Divya Rao</option><option value=\"Kiran Annaiah\">Kiran Annaiah</option><option value=\"Natalya Muzinich\">Natalya Muzinich</option><option value=\"Di Ren\">Di Ren</option><option value=\"Stuart Young\">Stuart Young</option><option value=\"Troy Campbell\">Troy Campbell</option><option value=\"Murali Mohan\">Murali Mohan</option> </select></td>
    </tr>
    <TR>
        <td width=\"816\" bgcolor=\"#CCFF66\" height=\"10\" colspan=\"2\">&nbsp;</td>
    </tr>
            <TR>
                <TD width=\"353\" bgcolor=\"#CCFF66\" align=\"center\"><STRONG><font size=\"4\" face=\"Comic Sans MS\">Overal Quality</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"></font></TD>
                <TD width=\"457\" align=\"center\" valign=\"middle\" bgcolor=\"#CCFF66\"><font size=\"4\" face=\"Comic Sans MS\"><SELECT name=OveralQuality>
                      <option value=\"10\" default> 10</option><option value=\"1\">1</option><option value=\"2\">2</option><option value=\"3\">3</option><option value=\"4\">4</option><option value=\"5\">5</option><option value=\"6\">6</option><option value=\"7\">7</option><option value=\"8\">8</option><option value=\"9\">9</option><option value=\"10\">10</option></select> (BEST 10&nbsp;&nbsp;&nbsp;&nbsp;1 WORST)</td>  </tr>
            <TR>
                <TD width=\"353\" height=\"24\" bgcolor=\"#CCFF66\" align=\"center\">
                    <P><STRONG><font size=\"4\" face=\"Comic Sans MS\">Effective Organization&nbsp;</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"></font></P>
                </TD>
                <TD width=\"457\" height=\"24\" align=\"center\" valign=\"middle\" bgcolor=\"#CCFF66\"><font size=\"4\" face=\"Comic Sans MS\"><SELECT name=EffectiveOrganization>
                       <OPTION value=10 selected default>10</OPTION><option value=\"1\">1</option><option value=\"2\">2</option><option value=\"3\">3</option><option value=\"4\">4</option><option value=\"5\">5</option><option value=\"6\">6</option><option value=\"7\">7</option><option value=\"8\">8</option><option value=\"9\">9</option><option value=\"10\">10</option></select> (BEST 10&nbsp;&nbsp;&nbsp;&nbsp;1 WORST)</td>  </tr>
            <TR>
                <TD width=\"353\" bgcolor=\"#CCFF66\" align=\"center\">
                    <P><STRONG><font size=\"4\" face=\"Comic Sans MS\">Professional Appearance</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"></font></P>
                </TD>
                <TD width=\"457\" align=\"center\" valign=\"middle\" bgcolor=\"#CCFF66\"><font size=\"4\" face=\"Comic Sans MS\"><SELECT name=ProfessionalAppearance>
                        <OPTION value=10 selected default>10</OPTION><option value=\"1\">1</option><option value=\"2\">2</option><option value=\"3\">3</option><option value=\"4\">4</option><option value=\"5\">5</option><option value=\"6\">6</option><option value=\"7\">7</option><option value=\"8\">8</option><option value=\"9\">9</option><option value=\"10\">10</option></select> (BEST 10&nbsp;&nbsp;&nbsp;&nbsp;1 WORST)</td>     </tr>
            <TR>
                <TD width=\"353\" bgcolor=\"#CCFF66\" align=\"center\">
                    <P><STRONG><font size=\"4\" face=\"Comic Sans MS\">Appropriate Use of Audiovisual Aids</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"></font></P>
                </TD>
                <TD width=\"457\" align=\"center\" valign=\"middle\" bgcolor=\"#CCFF66\"><font size=\"4\" face=\"Comic Sans MS\"><SELECT name=AudiovisualAids>
                      <OPTION value=10 selected default>10</OPTION><option value=\"1\">1</option><option value=\"2\">2</option><option value=\"3\">3</option><option value=\"4\">4</option><option value=\"5\">5</option><option value=\"6\">6</option><option value=\"7\">7</option><option value=\"8\">8</option><option value=\"9\">9</option><option value=\"10\">10</option></select> (BEST 10&nbsp;&nbsp;&nbsp;&nbsp;1 WORST)</td>   </tr>
            <TR>
                <TD width=\"353\" bgcolor=\"#CCFF66\" align=\"center\">
                    <P><STRONG><font size=\"4\" face=\"Comic Sans MS\">Clarity of Presentation</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"></font></P>
                </TD>
                <TD width=\"457\" align=\"center\" valign=\"middle\" bgcolor=\"#CCFF66\"><font size=\"4\" face=\"Comic Sans MS\"><SELECT name=ClarityPresentation>
                       <OPTION value=10 selected default>10</OPTION><option value=\"1\">1</option><option value=\"2\">2</option><option value=\"3\">3</option><option value=\"4\">4</option><option value=\"5\">5</option><option value=\"6\">6</option><option value=\"7\">7</option><option value=\"8\">8</option><option value=\"9\">9</option><option value=\"10\">10</option></select> (BEST 10&nbsp;&nbsp;&nbsp;&nbsp;1 WORST)</td> </tr>
            <TR>
                <TD width=\"353\" bgcolor=\"#CCFF66\" align=\"center\">
                    <P><STRONG><font size=\"4\" face=\"Comic Sans MS\">Effective Explanation of Project</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"></font></P>
                </TD>
                <TD width=\"457\" align=\"center\" valign=\"middle\" bgcolor=\"#CCFF66\"><font size=\"4\" face=\"Comic Sans MS\"><SELECT name=EffectiveExplanation>
                     <OPTION value=10 selected default>10</OPTION><option value=\"1\">1</option><option value=\"2\">2</option><option value=\"3\">3</option><option value=\"4\">4</option><option value=\"5\">5</option><option value=\"6\">6</option><option value=\"7\">7</option><option value=\"8\">8</option><option value=\"9\">9</option><option value=\"10\">10</option></select> (BEST 10&nbsp;&nbsp;&nbsp;&nbsp;1 WORST)</td>  </tr>
            <TR>
                <TD width=\"353\" bgcolor=\"#CCFF66\" align=\"center\">
                    <P><STRONG><font size=\"4\" face=\"Comic Sans MS\">Helpful Responses to Questions</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"></font></P>
                </TD>
                <TD width=\"457\" align=\"center\" valign=\"middle\" bgcolor=\"#CCFF66\"><font size=\"4\" face=\"Comic Sans MS\"><SELECT name=HelpfulResponse>
                    <OPTION value=10 selected default>10</OPTION><option value=\"1\">1</option><option value=\"2\">2</option><option value=\"3\">3</option><option value=\"4\">4</option><option value=\"5\">5</option><option value=\"6\">6</option><option value=\"7\">7</option><option value=\"8\">8</option><option value=\"9\">9</option><option value=\"10\">10</option></select> (BEST 10&nbsp;&nbsp;&nbsp;&nbsp;1 WORST)</td>  </tr>
            <TR>
                <TD width=\"353\" height=\"24\" bgcolor=\"#CCFF66\" align=\"center\">
                    <P><STRONG><font size=\"4\" face=\"Comic Sans MS\">Mastery of Subject Matter</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"></font></P>
                </TD>
                <TD width=\"457\" height=\"24\" align=\"center\" valign=\"middle\" bgcolor=\"#CCFF66\"><font size=\"4\" face=\"Comic Sans MS\"><SELECT name=Mastery>
                    <OPTION value=10 selected default>10</OPTION><option value=\"1\">1</option><option value=\"2\">2</option><option value=\"3\">3</option><option value=\"4\">4</option><option value=\"5\">5</option><option value=\"6\">6</option><option value=\"7\">7</option><option value=\"8\">8</option><option value=\"9\">9</option><option value=\"10\">10</option></select> (BEST 10&nbsp;&nbsp;&nbsp;&nbsp;1 WORST)</td>   </tr>
            <TR>
                <TD width=\"353\" bgcolor=\"#FFFF99\" height=\"105\" align=\"center\">
                    <P><STRONG><font size=\"4\" face=\"Comic Sans MS\">What did you like most?</font></STRONG><font size=\"4\" face=\"Comic Sans MS\"></font></P>
                </TD>
                <TD width=\"457\" bgcolor=\"#FFFF99\" height=\"105\"><font size=\"4\" face=\"Comic Sans MS\"><TEXTAREA name=YouLikeMost rows=\"6\" cols=\"57\"></TEXTAREA>
           </font>
                </td>
                </tr>
                <TR>
                    <TD width=\"353\" bgcolor=\"#FFFF99\" height=\"108\" align=\"center\">

                        <P><STRONG><font size=\"4\" face=\"Comic Sans MS\">Suggestion to improve the presentation: </font></STRONG><font size=\"4\" face=\"Comic Sans MS\"></font></P>
                    </TD>
                    <TD width=\"457\" bgcolor=\"#FFFF99\" height=\"108\"><font size=\"4\" face=\"Comic Sans MS\"><TEXTAREA name=Suggestion rows=\"6\" cols=\"57\"></TEXTAREA></font>
                    </td></TR>
                    </TBODY>
                  <TR bgcolor=\"#9966CC\">
        <td width=\"353\" height=\"109\" align=\"center\">
            <p><STRONG><font size=\"4\" face=\"Comic Sans MS\"> Any Question?<br>(This will NOT be sent together with the above evaluation)</font></STRONG></p>
        </td>
        <td width=\"457\" height=\"109\"><font size=\"4\" face=\"Comic Sans MS\"><TEXTAREA name=\"Question\" rows=\"6\" cols=\"57\"></TEXTAREA></font></td>
    </TR>
</TABLE>
   <BR>
      <input type=\"reset\">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type=\"submit\" name=\"evaluate\" value=\"Evaluate\"></form>
      <HR COLOR = \"#FFFF66\" SIZE = \"4\">";
print 'Last Modified : Oct. 27, 2004<BR>'.
      'Got any comment? Send an email to me<a href="mailto:windyskyemail-open@yahoo.co.kr?subject=Capstone Evaluation Homepage"><img src="E:\WORKING\L519\HW4\steel\email.jpg" width="20" height="20" border="0"></a>';



}



sub printOption1through10
{
    for ( my $i=1; $i <= 10; $i++ )
    {
        print "<option value=\"$i\">$i</option>";
    }
    print '</select> (BEST 10&nbsp;&nbsp;&nbsp;&nbsp;1 WORST)</td>';
}
