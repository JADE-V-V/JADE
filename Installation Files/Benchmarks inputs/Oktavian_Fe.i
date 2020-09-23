OKTAVIAN IRON EXPERIMENT: routine MCNP5(X) analysis
C  2-D MODEL, ENDF/B-VII
c  Author: Alberto Milocco, IJS, Alberto.Milocco@ijs.si
c
c  sphere cavity
1  0              -1
c  beam duct
2  0               1 -2 -3 -4
c  monitor duct
3  0               1 -2 -5 -6 #2
c  iron sample
4  1  8.5369e-2   -2 #1 #2 #3
c  precollimator
5  0               2 -7
c  collimator
6  0              -8
c  athmosphere
7  0               2 7 8

c  shell surfaces
1  so  4
2  so  50.32
3  cy  4
4  py  0
5  cx  2
6  px  0
c  collimator bottleneck
7  trc  0 0    0   0 400.     0  25.6886  11.9602
8  trc  0 400. 0   0 538.581  0  11.9602  6.351

c  problem type
mode n
PRDMP  2J  -1 $ Flag to print the mctal
c  variance reduction
imp:n 1 1 1 2 2 2 0
c  source specification
sdef  sur 4  pos 0 0 0  rad d1  vec 0 1 0  dir d2  erg fdir d3
si1  0 0.3
sp1  -21 1
si2  a  -1.0000 -0.9962 -0.9848 -0.9659 -0.9397 -0.9063 -0.8660 -0.8192 &
        -0.7660 -0.7071 -0.6428 -0.5736 -0.5000 -0.4226 -0.3420 -0.2588 &
        -0.1737 -0.0872  0.0000  0.0872  0.1737  0.2588  0.3420  0.4226 &
         0.5000  0.5736  0.6428  0.7071  0.7660  0.8192  0.8660  0.9063 &
         0.9397  0.9659  0.9848  0.9962  1.0000
sp2      0.8700  0.8700  0.8700  0.8700  0.8700  0.8800  0.8800  0.9000 &
         0.9000  0.8600  0.8600  0.8300  0.8300  0.8400  0.8400  0.8300 &
         0.8300  0.8200  0.8200  0.8700  0.8700  0.9000  0.9000  0.9600 &
         0.9600  0.9750  0.9750  0.9800  0.9800  0.9850  0.9850  0.9900 &
         0.9900  1.0000  1.0000  1.0000  1.0000
ds3      13.36   13.365  13.37   13.385  13.4    13.425  13.45   13.49 &
         13.53   13.58   13.62   13.67   13.71   13.8    13.88   13.92 &
         13.97   14.04   14.1    14.165  14.23   14.32   14.4    14.44 &
         14.48   14.54   14.6    14.65   14.7    14.74   14.78   14.81 &
         14.84   14.86  14.88    14.885  14.89
c  tally specifiction
fc5  point detector time domain
f5:n  0 936.04 0 0
t5  0  10  12  99i  20  159i  100  119i  220  249i 720
fc15 point detector energy domain
f15:n  0 936.04 0 0
e15  0.001 9i 0.01 9i 0.02 9i 0.04 29i 0.1 39i 0.5 24i 1 79i 5 49i 10 79i 18
c  material specification
m1     6012.    6.23002E-04
       6013.    6.73822E-06
C      6000.    6.2974E-04
      14028.    3.5705E-04
      14029.    1.8130E-05
      14030.    1.1951E-05
      15031.    3.0524E-05
      16032.    1.3995E-05
      16033.    1.1205E-07
      16034.    6.3246E-07
      16036.    2.9486E-09
      25055.    7.6582E-04
      26054.    4.8830E-03
      26056.    7.6652E-02
      26057.    1.7702E-03
      26058.    2.3559E-04
c  problem cutoff
c nps  100e6
c  peripheral cards
c prdmp  10000000 10000000 j j 10000000
c dbcn  j 10000000 1 10 j j j j j j 1 j j j j 1 j j
print
