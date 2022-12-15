% --- surface definitions --- %
surf 1 cylx 0.0 0.0 2.55 
surf 2 cylx 0.0 0.0 2.85 
surf 5 sph 0.0 0.0 0.0 30.0
surf 6 sph 0.0 0.0 0.0 30.5
surf 7 sph 0.0 0.0 0.0 100.0
surf 8 px -2.2
surf 9 px -2.5
% --- cell definitions --- %
cell 1 0 void ( ( 8 -1 -6 ) ) 
cell 2 0 2 ( ( -8 9 -2 ) : ( 8 1 -2 -5 ) ) 
cell 3 0 1 ( ( -5 -9 ) : ( 9 2 -5 ) ) 
cell 4 0 2 ( ( 5 -6 -8 ) : ( 8 1 5 -6 ) ) 
cell 5 0 void ( 6 -7 ) 
cell 6 0 void ( 7 ) 
% --- material definitions --- %
% M1
mat 1 -4.36894 rgb 0 208 31
25055 9.997710e-01 
6012 2.265206e-04 
6013 2.449985e-06 
% M2
mat 2 -7.824 rgb 0 0 255
24050 -1.000000e+00 
