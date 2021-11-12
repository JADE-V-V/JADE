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

C Header M1
M1
C M1-submat1
      1001.21c    0.5
	  1002.21c    0.5
C M1-Submat 2
	  2004.21c    -1
	  8016        -3
	  1001        -0.5
C Header M2
M2    8016    1
C M2-submat1
C second line
      9019    1
M102    8016    1    1002.21c   1
      1002.21c   1    1002.21c   1
      9019    1
	  plib=84p