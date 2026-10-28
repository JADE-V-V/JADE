% --- Dummy Serpent benchmark used for JADE tests ---
include "geom.txt"

/* materials: the comment
   must survive */
mat steel -7.93 rgb 100 100 100
    26000.31c   -0.70   % natural iron
    24052.31c   -0.18
    28058.31c   -0.12
mat 2 -1.0 moder lwtr 1001
    1001.31c 2 8016.31c 1
therm lwtr lwj3.11t

det 4 n dc 10 dc 20 de egrid
ene egrid 1 1e-11 1 20

src point n sp 0 0 0 se 14

set acelib "/old/library.xsdata"
set nps 50
