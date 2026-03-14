###############################################################################
#
#   Capstone Feedback Form Summarizing Script
#
#   Desc: This script accepts the result of evaluation 'result.txt'
#         and summarize it according the presenters
#
###############################################################################

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


while ( <FILE> )
{   chomp (my $line=$_);
    $line =~ s/\r\n//g;
    if ( $line =~ /\-\-\-/ )
    {   # New Entry Begins From Here
        $feedback_count{$presenter}++;
        $feedback_presenter{$presenter} .= 'Evaluator#'.$feedback_count{$presenter}.
                "\t$overall_quality\t$effective_organization\t$audiovisual_aids\t".
                "$clarity_presentation\t$effective_explanation\t$helpful_response\t".
                "$mastery_project\t$you_liked_most\t$suggestion\n";

        # Sum up the scores for each column
        $overall_quality_sum{$presenter} += $overall_quality;
        $effective_organization_sum{$presenter} += $effective_organization;
        $audiovisual_aids_sum{$presenter} += $audiovisual_aids;
        $clarity_presentation_sum{$presenter} += $clarity_presentation;
        $effective_explanation_sum{$presenter} += $effective_explanation;
        $helpful_response_sum{$presenter} += $helpful_response;
        $mastery_project_sum{$presenter} += $mastery_project;

        # Init for tmp values
        $overall_quality=0;          $effective_organization=0;
        $clarity_presentation=0;     $audiovisual_aids=0;
        $effective_explanation=0;    $helpful_response=0;
        $mastery_project=0;          $you_liked_most='';
        $suggestion='';              $question='';

    }elsif ( $line =~ /^\#Presenter\s+(\S.*)/ )
    {   $presenter = $1;
    }elsif ( $line =~ /^\#OveralQuality\s+(\d+)/ )
    {   $overall_quality = $1;
    }elsif ( $line =~ /^\#EffectiveOrganization\s+(\d+)/ )
    {   $effective_organization = $1;
    }elsif ( $line =~ /^\#AudiovisualAids\s+(\d+)/ )
    {   $audiovisual_aids = $1;
    }elsif ( $line =~ /^\#ClarityPresentation\s+(\d+)/ )
    {   $clarity_presentation = $1;
    }elsif ( $line =~ /^\#EffectiveExplanation\s+(\d+)/ )
    {   $effective_explanation = $1;
    }elsif ( $line =~ /^\#HelpfulResponse\s+(\d+)/ )
    {   $helpful_response = $1;
    }elsif ( $line =~ /^\#Mastery\s+(\d+)/ )
    {   $mastery_project = $1;
    }elsif ( $line =~ /^\#YouLikeMost/ )
    {   $line =~ s/\n|\r//g;
        my @tmpSplit = split ( /\t/, $line );
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

foreach ( keys %overall_quality_sum)
{   open ( RESULT , ">./EvalResult/".$_.".summary");
    print RESULT "\tOverall Quality\tEffective Organization\tAudiovisual Aids\t".
                 "Clarity of Presentation\tEffective Explanation\t".
                 "Helpful Responses\tMastery\tLiked\tSuggestion\n";
    print RESULT $feedback_presenter{$_}."\n";
    printf RESULT ("\t%.1f",($overall_quality_sum{$_}/$feedback_count{$_}));
    printf RESULT ("\t%.1f",($effective_organization_sum{$_}/$feedback_count{$_}));
    printf RESULT ("\t%.1f",($audiovisual_aids_sum{$_}/$feedback_count{$_}));
    printf RESULT ("\t%.1f",($clarity_presentation_sum{$_}/$feedback_count{$_}));
    printf RESULT ("\t%.1f",($effective_explanation_sum{$_}/$feedback_count{$_}));
    printf RESULT ("\t%.1f",($helpful_response_sum{$_}/$feedback_count{$_}));
    printf RESULT ("\t%.1f",($mastery_project_sum{$_}/$feedback_count{$_}));

}

