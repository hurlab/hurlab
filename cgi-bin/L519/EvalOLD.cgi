#! /usr/bin/perl
#******************************************************************************
#
#                Capstone Project Feedback or Evaluation Form
#
#                                         Written By Junguk HUR
#                                                juhur@indiana.edu
#
#  Last Modified : Nov. 11, 2004
#  Version : 1.1
#******************************************************************************

use CGI qw(:standard);
my $CurrentDate = `date`;

print header, start_html ( 'Capstone Project Presentaiton Evaluation Form' );
print "<body bgcolor=#00CCFF>";
print h1({-align=>"center"}, 'Capstone Project Presentaiton Evaluation Form');
print '<HR COLOR = "#FFFF66" SIZE = 4>';


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

    my $youlikemost_value = param('YouLikeMost');
    my $suggestion_value = param('Suggestion');
    my $question_value = param('Question');

    $youlikemost_value =~ s/\r|\n//g;
    $suggestion_value =~ s/\r|\n//g;
    $question_value =~ s/\r|\n//g;



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
    print SAVE "#YouLikeMost\t".$youlikemost_value."\n";
    print SAVE "#Suggestion\t".$suggestion_value."\n";
    print SAVE "#Question\t".$question_value."\n";
    print SAVE "-------------------------------------------------------------\n";
    
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
    print  "#YouLikeMost\t".$youlikemost_value."<BR>";
    print  "#Suggestion\t".$suggestion_value."<BR>";
    print  "#Question\t".$question_value."\n";
}









sub print_form
{

my @fullMember = ( 'Gary Grumbling', 'Jeffrey Mower', 'Kranthi Varala', 'Yogita Mantri',
'Sumit Middha', 'Vasanth Singan', 'Lalitha Viswanath', 'Hardik Sheth', 'Gayathri Athreya',
'Anita Dalwani', 'Rupali Patwardhan', 'Divya Rao', 'Kiran Annaiah', 'Natalya Muzinich',
'Di Ren', 'Stuart Young', 'Troy Campbell', 'Murali Mohan', 'Jonathan Nowacki',
'Haixu Tang', 'Sun Kim', 'Mehmet Dalkilic', 'Gary Wiggins', 'Junguk Hur' )  ;

my @students = ( 'Gary Grumbling', 'Jeffrey Mower', 'Kranthi Varala', 'Yogita Mantri',
'Sumit Middha', 'Vasanth Singan', 'Lalitha Viswanath', 'Hardik Sheth', 'Gayathri Athreya',
'Anita Dalwani', 'Rupali Patwardhan', 'Divya Rao', 'Kiran Annaiah', 'Natalya Muzinich',
'Di Ren', 'Stuart Young', 'Troy Campbell', 'Murali Mohan','Jonathan Nowacki' );

    print '<font size="4">';
    print "Hi. This is Junguk. I would like all of you to fill out the following evaluation form. ".
          "I hope this will help the presenter to understand his overall performace ".
          "and to improve his/her presentation. Please".
          " make sure you select your name too, though it will not ".
          "be shown to the presenter";
    print '</font>';

    print "<form action='http://biokdd.informatics.indiana.edu/cgi-bin/juhur/Capstone/Eval.cgi' method='POST'>".
      '<table>'.
      '<tr>'.
      '<td>'.
      '<strong> PASSWORD : </strong></td>'.
      "<td><input type=password name='passwd' value=''>".
      '</td><tr><td><hr></td><br><hr><tr><td>'.
#       '<p><font color=red> JUST SHOW WHAT I EVALUATED SO FAR:'.
#       '</font></td><td><input type="checkbox" name="whatidid" value="on" ></td>'.
       '<tr><td>'.      '<hr><p><strong> Identify yourself : </strong></td><td>'.
      '<select name="yourid"><option value=""></option>';


foreach ( @fullMember )
{
    print "<option value=\"".$_."\">".$_.'</option>';
}

print '</td>'.
      '<tr><td><p><strong>Evaluating WHO : </strong></td>'.
      "<td><select name='student'><option value=''></option>";


foreach ( @students )
{
    print "<option value=\"".$_."\">".$_.'</option>';
}

print '<tr><td><hr><br></td>'.
      '<tr><td><strong> Overal Quality : </strong></td>'.
      '<td><select name="OveralQuality">'.
      '<option value="10" default> 10</option>';
printOption1through10();

#print '<tr><td><hr><br></td>'.
print      '<tr><td><p><strong> Effective Organization of Presentation : </strong></td>'.
      '<td><select name="EffectiveOrganization">'.
      '<option value="10" default> 10</option>';
printOption1through10();

#print '<tr><td><hr><br></td>'.
print      '<tr><td><p><strong> Professional Appearance : </strong></td>'.
      '<td><select name="ProfessionalAppearance">'.
      '<option value="10" default> 10</option>';
printOption1through10();

#print '<tr><td><hr><br></td>'.
print      '<tr><td><p><strong> Appropriate Use of Audiovisual Aids : </strong></td>'.
      '<td><select name="AudiovisualAids">'.
      '<option value="10" default> 10</option>';
printOption1through10();

#print '<tr><td><hr><br></td>'.
print      '<tr><td><p><strong> Clarity of Presentation : </strong></td>'.
      '<td><select name="ClarityPresentation">'.
      '<option value="10" default> 10</option>';
printOption1through10();

#print '<tr><td><hr><br></td>'.
print      '<tr><td><p><strong> Effective Explanation of Project : </strong></td>'.
      '<td><select name="EffectiveExplanation">'.
      '<option value="10" default> 10</option>';
printOption1through10();

#print '<tr><td><hr><br></td>'.
print      '<tr><td><p><strong> Helpful Responses to Questions : </strong></td>'.
      '<td><select name="HelpfulResponse">'.
      '<option value="10" default> 10</option>';
printOption1through10();

#print '<tr><td><hr><br></td>'.
print      '<tr><td><p><strong> Mastery of Subject Matter : </strong></td>'.
      '<td><select name="Mastery">'.
      '<option value="10" default> 10</option>';
printOption1through10();


print '<tr><tr><td><p><strong>What did you like most? </strong>'.
      "</td><td><textarea rows=5 cols=50 name='YouLikeMost'></textarea>".
      '<tr><tr><td><p><strong>Suggestion to improve the presentation: '.
      "</strong></td><td><textarea rows=5 cols=50 name='Suggestion'></textarea>".
      '</table><hr>'.
      '<p><input type="reset">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'.
      '<input type="submit" name="evaluate" value="Evaluate"></form><div></font>';


print '<HR COLOR = "#FFFF66" SIZE = 4>';
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
