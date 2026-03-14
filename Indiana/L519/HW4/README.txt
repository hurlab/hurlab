***************************************************************************

 			README for Model.cgi
			   
			                     Oct. 21, 2004
			                     Written by Junguk HUR
			                     windyskyemail-open@yahoo.co.kr
***************************************************************************

0. Web-pages
   http://mypage.iu.edu/~juhur/L519/HW4/Model.html     (BEST)
   http://biokdd.informatics.indiana.edu/~juhur/Model.html   

   * http://mypage.iu.edu/~juhur/L519/HW4/Model.cgi      or
   * http://biokdd.informatics.indiana.edu/cgi-bin/L519/HW4/Model.cgi
	
			                                          
1. Introduction
   This perl CGI script accepts three DNA or protein sequences 
   (either in FASTA format or as simple string of sequence) from the web-page.
   It calculates the LOD for d treating s1(Model1) and s2(Model2) 
   as models like we did in class. The calculation is based upon 
   
     exp( L(Ms1 |d) - L(Ms2 |d))
     
   This script uses find_percent.pl for the probability calulation of
   given model sequences (S1, S2). 
   

2. Running Environment
   Tested on windows XP and UNIX with Perl 5.8.0


3. Features
   A. Input Sequences
      a. All three sequences should be provided by users. 
      b. They must be same type (either all protein ro all DNA sequences)
      c. They may be in FASTA format but it doesn't really matter. If it's
         not in FASTA format, the script will automatically add a temporary
         preamble (description or ID) line for the sequence.
      d. In order to help users understand how it works, this script
         will provide sample DNA sequences, when users click 'SampleSet'
      e. To give some flexibility, numeric characters, spaces are allowed 
         at any position except from the '>' of FASTA (if any)
      
   B. Sequence Check
       a. This script recognizes whether the input sequence is 
          DNA, protein, or errorneous sequences. This is done by
          checking non DNA character and non amino acid character.           
       b. All the three sequence (S1, S2, Data) should be 
          either all protein or all DNA. Otherwise, this script 
          will show an error message. 
   
   C. Result
       a. A result with a table of probabilities and LOD scores.
       
   D. Laplace Correction
      To prevent a probability of character to be Zero(o), the laplace
      correction algorithm has been implemented. Depending on the 
      sequence type, one count will be added to all the characters
      including missing ones. 

4. Clickable Button
   A. Submit Query : Begin to calculate the LOD of data sequence
   B. Clear        : Erase all the input
   C. SampleSeq    : Show sample sequences entered into the textarea
   

5. Links
   A. README.txt : Link to this readme file
   B. L519 : Junguk's homepage for L519
             L519 Bioinformatics : Theory and Application
   C. Email : Send an email to me.
              For a security reason and to prevent spams,
              the email address used here is not IU account
   
          
6. Exception(Error)
   A. when any input sequence was missing.
   B. when any sequence has a errorneous sequences
   C. when the types of three sequences do not match
      (they should be either all protein or all DNA)
   
      
7. Subroutin Package Requirement
   This cgi script uses 'LODSubs.pl', which uses 'commonsubs.pl'

8. Sample Result Description
---------------------------------------------------------------------------
CHAR M(SEQ#1) M(SEQ#2) DATA log(D|M1) log(D|M2) 
---------------------------------------------------------------------------
G 0.132 0.062 62 -125.547 -172.398 
A 0.316 0.423 72 -82.945 -61.948 
C 0.114 0.092 39 -84.691 -93.053 
T 0.438 0.423 95 -78.426 -81.736 
---------------------------------------------------------------------------
TOTAL 1.000 1.000 268 -371.609 -409.135 
---------------------------------------------------------------------------
log(D|M1)-log(D|M2)=37.526 
---------------------------------------------------------------------------
exp(log(D|M1)-log(D|M2))=1.984e+16 
---------------------------------------------------------------------------

M(SEQ#1) : Character frequency for Model 1
M(SEQ#2) : Character frequency for Model 2
DATA     : Character count of Data
log(D|M1): log of probability of given sequence at Model1
log(D|M1): log of probability of given sequence at Model2
