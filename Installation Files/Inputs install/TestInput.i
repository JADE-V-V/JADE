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
m10
      1001    1.0  $ Pb-206 AB(%) 100.0 $ Bla bla bla
C
m5    $ Here comment
C     Comment here again
      1001    -1.0  $ Pb-206 AB(%) 100.0
m3
      1001.70c    1.0  $ Pb-206 AB(%) 100.0
C
C ***********************************
C *  WATER
C *  MASS DENSITY [G/CC] - 0.946
C *  VOLUME FRACTION [%] - 100
C ***********************************
C
C
M1
      1001.21c    -0.25  $ Pb-206 AB(%) 100.0
      1002    -0.25  $ Pb-206 AB(%) 100.0
      8016    -0.25  $ Pb-206 AB(%) 100.0
      8017    -0.25  $ Pb-206 AB(%) 100.0
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
      1001.21c    -1  $ Pb-206 AB(%) 100.0
      1002.70c    -2  $ Pb-206 AB(%) 100.0
      16000    -1  $ Pb-206 AB(%) 100.0
      17000    -1  $ Pb-206 AB(%) 100.0
C
      8016    -1  $ Pb-206 AB(%) 100.0
      8017    -0.5  $ Pb-206 AB(%) 100.0
	  8017 -1
m4
      1001    1.0  $ Pb-206 AB(%) 100.0
      1002    1.0  $ Pb-206 AB(%) 100.0
       nlib=.66c hlib=.24h
C
C
      8016.80c    1.0  $ Pb-206 AB(%) 100.0
      8016.21c    1.0  $ Pb-206 AB(%) 100.0
      8016.31c    1.0  $ Pb-206 AB(%) 100.0
      8016    1.0  $ Pb-206 AB(%) 100.0
      6012.21c    5.0  $ Pb-206 AB(%) 100.0
       nlib=.66c hlib=.24h
m11
      8016    1.0  $ Pb-206 AB(%) 100.0
      82206    10.0  $ Pb-206 AB(%) 100.0
mx10:n j 26056.70h
C mx10
m14   8016    1.0  $ Pb-206 AB(%) 100.0
      8016    1.0  $ Pb-206 AB(%) 100.0
C
SDEF POS 0 0 0 PAR=N ERG=d1 $ position, particle type, energy
SI1 H 1e-6 0.1 1 10 14      $ histogram boundaries
SP1 D 0    1   1 1  1       $ probabilities for each bin
C
PRDMP  2J  -1 $ Flag to print the mctal
C
nps 1e6
