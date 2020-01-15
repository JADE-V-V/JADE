MCNP XS LEAK SPHERE TEST INPUT
1  1 -1 -1          IMP:N=1
2  2 -1 -2          IMP:N=1
3  3 -1 -3          IMP:N=1
4  4 -1 -4          IMP:N=1
5  5 -1 -5          IMP:N=1
6  0 #1 #2 #3 #4 #5 IMP:N=0

1 S 0  0 0 5
2 S 10 0 0 5
3 S 20 0 0 5
4 S 30 0 0 5
5 S 40 0 0 5
C

C
m10 1001 1
C
SDEF POS 0 0 0 PAR=N ERG=d1 $ position, particle type, energy
SI1 H 1e-6 0.1 1 10 14      $ histogram boundaries
SP1 D 0    1   1 1  1       $ probabilities for each bin
C
PRDMP  2J  -1 $ Flag to print the mctal
C
m5 1001 -1
m3 1001.70c 1 $ Comment here
C
nps 1e6
C
C ***********************************
C *  WATER
C *  MASS DENSITY [G/CC] - 0.946
C *  VOLUME FRACTION [%] - 100
C ***********************************
C
C
M1       1001.21c   -6.33910e-002 $H   1 AMOUNT(%)  2.0000 AB(%) 99.99
         1002   -7.29080e-006 $H   2 AMOUNT(%)  2.0000 AB(%)  0.01
         8016   -3.15453e-002 $O  16 weight(%)     N/A ab(%) 99.76
         8017   -1.20164e-005  
C *
C *  T.A.D. = 9.50204E-002
C *  EFF.DENSITY = 9.46000E-001
C
C ***********************************
C *  WATER
C *  MASS DENSITY [G/CC] - 0.946
C *  VOLUME FRACTION [%] - 100
C ***********************************
C
C
M2      
C
         1001.21c   -6.33910e-002 $H   1 AMOUNT(%)  2.0000 AB(%) 99.99
         1002.70c   -7.29080e-006 $H   2 AMOUNT(%)  2.0000 AB(%)  0.01
		 16000      -8.2
		 17000      -10
		 18055		-10 $This will be ignored, it does not exist
C
         8016   -3.15453e-002   $O  16 weight(%)     N/A ab(%) 99.76
         8017   -1.20164e-005 $O  17 weight(%)     N/A ab(%)  0.04
m4    1001 1 1002  1 nlib=.66c hlib=.24h $ Comment_No.1
C
      8016.80c     1  $ Comment_No.2
      8016.21c     1  $ Comment_No.3
      8016.31c     1  $ Comment_No.4
      8016     1      $ Comment_No.5
      6012.21c 1      $ Comment_No.6
      6012.21c 1 6012.21c 1 6012.21c 1 6012.21c 1  $ Comment_No.7
	  nlib=.66c hlib=.24h
m1  8016 1.0
     82206 10.0
mx1:h j 26056.70h
mx1:n j 88223.70c
mx1:p j 94239.70u
      
