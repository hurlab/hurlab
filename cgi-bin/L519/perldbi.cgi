#!/usr/bin/perl

######################################################################
# Copyright 2004, James Costello.  All rights reserved.
# Original author: James Costello
# Last modified by Rupali Patwardhan, 18 November 2004.
# 
# This is written to illustrate DBI for L519: Bioinformatics (Spring and Fall 2004).
######################################################################

use DBI;
use CGI;

######################################################################
##################### Variable Declarations ##########################
######################################################################

####
# This is where you can find the perldoc for the DBI
# or if you are not viewing this in html:  http://search.cpan.org/~timb/DBI/DBI.pm
####

# create a new instance of CGI
  my $cgi = new CGI;

# variables that will be used by the DBI
  my $DB        = "DBI:mysql:juhurdb";      # data source name (database) 
  my $username  = "juhur";                     
  my $password  = "L519pass";
  my $db_table  = "test";              

# uses a global call to get the path and name of this program
  my $program = $ENV{"SCRIPT_NAME"};

######################################################################
########################### CGI and DBI ##############################
######################################################################

# In order to start use any of the DBI functionality, you must create a database
# connection and store that connection in the database handle object ($dbh).
  my $dbh = DBI->connect($DB, $username, $password, {PrintError => 0})
     || die "Could not open database, ", $DBI::errstr;


# simply the start of the html
  print $cgi->header;
  print $cgi->start_html(-title=>'Database Connectivity Example');

  print $cgi->h2('Database Connectivity Example');

print "<a href='http://biokdd.informatics.indiana.edu/rpatward/teaching/L519/Lab9/perldbi.txt'> Source Code </a>";

# if there were parameters entered, then process them and hand them off to 
# the database subs, else print the form to enter the values.
  if ($cgi->param) {
      my $name = $cgi->param('name');
      my $number = $cgi->param('number');
      my $color = $cgi->param('color');
      my $search = $cgi->param('search');
      &store_values($name, $number, $color);
      &retrieve_values($search);
  } else {
      &print_form();
  }

  print $cgi->end_html;

# must close the database connection
  $dbh->disconnect;



######################################################################
########################## Subroutines ###############################
######################################################################

# simply prints the form that will be used to submit the values
  sub print_form {
      print "<form action=\"$program\"  method=POST>";
      print "<h3>The following fields will be entered into the database if they have values when the submission button is hit</h3>";
      print "Please enter a name:<br>";
      print "<input type=\"text\" name=\"name\"><br>";
      print "Please enter an id:<br>";
      print "<input type=\"text\" name=\"number\"><br>";
      print "Please enter your hair color:<br>";
      print "<input type=\"text\" name=\"color\"><br>";
      print "<hr>";
      print "<h3>The following field is a search of the database and will return you all the information found with in the tuples that matches the search terms</h3>";
      print "Please enter a name to be searched for in the database<br>";
      print "<input type\"text\" name=\"search\">";
      print "<hr><input type=\"submit\" value=\"Submit\">";
      print "<input type=\"reset\" value=\"reset\">";
      print "</form>";
  }


# will store the input values to the database and print out what the values were
  sub store_values {
      local($name, $number, $color) = @_;

      if ($name && $number && $color) {
          ####
          # First, you must create a query
          ####
          my $insert = "INSERT INTO $db_table VALUES('$name', $number, '$color')";
          ####
          # Next, you must prepare the query for later use in the form of a statement handle object
          ####
          my $sth = $dbh->prepare($insert) || die "Query not prepared";
          #### Next, execute the query.  This query will remain open until the "finish" method is called.  
          # As we will see later, the query is kept open for retrieval purposes.
          ####
          $sth->execute || die "Query not executed";
          ####
          # Lastly, tell the statement handle object that you are done with it
          ####
          $sth->finish;

          print "The following terms were entered into the database <font size=5><b>$db_table</b></font><br>";
          print "Name = $name<br>";
          print "ID = $number<br>";
          print "Hair Color = $color<hr>";
      }
  }          


  sub retrieve_values {
      local $search = shift;

      if ($search) {
          ####
          # First, you must create a query
          ####
          my $query = "SELECT * FROM $db_table WHERE name='$search'";
          ####
          # Next, you must prepare the query for later use in the form of a statement handle object
          ####
          my $sth = $dbh->prepare($query) || die "Query not prepared";
          ####
          # Next, execute the query.  This query will remain open until the "finish" method is called.  
          # The query is kept open to retrieve multiple tuples of data, specifically for a SELECT statement.
          ####
          $sth->execute || die "Query not executed";
          ####
          # The "rows" method will return the amount of tuples in the table that are affected by the query
          ####
          my $rows = $sth->rows;
          if ($rows > 0) {
              print "there were <font size=5><b>$rows</b></font> rows found in the database<br>";
          }
          my $count = 0; # simply keeps track if there was any data that was printed out to the screen
          ####
          # Creates a table with all of the tuples as rows and each column as the table data
          ####
          my $output = "<table border=1 cellpadding=10><tr>";
          while (my @results = $sth->fetchrow_array) { # retrieves a tuple from the table one row at time
              for (my $i=0; $i<=$#results; $i++) {
                  $output .= "<td>$results[$i]</td>";
                  $count++;
              }
              $output .= "</tr><tr>";
          }
          $output .= "</tr></table><hr>";
          print $output;

          ####
          # Lastly, tell the statement handle object that you are done with it
          ####
          $sth->finish;

          if ($count == 0) {
              print "Sorry, but your query of <font size=5><b>$search</b></font> did not return any results<br>";
          }
      }
  }



