% --- surface definitions --- %
surf 1 sph 0.0 0.0 0.0 5.0
surf 2 sph 0.0 0.0 0.0 50.0
surf 3 sph 0.0 0.0 0.0 60.0
% --- cell definitions --- %
cell 1 0 void ( -1 ) 
cell 2 0 1 ( 1 -2 ) 
cell 3 0 outside 2  

% --- Tally definitions --- %
det 4 n dc 2 dv 1 de vitJ

det 14 p dc 2 dv 1 de 24_group

ene vitJ 4 nj17
ene 24_group 1 1e-11 0.01 0.02 0.05 0.10 0.20 0.30 0.40 0.60 0.80 1.00 1.22 1.44 1.66 2.00 2.50
3.00 4.00 5.00 6.50 8.00 10.00 12.00 14.00 20.00

% --- Source definition --- %
/* Note that Serpent reads probability over each histogram while MCNP calculates
the integral i.e. probability*bin_width. Note that there is a bug in Serpent 
v2.1.32 for sampling 1D tabular source definitions (https://ttuki.vtt.fi/A33Mpg0ryEvxnGVE572g/viewtopic.php?f=25&t=3682&start=40#p13388)*/
src point n sp 0 0 0
sb 5 1
1e-6 0
0.1 10
1 1.111
10 0.111
14 0.25

% --- Data cards -- %

set gcu -1
set bala 1
set ngamma 2
set bc 1
set nbuf 1000
set gbuf 10000
set srcrate 1
