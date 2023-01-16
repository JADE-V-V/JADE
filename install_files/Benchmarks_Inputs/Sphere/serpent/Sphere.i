% --- surface definitions --- %
surf 1 sph 0.0 0.0 0.0 5.0
surf 2 sph 0.0 0.0 0.0 50.0
surf 3 sph 0.0 0.0 0.0 60.0
% --- cell definitions --- %
cell 1 0 void ( -1 ) 
cell 2 0 1 ( 1 -2 ) 
cell 3 0 outside 2  

% --- Tally definitions --- %
det 2 n ds 2 -2 dv 3.14159E+04 de vitJ

det 22 p ds 2 -2 dv 3.14159E+04 de course_gamma

det 32 p ds 2 -2 dv 3.14159E+04 de FISPACT

det 6 n dc 2 dv 1 dr -4 void

det 46 p dc 2 dv 1 dr -26 void

det 12 n ds 2 -2 dv 3.14159E+04 de course_neutron

/* Tallies calling MT numbers in Serpent require a material defined
by a single isotope with number density. To be added at later stage*/

% det 24 n dc 2 dv 1 dr 105 360
% 
% det 214 n dc 2 dv 1 dr 205 370
% 
% det 14 n dc 2 dv 1 dr 207 360
% 
% det 34 n dc 2 dv 1 dr 444 360

ene vitJ 4 nj17
ene FISPACT 1 1e-11 0.01 0.02 0.05 0.10 0.20 0.30 0.40 0.60 0.80 1.00 1.22 1.44 1.66 2.00 2.50
3.00 4.00 5.00 6.50 8.00 10.00 12.00 14.00 20.00
ene course_gamma 1 1e-11 1e-2 1e-1 1 5 20
ene course_neutron 1 1e-11 1e-6 0.1 1 10 20

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
