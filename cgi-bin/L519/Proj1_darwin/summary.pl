###############################################################################
#
#   Capstone Feedback Form Summarizing Script
#
#   Desc: This script accepts the result of evaluation 'result.txt'
#         and summarize it according the presenters
#
###############################################################################

mkdir ("EvalResult") || print"";
open (FULL, "fullMembers.txt");
while(<FULL>)
{   $line=$_;
    $line=~ s/\r|\n//g;
    @tmp=split(/\t/,$line);
    $GroupByMember{$tmp[0]}=$tmp[2];
}   close FULL;


open ( FILE, "./result.txt" );

my %feedback_presenter=();
my %feedback_count=();
my $presenter=();
my $overall_quality=0;         my %overall_quality_sum=();
my $effective_organization=0;  my %effective_organization_sum = ();
my $audiovisual_aids=0;        my %audiovisual_aids_sum = ();
my $clarity_presentation=0;    my %clarity_presentation_sum = ();
my $effective_explanation=0;   my %effective_explanation_sum = ();
my $helpful_response=0;        my %helpful_response_sum = ();
my $mastery_project=0;         my %mastery_project_sum = ();
my $you_liked_most='';         my %you_liked_most_sum = ();
my $suggestion='';             my %suggestion_sum = ();
my $question='';               my %question_sum = ();
my $evaluator='';
my %presenterCheck=();

while ( <FILE> )
{   chomp (my $line=$_);
    $line =~ s/\r\n//g;

    if ($line eq "")
    {   next;
    }elsif ( $line =~ /\-\-\-/ )
    {   # New Entry Begins From Here
        if (($evaluator ne "") && ( $GroupByMember{$evaluator} ne $presenter))
        {   $feedback_count{$presenter}++;
            $feedback_presenter{$presenter} .=
                'Evaluator#'.$feedback_count{$presenter}.
                "\t$overall_quality\t$you_liked_most\t$suggestion\n";
            # Sum up the scores for each column
            $overall_quality_sum{$presenter} += $overall_quality;
        }
        # Init for tmp values
        $overall_quality=0;          $you_liked_most='';
        $suggestion='';              $evaluator='';
        $presenter='';
    }elsif ( $line =~ /^\#Evaluator\s+(\S.*)/ )
    {   $evaluator = $1;
    }elsif ( $line =~ /^\#Presenter\s+(\S.*)/ )
    {   $presenter = $1;
    }elsif ( $line =~ /^\#OveralQuality\s+(\d+)/ )
    {   $overall_quality = $1;
    }elsif ( $line =~ /^\#YouLikeMost/ )
    {   my @tmpSplit = split ( /\t/, $line );
        if ( $#tmpSplit == 0 )
        {   $you_liked_most = "__";
        }else
        {   $you_liked_most = $tmpSplit[$#tmpSplit];
        }
    }elsif ( $line =~ /^\#Suggestion/ )
    {   $line =~ s/\n|\r//g;
        my @tmpSplit = split ( /\t/, $line );
        if ( $#tmpSplit == 0 )
        {   $suggestion = "__";
        }else
        {   $suggestion = $tmpSplit[$#tmpSplit];
        }
    }
}
close FILE;

foreach ( keys %feedback_count)
{   open ( RESULT , ">./EvalResult/".$_.".summary");
    print RESULT "\tOverall Quality\tLiked\tSuggestion\n";
    print RESULT $feedback_presenter{$_}."\n";
    printf RESULT ("\t%.1f",($overall_quality_sum{$_}/$feedback_count{$_}));
}