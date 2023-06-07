% --- surface definitions --- %
surf 1 cylx 0.0 0.0 5.55 
surf 2 cylx 0.0 0.0 5.75 
surf 3 sph 0.0 0.0 0.0 10.0
surf 4 sph 0.0 0.0 0.0 10.2
surf 5 sph 0.0 0.0 0.0 19.75
surf 6 sph 0.0 0.0 0.0 19.95
surf 7 sph 0.0 0.0 0.0 100.0
surf 8 px 8.32
% --- cell definitions --- %
cell 1 0 void ( ( -3 -8 ) : ( 8 -1 -6 ) ) 
cell 2 0 2 ( ( 3 -4 -8 ) : ( 8 1 -2 -6 ) ) 
cell 3 0 1 ( ( 4 -5 -8 ) : ( 8 2 -5 ) ) 
cell 4 0 2 ( ( 5 -6 -8 ) : ( 8 2 5 -6 ) ) 
cell 5 0 void ( 6 -7 ) 
cell 6 0 void ( 7 ) 
% --- material definitions --- %
% M1
mat 1 -1.223 rgb 0 208 31
13027 1.000000e+00 
% M2
mat 2 -7.824 rgb 0 0 255
24050 -1.000000e+00 
